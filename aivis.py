#!/usr/bin/env python3
"""
aivis — check whether AI assistants can actually read your store.

    python3 aivis.py yourstore.com

No dependencies. No account. Nothing is uploaded — it fetches your public pages
directly and prints the result.

What it checks
  1. robots.txt, separating the crawlers that RECOMMEND you (OAI-SearchBot,
     PerplexityBot, Claude-SearchBot, Claude-User) from the ones that only TRAIN
     on you (GPTBot, ClaudeBot, Google-Extended, CCBot). Blocking the first group
     removes you from AI answers. Blocking the second costs you nothing. Most
     advice conflates them; every token here was read from the vendor's own docs.
  2. A product page's RAW HTML — not the rendered DOM — because most AI crawlers
     do not run JavaScript. Structured data, offer completeness, whether your
     facts survive, and how many concrete measurements you actually give.

Why raw HTML matters: if your JSON-LD is injected by JavaScript it will look
perfect in dev tools and in any tester that runs JS, while being completely
absent from what an assistant receives.

MIT licensed. Source and the 70-store study it came from:
https://github.com/krisdiallo/ecom-agent
"""
import argparse, gzip, io, json, re, sys, urllib.error, urllib.request
from html import unescape

__version__ = "1.0.0"

UA = ("Mozilla/5.0 (compatible; aivis/%s; +https://github.com/krisdiallo/ecom-agent) "
      "AI-visibility self-check" % __version__)

SEARCH_BOTS = [
    ("OAI-SearchBot", "ChatGPT search results"),
    ("PerplexityBot", "Perplexity results"),
    ("Claude-SearchBot", "Claude search quality"),
    ("Claude-User", "Claude user-initiated retrieval"),
    ("Amzn-SearchBot", "Alexa / Amazon search experiences"),
    ("Amzn-User", "Alexa live query fetches"),
    ("Applebot", "Spotlight, Siri, Safari"),
]
TRAIN_BOTS = [
    ("GPTBot", "OpenAI training"), ("ClaudeBot", "Anthropic training"),
    ("Google-Extended", "Gemini training/grounding"), ("CCBot", "Common Crawl"),
    ("Bytespider", "ByteDance"), ("Amazonbot", "Amazon"),
    ("Applebot-Extended", "Apple training opt-out"), ("meta-externalagent", "Meta"),
]

C = {"r": "\033[31m", "y": "\033[33m", "g": "\033[32m", "b": "\033[1m",
     "d": "\033[2m", "x": "\033[0m"}


def paint(on):
    if not on:
        for k in C:
            C[k] = ""


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def fold(s):
    s = unescape(s or "").lower().replace("’", "'").replace("‘", "'")
    return norm(re.sub(r"[^a-z0-9]+", " ", s))


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
            return r.status, r.geturl(), raw.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception:
        return 0, url, ""


# ---------- robots.txt ----------
def parse_robots(txt):
    groups, cur, last_ua = {}, [], False
    for line in txt.splitlines():
        clean = re.sub(r"#.*$", "", line).strip()
        if not clean or ":" not in clean:
            continue
        field, value = clean.split(":", 1)
        field, value = field.strip().lower(), value.strip()
        if field == "user-agent":
            if not last_ua:
                cur = []
            cur.append(value.lower())
            groups.setdefault(value.lower(), {"dis": [], "allow": []})
            last_ua = True
        else:
            last_ua = False
            if field in ("disallow", "allow"):
                k = "dis" if field == "disallow" else "allow"
                for ua in cur:
                    groups.setdefault(ua, {"dis": [], "allow": []})[k].append(value)
    return groups


def path_risk(d):
    """Shopify's default file blocks ~45 paths, all of them faceted-nav params,
    checkout and admin. Warning about those would fire on nearly every store."""
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
    """A crawler obeys ONLY its own group when it has one, ignoring User-agent: *."""
    k = token.lower()
    if k in groups:
        return groups[k]
    return groups.get("*")


def verdict(g):
    if not g:
        return "none"
    if any(a in ("/", "/*") for a in g["allow"]):
        return "allowed"
    if any(path_risk(d) == "full" for d in g["dis"]):
        return "blocked"
    if any(path_risk(d) == "catalog" for d in g["dis"]):
        return "risky"
    return "allowed"


# ---------- product page ----------
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
    return ",".join(t) if isinstance(t, list) else str(t or "")


def analyse(html):
    r = {}
    blocks = re.findall(
        r"<script[^>]*type\s*=\s*[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
        html, re.S | re.I)
    nodes, bad_json = [], 0
    for b in blocks:
        try:
            walk(json.loads(b.strip()), nodes)
        except Exception:
            bad_json += 1
    r["blocks"], r["bad_json"] = len(blocks), bad_json
    r["js_injected"] = (not blocks) and bool(re.search(r"application/ld\+json", html))
    cands = [n for n in nodes if re.search(r"\bProduct(Group)?\b", type_of(n))]
    p = next((n for n in cands if n.get("offers")), cands[0] if cands else None)
    r["product"] = p
    r["is_group"] = bool(p and "ProductGroup" in type_of(p))
    if p:
        off = p.get("offers")
        if isinstance(off, list):
            off = off[0] if off else None
        r["offers"] = off if isinstance(off, dict) else None
        r["fields"] = {k: (p.get(k) not in (None, "")) for k in
                       ("name", "image", "description", "brand", "aggregateRating")}
        r["fields"]["sku"] = any(p.get(k) not in (None, "")
                                 for k in ("sku", "gtin", "gtin13", "mpn"))
    body = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    body = re.sub(r"<style[\s\S]*?</style>", " ", body, flags=re.I)
    text = norm(re.sub(r"<[^>]+>", " ", body))
    r["text"], r["words"] = text, len(text.split())
    nums = re.findall(r"\b\d+(?:\.\d+)?\s?(?:mm|cm|m|in|inch|inches|ft|kg|g|lb|lbs|oz|ml|l|"
                      r"w|watt|v|hz|mah|gsm|denier|thread|count|year|yr|month|day|hour|hr|"
                      r"min|pack|piece|pcs|%)\b", text, re.I)
    r["meas"] = sorted({n.strip().lower() for n in nums})
    t = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    r["title"] = norm(unescape(t.group(1))) if t else ""
    og = re.search(r"<meta[^>]+property=[\"']og:title[\"'][^>]+content=[\"']([^\"']+)",
                   html, re.I)
    r["og"] = norm(unescape(og.group(1))) if og else ""
    r["canonical"] = bool(re.search(r"<link[^>]+rel=[\"']canonical[\"']", html, re.I))
    return r


STOP = {"the", "a", "an", "for", "and", "with", "in", "of", "to", "by", "on", "oz",
        "ml", "g", "kg", "pack", "set", "size", "new", "our"}


def toks(s):
    return {w for w in fold(s).split() if len(w) > 1 and w not in STOP}


def titles_agree(t, o):
    """Token overlap, not substring: a title carrying a bracketed suffix with a '|'
    is not a contradiction, and substring matching called that a failure."""
    a, b = toks(t), toks(o)
    if not a or not b:
        return None
    return len(a & b) / min(len(a), len(b)) >= 0.5


# ---------- report ----------
class R:
    def __init__(self, quiet=False):
        self.bad = self.warn = self.ok = 0
        self.quiet = quiet
        self.findings = []

    def f(self, lvl, title, body=""):
        col = {"bad": C["r"], "warn": C["y"], "ok": C["g"]}[lvl]
        mark = {"bad": "FAIL", "warn": "WARN", "ok": " OK "}[lvl]
        setattr(self, lvl, getattr(self, lvl) + 1)
        self.findings.append({"level": lvl, "title": title, "detail": norm(body)})
        if self.quiet:
            return
        print(f"  {col}[{mark}]{C['x']} {C['b']}{title}{C['x']}")
        for line in body.split("\n") if body else []:
            if line.strip():
                print(f"         {C['d']}{line.strip()}{C['x']}")

    def note(self, title, body=""):
        self.findings.append({"level": "note", "title": title, "detail": norm(body)})
        if self.quiet:
            return
        print(f"  {C['d']}[note]{C['x']} {title}")
        for line in body.split("\n") if body else []:
            if line.strip():
                print(f"         {C['d']}{line.strip()}{C['x']}")


def check_robots(host, rep):
    say = (lambda *a, **k: None) if rep.quiet else print
    say(f"\n{C['b']}1. robots.txt — are you blocking the crawlers that recommend you?{C['x']}")
    st, _, txt = get(f"https://{host}/robots.txt")
    if st != 200 or not txt:
        if st in (403, 429):
            rep.note(f"robots.txt returned HTTP {st}",
                     "A firewall refused us. That may also affect AI crawlers, in a way "
                     "robots.txt cannot show. Worth checking your WAF's bot rules.")
        elif st == 404:
            rep.f("ok", "No robots.txt at all",
                  "With no file, everything is allowed by default. Nothing is blocked.")
        else:
            rep.note(f"Could not read robots.txt (HTTP {st or 'no response'})")
        return
    if re.search(r"<html|<!doctype", txt[:400], re.I):
        rep.f("warn", "robots.txt returned an HTML page",
              "Your server served a normal page instead of a plain-text file.")
        return

    g = parse_robots(txt)
    blocked = [(t, w) for t, w in SEARCH_BOTS if verdict(group_for(g, t)) == "blocked"]
    risky = [(t, w) for t, w in SEARCH_BOTS if verdict(group_for(g, t)) == "risky"]
    fine = [(t, w) for t, w in SEARCH_BOTS if verdict(group_for(g, t)) == "allowed"]

    if blocked:
        rep.f("bad", f"Blocking {len(blocked)} crawler(s) that decide if you appear in AI answers",
              "\n".join(f"{t} — {w}" for t, w in blocked) +
              "\nRemove the Disallow: / for these tokens, or give each an explicit allow group.")
    if risky:
        rep.f("warn", f"{len(risky)} search crawler(s) blocked from catalog paths",
              "\n".join(t for t, _ in risky) +
              "\nThese rules cover product/collection paths — the pages you want quoted.")
    if fine:
        rep.f("ok", f"{len(fine)} search crawler(s) can read your catalog",
              " ".join(t for t, _ in fine) +
              "\nFloor cleared — necessary, not sufficient.")

    tb = [(t, w) for t, w in TRAIN_BOTS if verdict(group_for(g, t)) == "blocked"]
    if tb:
        rep.note(f"Blocking {len(tb)} training crawler(s) — not a problem",
                 " ".join(t for t, _ in tb) +
                 "\nThese feed model training, not live recommendations. Opting out is a "
                 "legitimate choice with no cost to your AI visibility.")
    if verdict(g.get("*")) == "blocked":
        rep.f("bad", "User-agent: * disallows everything",
              "This blocks every crawler without its own group, search engines included.")


PROD_PAT = re.compile(r"/(products?|shop|item|p|dp|collections/[^/]+/products)/[^/\s<]+", re.I)


def find_product_via_sitemap(host, budget=6):
    """Walk sitemaps (including sitemap indexes) looking for something product-shaped.
    Platform-agnostic on purpose: Shopify is only ~3 in 4 of the stores we sampled."""
    seen, queue = set(), []
    st, _, robots = get(f"https://{host}/robots.txt")
    queue += re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots or "")
    queue += [f"https://{host}/sitemap.xml", f"https://{host}/sitemap_index.xml",
              f"https://{host}/product-sitemap.xml",
              f"https://{host}/sitemap_products_1.xml?from=1&to=999999999"]
    while queue and budget > 0:
        sm = queue.pop(0)
        if sm in seen:
            continue
        seen.add(sm)
        budget -= 1
        st, _, xml = get(sm, timeout=20)
        if st != 200 or not xml:
            continue
        locs = re.findall(r"<loc>\s*([^<\s]+?)\s*</loc>", xml)
        hits = [u for u in locs if PROD_PAT.search(u)]
        if hits:
            return hits[0]
        # a sitemap index: follow the most product-looking children first
        children = [u for u in locs if u.lower().endswith((".xml", ".xml.gz"))]
        children.sort(key=lambda u: 0 if re.search(r"product|item|shop", u, re.I) else 1)
        queue = children[:4] + queue
    return None


def check_product(host, rep, url=None):
    explicit = bool(url)
    say = (lambda *a, **k: None) if rep.quiet else print
    say(f"\n{C['b']}2. Product page — can a crawler read your facts?{C['x']}")
    if not url:
        st, _, js = get(f"https://{host}/products.json?limit=1")
        handle = None
        if st == 200 and js:
            try:
                ps = json.loads(js).get("products", [])
                if ps:
                    handle = ps[0].get("handle")
            except Exception:
                pass
        if handle:
            url = f"https://{host}/products/{handle}"
        else:
            # Not Shopify (or products.json disabled). Walk sitemaps generically so this
            # works on WooCommerce, BigCommerce and custom carts too — 24% of the hosts
            # in our own 70-store sample were not Shopify.
            url = find_product_via_sitemap(host)
        if not url:
            rep.note("Could not find a product page automatically",
                     "Point it at one directly:\n"
                     f"  python3 aivis.py {host} --url https://{host}/<your-product-page>")
            return

    st, final, html = get(url)
    if (st != 200 or not html) and not explicit:
        # products.json can hand back a handle whose page is gone (stale feed). Fall
        # back to sitemap discovery rather than reporting "could not fetch" and quitting.
        alt = find_product_via_sitemap(host)
        if alt and alt != url:
            url = alt
            st, final, html = get(url)
    if st != 200 or not html:
        rep.note(f"Could not fetch {url} (HTTP {st or 'no response'})",
                 f"Point it at a product page directly:\n"
                 f"  python3 aivis.py {host} --url https://{host}/<your-product-page>")
        return

    # A redirect can land us somewhere that is not the product page at all — Gymshark
    # sends /products/<handle> to a checkout subdomain, which is a JS shell with no
    # title. Reporting "3 critical" against that would tell a merchant their store is
    # broken when it is not. Refuse to grade a page we were redirected away to.
    want = re.sub(r"^www\.", "", host).lower()
    got = re.sub(r"^www\.", "", re.sub(r"^https?://", "", final).split("/")[0]).lower()
    if got != want and not got.endswith("." + want) or "checkout." in got:
        rep.note(f"Redirected to {got} — not grading this page",
                 f"{url}\n  -> {final}\n"
                 "That is a different host (often a checkout or regional domain), so it is "
                 "not your product page and any result would be misleading. Re-run against a "
                 "real product URL:\n"
                 f"  python3 aivis.py {host} --url https://{host}/products/<handle>")
        return

    say(f"  {C['d']}checked: {final}{C['x']}")
    a = analyse(html)

    if a["js_injected"]:
        rep.f("bad", "Structured data is injected by JavaScript — crawlers never see it",
              "'application/ld+json' appears only inside JavaScript; there is no real "
              "<script type=\"application/ld+json\"> in the served HTML. This is the most "
              "deceptive failure here: dev tools and Google's Rich Results Test both run JS, "
              "so every tool you'd normally check with reports success. Render it server-side.")
    elif not a["blocks"]:
        rep.f("bad", "No structured data at all",
              "No application/ld+json on the page. It is the most reliable way to hand an "
              "assistant unambiguous facts: name, price, availability, brand.")
    elif a["bad_json"]:
        rep.f("bad", f"{a['bad_json']} structured-data block(s) failed to parse",
              "Invalid JSON is skipped entirely by consumers, so a broken block is worth zero.")
    elif not a["product"]:
        rep.f("warn", "Structured data present, but no Product type",
              "On a product page you want a Product node with an offers object.")
    else:
        have = [k for k, v in a["fields"].items() if v]
        miss = [k for k, v in a["fields"].items() if not v]
        rep.f("ok", ("ProductGroup" if a["is_group"] else "Product") + " schema found",
              "present: " + " ".join(have) + ("\nmissing: " + " ".join(miss) if miss else ""))
        off = a["offers"]
        if off:
            gaps = [k for k in ("price", "priceCurrency", "availability")
                    if off.get(k) in (None, "")]
            if gaps:
                rep.f("warn", "Offer is missing " + ", ".join(gaps),
                      "Assistants use these to decide whether you are a live, buyable option.")
            else:
                rep.f("ok", "Offer data is complete", "price, priceCurrency and availability all present.")
        else:
            rep.f("warn", "Product schema has no offers object",
                  "Without it there is no machine-readable price or availability.")

    w = a["words"]
    if w < 120:
        rep.f("bad", f"Only ~{w} words of readable text",
              "To a crawler that doesn't run JavaScript this page is close to blank, "
              "however it looks in a browser.")
    elif w < 300:
        rep.f("warn", f"~{w} words of readable text", "Thin — not much here to quote.")
    else:
        rep.f("ok", f"~{w} words of readable text", "Enough substance to be quotable.")

    m = a["meas"]
    if len(m) >= 5:
        rep.f("ok", f"{len(m)} concrete measurements", "e.g. " + ", ".join(m[:6]))
    else:
        rep.f("warn", f"Only {len(m)} concrete measurement(s) in the readable text",
              "Across 70 brands we scanned, the median was 2 — this is the most common real "
              "gap. Assistants repeat facts, not adjectives: 'holds 120 lb' survives the trip, "
              "'premium quality' does not. Dimensions, weight, materials, capacity, "
              "compatibility are the highest-value additions.")

    if a["title"] and a["og"]:
        agree = titles_agree(a["title"], a["og"])
        if agree is False:
            rep.f("bad", "Your <title> contradicts your own og:title",
                  f"title:    {a['title'][:70]}\nog:title: {a['og'][:70]}\n"
                  "The title is the strongest short summary a crawler gets. We found a live "
                  "product page whose title announced an entirely different product.")
    if not a["title"]:
        rep.f("bad", "No page title", "The strongest short summary a crawler gets.")
    if not a["canonical"]:
        rep.f("warn", "No canonical link", "Variant URLs can split how you are understood.")


def exit_code(rep, fail_on):
    if fail_on == "never":
        return 0
    if fail_on == "warning":
        return 1 if (rep.bad or rep.warn) else 0
    return 1 if rep.bad else 0


def main():
    ap = argparse.ArgumentParser(
        prog="aivis", description="Check whether AI assistants can read your store.",
        epilog="Example:  python3 aivis.py allbirds.com")
    ap.add_argument("store", help="your store domain, e.g. yourstore.com")
    ap.add_argument("--url", help="a specific product page to check")
    ap.add_argument("--no-color", action="store_true")
    ap.add_argument("--json", action="store_true",
                    help="machine-readable output (for CI)")
    ap.add_argument("--fail-on", choices=["critical", "warning", "never"],
                    default="critical",
                    help="exit non-zero on this severity or worse (default: critical)")
    ap.add_argument("--version", action="version", version=f"aivis {__version__}")
    args = ap.parse_args()
    paint(sys.stdout.isatty() and not args.no_color and not args.json)

    host = re.sub(r"^https?://", "", args.store).strip("/").split("/")[0]
    rep = R(quiet=args.json)
    if not args.json:
        print(f"\n{C['b']}aivis {__version__}{C['x']} — can AI assistants read {C['b']}{host}{C['x']}?")
        print(f"{C['d']}Nothing is uploaded. Reading your public pages directly.{C['x']}")

    check_robots(host, rep)
    check_product(host, rep, args.url)

    if args.json:
        json.dump({"tool": "aivis", "version": __version__, "host": host,
                   "critical": rep.bad, "warnings": rep.warn, "passed": rep.ok,
                   "findings": rep.findings}, sys.stdout, indent=2)
        print()
        return exit_code(rep, args.fail_on)

    print(f"\n{C['b']}Summary:{C['x']} {C['r']}{rep.bad} critical{C['x']}  "
          f"{C['y']}{rep.warn} to review{C['x']}  {C['g']}{rep.ok} passed{C['x']}")
    print(f"{C['d']}This cannot tell you whether an assistant WILL recommend you — nobody can; "
          f"rankings\nare not public and vary by wording. It also can't see third-party "
          f"mentions, which\nare probably the bigger factor. It checks the floor: whether you "
          f"are readable at all.\n\nMethod and the 70-store study: "
          f"https://github.com/krisdiallo/ecom-agent{C['x']}\n")
    return exit_code(rep, args.fail_on)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
