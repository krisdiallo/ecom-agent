#!/usr/bin/env python3
"""
AI-visibility survey of real ecommerce stores.

Mirrors the logic in site/ai-visibility.html exactly, so published numbers and the
public tool cannot disagree. Read-only: fetches robots.txt, the public /products.json
that Shopify exposes, and one product page per store. Polite delays, honest UA.

Usage: python3 research/scan.py stores.txt out.json
"""
import json, re, sys, time, random, urllib.request, urllib.error, gzip, io
from html import unescape


def norm_ws(s):
    return re.sub(r"\s+", " ", s).strip()


def fold(s):
    """Lowercase, decode entities, unify quote characters, drop punctuation noise."""
    s = unescape(s or "").lower()
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return norm_ws(s)

UA = ("Mozilla/5.0 (compatible; ecom-agent-research/1.0; "
      "+https://github.com/krisdiallo/ecom-agent) AI-visibility survey")

SEARCH_BOTS = ["OAI-SearchBot", "PerplexityBot", "Claude-SearchBot", "Claude-User"]
TRAIN_BOTS  = ["GPTBot", "ClaudeBot", "Google-Extended", "CCBot",
               "Bytespider", "Amazonbot", "Applebot-Extended", "meta-externalagent"]


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "*/*",
        "Accept-Encoding": "gzip",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
            return r.status, r.geturl(), raw.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        # A 403 to a research UA is itself informative: keep the code, not just "error".
        return e.code, url, ""


# ---- robots.txt parsing: identical semantics to the browser tool ----
def parse_robots(txt):
    groups, current, last_was_ua = {}, [], False
    for line in txt.splitlines():
        clean = re.sub(r"#.*$", "", line).strip()
        if not clean or ":" not in clean:
            continue
        field, value = clean.split(":", 1)
        field, value = field.strip().lower(), value.strip()
        if field == "user-agent":
            if not last_was_ua:
                current = []
            ua = value.lower()
            current.append(ua)
            groups.setdefault(ua, {"dis": [], "allow": []})
            last_was_ua = True
        else:
            last_was_ua = False
            if field in ("disallow", "allow"):
                key = "dis" if field == "disallow" else "allow"
                for ua in current:
                    groups.setdefault(ua, {"dis": [], "allow": []})[key].append(value)
    return groups


def path_risk(d):
    if not d:
        return "none"
    if d == "/" or re.fullmatch(r"/\*+", d):
        return "full"
    s = d.lower()
    if re.search(r"[?=&]|%2b|%3d|\+|sort_by|filter|preview_|oseid|\.js$|-remote$|-loop$", s):
        return "benign"
    if re.match(r"^/(admin|cart|carts|checkout|checkouts|orders|account|search|policies|"
                r"a/downloads|apple-app-site-association|\.well-known|cdn|recommendations|\d+/)", s):
        return "benign"
    if re.fullmatch(r"/\*?/?(products|collections|blogs|pages)/?\*?", s):
        return "catalog"
    return "other"


def group_for(groups, token):
    k = token.lower()
    if k in groups:
        return groups[k], token
    if "*" in groups:
        return groups["*"], "*"
    return None, None


def verdict(g):
    if not g:
        return "none"
    allow_root = any(a in ("/", "/*") for a in g["allow"])
    if any(path_risk(d) == "full" for d in g["dis"]) and not allow_root:
        return "blocked"
    if any(path_risk(d) == "catalog" for d in g["dis"]):
        return "risky"
    return "allowed"


# ---- product page analysis ----
def walk(n, out, d=0):
    if d > 8 or n is None:
        return
    if isinstance(n, list):
        for x in n:
            walk(x, out, d + 1)
    elif isinstance(n, dict):
        out.append(n)
        for v in n.values():
            if isinstance(v, (dict, list)):
                walk(v, out, d + 1)


def type_of(n):
    t = n.get("@type")
    if not t:
        return ""
    return ",".join(t) if isinstance(t, list) else str(t)


def analyse_product(html, name=None, price=None):
    res = {}
    blocks = re.findall(
        r"<script[^>]*type\s*=\s*[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
        html, re.S | re.I)
    res["jsonld_blocks"] = len(blocks)
    nodes, malformed = [], 0
    for b in blocks:
        try:
            walk(json.loads(b.strip()), nodes)
        except Exception:
            malformed += 1
    res["jsonld_malformed"] = malformed
    cands = [n for n in nodes if re.search(r"\bProduct(Group)?\b", type_of(n))]
    prod = next((n for n in cands if n.get("offers")), cands[0] if cands else None)
    res["has_product_schema"] = bool(prod)
    res["is_product_group"] = bool(prod and "ProductGroup" in type_of(prod))

    if prod:
        off = prod.get("offers")
        if isinstance(off, list):
            off = off[0] if off else None
        res["has_offers"] = bool(off)
        if isinstance(off, dict):
            res["offer_price"] = off.get("price") not in (None, "")
            res["offer_currency"] = off.get("priceCurrency") not in (None, "")
            res["offer_availability"] = off.get("availability") not in (None, "")
        res["has_brand"] = prod.get("brand") not in (None, "")
        res["has_rating"] = prod.get("aggregateRating") not in (None, "")
        res["has_sku"] = any(prod.get(k) not in (None, "") for k in ("sku", "gtin", "gtin13", "mpn"))
        res["has_description"] = prod.get("description") not in (None, "")

    body = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    body = re.sub(r"<style[\s\S]*?</style>", " ", body, flags=re.I)
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).strip()
    res["words"] = len(text.split())
    if name:
        # Fold both sides: an early run reported Allbirds' product name as "missing"
        # purely because products.json uses a curly apostrophe and the page uses &#39;.
        res["name_in_raw_html"] = fold(name) in fold(text)
        res["product_name"] = name[:120]
    if price:
        digits = re.sub(r"[^0-9.]", "", str(price))
        res["price_in_raw_html"] = bool(digits) and digits in text
    nums = re.findall(r"\b\d+(?:\.\d+)?\s?(?:mm|cm|m|in|inch|inches|ft|kg|g|lb|lbs|oz|ml|l|"
                      r"w|watt|v|hz|mah|gsm|denier|thread|count|year|yr|month|day|hour|hr|min|"
                      r"pack|piece|pcs|%)\b", text, re.I)
    res["measurements"] = len(set(n.strip().lower() for n in nums))
    res["has_canonical"] = bool(re.search(r"<link[^>]+rel=[\"']canonical[\"']", html, re.I))
    t = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    title = norm_ws(unescape(t.group(1))) if t else ""
    res["has_title"] = bool(title)
    res["title"] = title[:160]
    og = re.search(r"<meta[^>]+property=[\"']og:title[\"'][^>]+content=[\"']([^\"']+)", html, re.I)
    ogt = norm_ws(unescape(og.group(1))) if og else None
    res["og_title"] = ogt[:160] if ogt else None
    # Discovered from real data (Brooklinen, 2026-08-28): a page can serve a <title>
    # for an entirely different product while og:title and canonical are correct.
    #
    # Compare <title> against og:title, NOT against the products.json name. An earlier
    # version compared to the internal name and produced 3 false positives out of 4:
    # merchants legitimately use a different internal name ("tote-bag-with-zipper")
    # from the display title ("The Lightweight Zipper Tote"), and that is not a defect.
    # title vs og:title is the defensible signal because both are on-page claims about
    # the same product, so disagreement is genuinely self-contradictory.
    if title and ogt:
        nt, no = fold(title), fold(ogt)
        head = lambda s: fold(re.split(r"[|–—]", s)[0])
        res["title_og_consistent"] = bool(
            nt and no and (nt in no or no in nt
                           or head(title) in no or head(ogt) in nt))
    # structured data present only as a JS-injected string is invisible to non-JS crawlers
    res["jsonld_js_injected"] = (res["jsonld_blocks"] == 0
                                 and "application/ld+json" in html)
    return res


def scan(host):
    out = {"host": host}
    # robots.txt
    try:
        st, final, txt = get(f"https://{host}/robots.txt")
        out["robots_status"] = st
        if "<html" in txt[:400].lower():
            out["robots_is_html"] = True
        else:
            groups = parse_robots(txt)
            out["robots_rules"] = sum(len(v["dis"]) for v in groups.values())
            out["is_shopify_robots"] = "preview_theme_id" in txt or "/a/downloads/-/" in txt
            out["search_blocked"] = [b for b in SEARCH_BOTS
                                     if verdict(group_for(groups, b)[0]) == "blocked"]
            out["search_risky"] = [b for b in SEARCH_BOTS
                                   if verdict(group_for(groups, b)[0]) == "risky"]
            out["train_blocked"] = [b for b in TRAIN_BOTS
                                    if verdict(group_for(groups, b)[0]) == "blocked"]
            out["star_blocks_all"] = verdict(groups.get("*")) == "blocked"
            out["has_explicit_ai_rules"] = any(
                b.lower() in groups for b in SEARCH_BOTS + TRAIN_BOTS)
    except Exception as e:
        out["robots_error"] = f"{type(e).__name__}"

    # find one real product: products.json first, sitemap as fallback (some stores
    # disable the JSON endpoint but still publish a product sitemap)
    handle = title = price = None
    try:
        st, final, js = get(f"https://{host}/products.json?limit=3")
        out["products_json_status"] = st
        if js:
            prods = json.loads(js).get("products", [])
            out["products_json"] = len(prods)
            if prods:
                p = prods[0]
                handle, title = p.get("handle"), p.get("title")
                price = (p.get("variants") or [{}])[0].get("price")
    except Exception as e:
        out["products_json_error"] = type(e).__name__

    if not handle:
        try:
            for sm in ("sitemap_products_1.xml?from=1&to=999999999", "sitemap.xml"):
                st, final, xml = get(f"https://{host}/{sm}")
                m = re.findall(r"<loc>\s*([^<]*?/products/[^<\s]+?)\s*</loc>", xml)
                if m:
                    out["product_via"] = "sitemap"
                    url = m[0]
                    handle = url.rstrip("/").split("/products/")[-1].split("?")[0]
                    break
        except Exception as e:
            out["sitemap_error"] = type(e).__name__

    if handle:
        try:
            st2, final2, html = get(f"https://{host}/products/{handle}")
            out["product_status"] = st2
            out["product_url"] = final2
            out["product_bytes"] = len(html)
            if html and "/products/" in final2:
                out.update(analyse_product(html, title, price))
            elif html:
                out["product_redirected_away"] = True
        except Exception as e:
            out["product_error"] = type(e).__name__
    else:
        out["product_error"] = "no_product_url_found"
    return out


if __name__ == "__main__":
    hosts = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
    results = []
    for i, h in enumerate(hosts, 1):
        r = scan(h)
        results.append(r)
        flag = ""
        if r.get("search_blocked"):
            flag = "  <-- BLOCKS SEARCH BOTS: " + ",".join(r["search_blocked"])
        elif r.get("has_product_schema") is False:
            flag = "  <-- no Product schema"
        print(f"[{i}/{len(hosts)}] {h:<32} "
              f"shopify={r.get('is_shopify_robots')} "
              f"schema={r.get('has_product_schema')} "
              f"words={r.get('words')}{flag}", flush=True)
        json.dump(results, open(sys.argv[2], "w"), indent=1)
        # Be a polite guest: several hosts returned 429 at 1.5s. Back off and jitter.
        time.sleep(random.uniform(4.0, 7.0))
    print(f"\nwrote {len(results)} -> {sys.argv[2]}")
