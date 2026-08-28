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
import argparse, gzip, io, ipaddress, json, re, socket, sys
import urllib.error, urllib.parse, urllib.request
from html import unescape

__version__ = "1.5.0"

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


# A page we have actually seen in the wild is 1.6 MB, and --pages 25 multiplies that.
# Nothing stopped a target serving far more, and the gzip path was worse: a small
# download decompresses unbounded, so a decompression bomb turns a few KB on the wire
# into gigabytes in memory. Both paths are now capped. 8 MB is ~5x the largest real
# page observed, which is generous for a document we only parse for text and JSON-LD.
MAX_BYTES = 8 * 1024 * 1024


def _read_capped(fp, limit=MAX_BYTES):
    """Read at most `limit` bytes. Truncation is not an error: a page too large to be
    read whole is also too large to be a sane product page, and the checks that matter
    (schema, title, facts) live near the top of the document anyway."""
    return fp.read(limit + 1)[:limit]


def _gunzip_capped(raw, limit=MAX_BYTES):
    out, z = b"", gzip.GzipFile(fileobj=io.BytesIO(raw))
    while len(out) < limit:
        chunk = z.read(min(262144, limit - len(out)))
        if not chunk:
            break
        out += chunk
    return out


# Benchmarks from our own published survey of 70 consumer brands (2026-08-28).
# Raw data: research/data/, method and caveats: STUDY.md. Embedded rather than fetched
# so the tool keeps working offline and in three years — the numbers are dated, and a
# dated number you can see beats a live one you cannot reach.
#
# The point is to answer "compared to what?". Telling someone they have 2 concrete
# measurements is useless; telling them 2 is the median of 51 well-resourced brands,
# and that a quarter of those brands have none at all, is actionable.
BENCH = {
    "n_pages": 51, "n_hosts": 70, "measured": "2026-08-28",
    "measurements": {25: 0, 50: 2, 75: 4, 90: 9},
    "words": {25: 894, 50: 1508, 75: 2170, 90: 3022},
    "schema_pct": 88,
    "agent_commerce_pct": 70,
}


def band_of(value, table):
    """Describe where a value sits in the published distribution, in words.

    Deliberately not "you are at the Nth percentile". Because p25 for concrete
    measurements is 0, a store with ZERO measurements came out as "at or above the 25th
    percentile" — technically true, and the exact opposite of what the reader needs to
    hear. A number that flatters is worse than a phrase that is blunt.
    """
    if value >= table[90]:
        return "top 10% of the sample"
    if value >= table[75]:
        return "top 25%"
    if value >= table[50]:
        return "above the median"
    if value > table[25]:
        return "below the median"
    if value > 0:
        return "bottom 25%"
    return "bottom 25% — nothing at all here"


class BlockedTarget(Exception):
    """Refused before any connection was made."""


def _public_ip(ip):
    a = ipaddress.ip_address(ip)
    return not (a.is_private or a.is_loopback or a.is_link_local or a.is_reserved
                or a.is_multicast or a.is_unspecified)


def guard_url(url):
    """Refuse anything that is not a public http(s) target.

    This matters more here than in an ordinary CLI: aivis also runs as an MCP server,
    so the hostname can come from a model that was itself fed untrusted text. Without
    this, "check my store at 169.254.169.254" would make the tool fetch a cloud
    metadata endpoint on the caller's behalf — a textbook SSRF, with the agent as the
    confused deputy. Verified before the fix that the fetch was attempted.

    Resolution is checked, not just the literal string, because a hostname an attacker
    controls can resolve to 127.0.0.1 or 10.x just as easily as to a public address.
    """
    p = urllib.parse.urlsplit(url)
    if p.scheme not in ("http", "https"):
        raise BlockedTarget(f"scheme {p.scheme!r} not allowed")
    host = p.hostname
    if not host:
        raise BlockedTarget("no host")
    try:
        infos = socket.getaddrinfo(host, p.port or (443 if p.scheme == "https" else 80),
                                   proto=socket.IPPROTO_TCP)
    except socket.gaierror as e:
        raise BlockedTarget(f"cannot resolve {host}: {e.strerror or e}")
    ips = {i[4][0] for i in infos}
    bad = [ip for ip in ips if not _public_ip(ip)]
    if bad:
        raise BlockedTarget(f"{host} resolves to non-public address {bad[0]}")
    return url


class _GuardedRedirect(urllib.request.HTTPRedirectHandler):
    """A public host can 302 to an internal one, so every hop is re-checked."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        guard_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_opener = urllib.request.build_opener(_GuardedRedirect)


def get(url, timeout=25):
    try:
        guard_url(url)
    except BlockedTarget:
        return 0, url, ""
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"})
    try:
        with _opener.open(req, timeout=timeout) as r:
            raw = _read_capped(r)
            if r.headers.get("Content-Encoding") == "gzip":
                raw = _gunzip_capped(raw)
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


# ---------------------------------------------------------------------------
# Public library API.
#
# The audience actually reachable through a registry and GitHub is developers
# building GEO tools and shopping agents, not merchants. They need the primitive,
# not the report: "is this token a search crawler or a training crawler, and what
# does blocking it cost me?" Every value below is sourced to the vendor's own
# documentation — see crawlers.json for the quotes and dates.
#
#     from aivis import classify_crawler, audit_robots
#     classify_crawler("GPTBot")["blocking_effect"]   # 'opts_out_of_training_only'
#     audit_robots(open("robots.txt").read())["blocked_search"]
# ---------------------------------------------------------------------------

SEARCH_TOKENS = tuple(t for t, _ in SEARCH_BOTS)
TRAINING_TOKENS = tuple(t for t, _ in TRAIN_BOTS)

#: Tokens the vendor documents as user-initiated, where robots.txt may not apply.
USER_INITIATED = ("ChatGPT-User", "Perplexity-User", "meta-externalfetcher")


def classify_crawler(token):
    """Classify a robots.txt user-agent token.

    Returns None for unknown tokens rather than guessing — an unrecognised crawler
    is not evidence of anything, and defaulting it to 'training' would be the exact
    conflation this project exists to correct.
    """
    k = (token or "").strip().lower()
    for t, what in SEARCH_BOTS:
        if t.lower() == k:
            return {"token": t, "purpose": "search", "serves": what,
                    "blocking_effect": "removes_from_ai_answers"}
    for t, what in TRAIN_BOTS:
        if t.lower() == k:
            return {"token": t, "purpose": "training", "serves": what,
                    "blocking_effect": "opts_out_of_training_only"}
    for t in USER_INITIATED:
        if t.lower() == k:
            return {"token": t, "purpose": "user_initiated", "serves": "user-initiated fetch",
                    "blocking_effect": "may_be_ignored"}
    return None


def audit_robots(robots_txt):
    """Which AI crawlers a robots.txt blocks, split by what blocking actually costs.

    Applies real group precedence: a crawler obeys its own group and ignores
    ``User-agent: *`` when it has one. Paths are classified so that the ~45 default
    Disallow rules on a stock Shopify store do not read as a problem.
    """
    g = parse_robots(robots_txt or "")
    out = {"blocked_search": [], "blocked_training": [],
           "search_restricted_from_catalog": [], "allowed_search": [],
           "sitemaps": re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots_txt or "")}
    for token in SEARCH_TOKENS:
        v = verdict(group_for(g, token))
        if v == "blocked":
            out["blocked_search"].append(token)
        elif v == "risky":
            out["search_restricted_from_catalog"].append(token)
        else:
            out["allowed_search"].append(token)
    for token in TRAINING_TOKENS:
        if verdict(group_for(g, token)) == "blocked":
            out["blocked_training"].append(token)
    out["visible_to_ai_search"] = not out["blocked_search"]
    return out


def training_optout_robots(comment=True):
    """Emit a robots.txt block that opts out of AI *training* without losing AI search.

    Context, stated fairly. The ecosystem's default blocklist
    (ai-robots-txt/ai.robots.txt, ~4k stars) disallows all 166 known AI user-agents.
    Audited with audit_robots(), that file blocks every search crawler we track
    alongside the training ones — and that is DELIBERATE, not a defect. Their FAQ is
    explicit that these crawlers are "extractive, confer no benefit to the creators of
    data they're ingesting". A publisher who does not want their articles answering
    questions without a click wants exactly that file.

    Blocking AI is two decisions, though, and one list collapses them: "don't train on
    me" costs nothing in recommendations, while "don't answer questions using me"
    removes you from ChatGPT search, Perplexity, Claude, Alexa, Siri and Spotlight. A
    publisher usually wants both. An ecommerce store usually wants the first and not the
    second, because absence from AI answers is lost demand rather than protected work.

    This emits that second option. Every token is sourced to vendor documentation in
    crawlers.json.
    """
    lines = []
    if comment:
        lines += [
            "# Opt out of AI training WITHOUT losing AI search visibility.",
            "# Blocking a training crawler costs you nothing in recommendations.",
            "# Blocking a SEARCH crawler removes you from AI answers entirely — so the",
            "# search crawlers are deliberately absent below. Verify with:",
            "#   python3 aivis.py yourstore.com",
            f"# Tokens sourced to vendor docs: {len(TRAIN_BOTS)} training crawlers.",
            "",
        ]
    for token, what in TRAIN_BOTS:
        lines += [f"# {what}", f"User-agent: {token}", "Disallow: /", ""]
    if comment:
        lines += [
            "# Left ALLOWED on purpose — blocking these removes you from AI answers:",
            "#   " + ", ".join(t for t, _ in SEARCH_BOTS),
        ]
    return "\n".join(lines).rstrip() + "\n"


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


def lead(s, n=4):
    """Leading content words — where the product's identity actually lives.
    Both an SEO title and an og:title normally open with the product name."""
    out = []
    for w in fold(s).split():
        if len(w) > 1 and w not in STOP:
            out.append(w)
        if len(out) >= n:
            break
    return out


def titles_agree(t, o):
    """Do <title> and og:title name the same product?

    Deliberately conservative, after three iterations of this check crying wolf:
      v1 compared <title> to the internal products.json name  -> 3 false positives
         in 4 (merchants use different internal vs display names).
      v2 used substring matching                               -> flagged a title whose
         bracketed suffix contained a '|'.
      v3 used 50% token overlap                                -> flagged Allbirds twice,
         where the title is an SEO phrase and og:title is the variant
         ("Women's Dasher NZ Sneakers | ..." vs "Women's Dasher NZ - Blizzard/Deep Navy").
         Same product, different specificity. Not a defect.

    So: flag only when the leading words share NOTHING at all. That catches the real
    case — a bath-towel page whose title announces a sheet set — and stays quiet on
    every legitimate variation seen across 70 live stores. Under-reporting here is
    much cheaper than telling a healthy store it is broken.
    """
    a, b = toks(t), toks(o)
    if not a or not b:
        return None
    la, lb = lead(t), lead(o)
    if not la or not lb:
        return None
    return bool(set(la) & b or set(lb) & a)


# ---------- report ----------
class R:
    def __init__(self, quiet=False):
        self.bad = self.warn = self.ok = 0
        self.quiet = quiet
        self.findings = []
        self.saw_product = False

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
            check_sitemap(host, rep, "")
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
    check_sitemap(host, rep, txt)


def check_sitemap(host, rep, robots_txt=""):
    """Found by running this tool on our own site: our robots.txt lived at
    /ecom-agent/robots.txt, which crawlers never read — robots.txt is only honoured
    at the domain root. The Sitemap: line in it was therefore invisible, so nothing
    pointed crawlers at our sitemap at all."""
    declared = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots_txt or "")
    if declared:
        rep.f("ok", f"Sitemap declared in robots.txt",
              declared[0] + "\nCrawlers that read your robots.txt are pointed straight at it.")
        return
    st, _, _ = get(f"https://{host}/sitemap.xml", timeout=15)
    if st == 200:
        rep.f("warn", "Sitemap exists but robots.txt doesn't point to it",
              f"https://{host}/sitemap.xml responds, but no Sitemap: line appears in your "
              "robots.txt. Crawlers have to guess the location. Add:\n"
              f"  Sitemap: https://{host}/sitemap.xml")
    else:
        rep.f("warn", "No sitemap crawlers can find",
              f"No Sitemap: line in robots.txt and https://{host}/sitemap.xml did not respond. "
              "Nothing tells a crawler what pages exist, so discovery depends entirely on links "
              "pointing at you from elsewhere.\n"
              "If your site lives on a subpath (e.g. user.github.io/project), note that a "
              "robots.txt inside that subpath is ignored — only the one at the domain root "
              "counts, and on shared hosts you usually don't control it.")


PROD_PAT = re.compile(r"/(products?|shop|item|p|dp|collections/[^/]+/products)/[^/\s<]+", re.I)


def find_products(host, want=1, budget=6):
    """Collect up to `want` product URLs. One page is an anecdote; a catalogue tells
    you whether a problem is systemic or a one-off on the page you happened to open."""
    urls = []
    st, _, js = get(f"https://{host}/products.json?limit={max(want, 1)}")
    if st == 200 and js:
        try:
            for p in json.loads(js).get("products", [])[:want]:
                if p.get("handle"):
                    urls.append((f"https://{host}/products/{p['handle']}",
                                 p.get("title"),
                                 (p.get("variants") or [{}])[0].get("price")))
        except Exception:
            pass
    if len(urls) < want:
        for u in sitemap_product_urls(host, want - len(urls), budget):
            if all(u != x[0] for x in urls):
                urls.append((u, None, None))
    return urls[:want]


def sitemap_product_urls(host, want=1, budget=6):
    seen, queue, found = set(), [], []
    st, _, robots = get(f"https://{host}/robots.txt")
    queue += re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots or "")
    queue += [f"https://{host}/sitemap.xml", f"https://{host}/sitemap_index.xml",
              f"https://{host}/product-sitemap.xml",
              f"https://{host}/sitemap_products_1.xml?from=1&to=999999999"]
    while queue and budget > 0 and len(found) < want:
        sm = queue.pop(0)
        if sm in seen:
            continue
        seen.add(sm)
        budget -= 1
        st, _, xml = get(sm, timeout=20)
        if st != 200 or not xml:
            continue
        locs = re.findall(r"<loc>\s*([^<\s]+?)\s*</loc>", xml)
        for u in locs:
            if PROD_PAT.search(u) and u not in found:
                found.append(u)
                if len(found) >= want:
                    break
        children = [u for u in locs if u.lower().endswith((".xml", ".xml.gz"))]
        children.sort(key=lambda u: 0 if re.search(r"product|item|shop", u, re.I) else 1)
        queue = children[:4] + queue
    return found


def find_product_via_sitemap(host, budget=6):
    """Single-URL convenience wrapper. Platform-agnostic on purpose: Shopify is only
    about 3 in 4 of the stores we sampled."""
    r = sitemap_product_urls(host, 1, budget)
    return r[0] if r else None


def _legacy_find(host, budget=6):
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


def check_agent_commerce(host, rep):
    """The layer everyone arguing about robots.txt is missing.

    Shopify now serves /llms.txt "Agent Instructions" advertising the Universal
    Commerce Protocol: a live MCP endpoint an agent can call to search your catalogue,
    build a cart and complete a checkout. That is a machine-readable commerce API which
    skips HTML parsing altogether — so it matters more than any amount of page copy for
    an agent that intends to actually buy. Verified live on real stores 2026-08-28.

    Read-only: this only ever calls tools/list, which enumerates capabilities. It never
    creates a cart or starts a checkout.
    """
    say = (lambda *a, **k: None) if rep.quiet else print
    say(f"\n{C['b']}3. Agent commerce — can an AI agent actually transact with you?{C['x']}")

    st, ct, body = get_ct(f"https://{host}/llms.txt")
    has_llms = (st == 200 and "html" not in ct.lower()
                and not re.match(r"\s*<", body or "")
                and not re.search(r"<!doctype|<html", (body or "")[:600], re.I))
    # Two different conventions are live in the wild and they mean different things:
    #   - Shopify's auto-generated "# Agent Instructions — Brand", which advertises UCP
    #     and a transactional MCP endpoint;
    #   - the original docs-style llms.txt (an H1 plus a summary), which is purely
    #     descriptive and never claims a commerce endpoint at all.
    # Treating the second as a broken promise would accuse a store of failing to deliver
    # something it never offered.
    claims_commerce = has_llms and bool(
        re.search(r"agent instructions|ucp\b|/api/ucp/mcp|shop\.app/SKILL\.md", body, re.I))

    st2, _, ucp_body = get_ct(f"https://{host}/.well-known/ucp")
    endpoint, version = None, None
    if st2 == 200 and (ucp_body or "").strip().startswith("{"):
        try:
            u = json.loads(ucp_body)
            u = u.get("ucp", u)
            version = u.get("version")
            for s in (u.get("services") or {}).get("dev.ucp.shopping") or []:
                if s.get("transport") == "mcp" and s.get("endpoint"):
                    endpoint = s["endpoint"]
                    break
        except Exception:
            pass

    tools = []
    if endpoint or st2 == 200:
        ep = endpoint or f"https://{host}/api/ucp/mcp"
        payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).encode()
        st3, _, mb = get_ct(ep, data=payload, ctype="application/json", timeout=20)
        if st3 == 200 and (mb or "").strip().startswith("{"):
            try:
                tools = sorted(t.get("name") for t in
                               json.loads(mb).get("result", {}).get("tools", []) if t.get("name"))
            except Exception:
                pass

    if tools:
        buy = [t for t in tools if re.search(r"checkout|cart|order", t)]
        rep.f("ok", f"Live agent-commerce endpoint — {len(tools)} tools",
              "An AI agent can call your store directly instead of scraping it.\n"
              + (f"UCP version {version}\n" if version else "")
              + "tools: " + ", ".join(tools[:8]) + ("…" if len(tools) > 8 else "")
              + (f"\nIncludes {len(buy)} cart/checkout tools, so an agent can complete a purchase."
                 if buy else ""))
    elif claims_commerce or version:
        rep.f("bad", "Agent commerce is advertised but the endpoint does not answer",
              "Your /llms.txt or UCP profile tells agents how to transact with you, and the MCP "
              "endpoint did not return a tool list. An agent that follows your own instructions "
              "hits a dead end — worse than not advertising it at all.")
    elif has_llms:
        rep.f("ok", "Serves a descriptive llms.txt (no commerce endpoint)",
              "This is the original llms.txt convention: a plain-language summary for assistants, "
              "not a transactional interface. It makes no claim about commerce, so nothing here "
              "is broken. Note that no AI vendor currently documents reading other sites' "
              "llms.txt, so treat it as cheap and harmless rather than as a visibility lever.")
    elif not rep.saw_product:
        rep.note("No agent-commerce endpoint (and no product page found)",
                 "This does not look like a storefront, so that is expected rather than a "
                 "problem. Run it against a store to get a meaningful result here.")
    else:
        rep.f("warn", "No agent-commerce endpoint found",
              "No /llms.txt agent instructions and no /.well-known/ucp profile. Shopify serves "
              "these automatically on stores that support the Universal Commerce Protocol — "
              "7 of 8 Shopify stores we sampled had a live one. Without it, an agent that wants "
              "to buy has to scrape your HTML, which is strictly worse for both of you.\n"
              "This is newer and less discussed than robots.txt, and it is the layer that "
              "decides whether an assistant can transact rather than merely describe you.")


def get_ct(url, timeout=15, data=None, ctype=None):
    """get() variant that also returns Content-Type, needed to spot soft-404s that
    answer 200 with an HTML page."""
    try:
        guard_url(url)
    except BlockedTarget:
        return 0, "", ""
    h = {"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"}
    if ctype:
        h["Content-Type"] = ctype
    req = urllib.request.Request(url, headers=h, data=data)
    try:
        with _opener.open(req, timeout=timeout) as r:
            raw = _read_capped(r)
            if r.headers.get("Content-Encoding") == "gzip":
                raw = _gunzip_capped(raw)
            return r.status, r.headers.get("Content-Type", ""), raw.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, "", ""
    except Exception:
        return 0, "", ""


def check_catalogue(host, rep, n):
    """Sample n product pages and report whether problems are systemic or one-offs."""
    say = (lambda *a, **k: None) if rep.quiet else print
    say(f"\n{C['b']}2. Product pages — sampling {n} across the catalogue{C['x']}")
    items = find_products(host, want=n)
    if not items:
        rep.note("Could not find product pages automatically",
                 f"Try a single page:  python3 aivis.py {host} --url https://{host}/<product>")
        return
    rows, issues = [], {"no_schema": [], "js_injected": [], "thin": [],
                        "few_meas": [], "title_clash": [], "no_offers": []}
    for url, _title, _price in items:
        st, final, html = get(url)
        if st != 200 or not html:
            continue
        a = analyse(html)
        rows.append((final, a))
        if a["js_injected"]:
            issues["js_injected"].append(final)
        elif not a["product"]:
            issues["no_schema"].append(final)
        elif not a.get("offers"):
            issues["no_offers"].append(final)
        if a["words"] < 300:
            issues["thin"].append(final)
        if len(a["meas"]) < 5:
            issues["few_meas"].append(final)
        if a["title"] and a["og"] and titles_agree(a["title"], a["og"]) is False:
            issues["title_clash"].append(final)
    if not rows:
        rep.note("Found product URLs but could not fetch any of them")
        return
    t = len(rows)
    rep.saw_product = any(a.get("product") or a.get("js_injected") for _u, a in rows)
    say(f"  {C['d']}checked {t} page(s){C['x']}")

    def report(key, lvl, label, detail):
        hits = issues[key]
        if not hits:
            return
        frac = f"{len(hits)}/{t} pages"
        rep.f(lvl, f"{label} ({frac})",
              detail + "\n" + "\n".join("· " + u for u in hits[:4]) +
              (f"\n… and {len(hits)-4} more" if len(hits) > 4 else ""))

    report("js_injected", "bad", "Structured data injected by JavaScript",
           "Invisible to crawlers that don't run JS, while looking perfect in dev tools.")
    report("no_schema", "bad", "No Product schema in raw HTML",
           "Nothing hands an assistant unambiguous name/price/availability.")
    report("no_offers", "warn", "Product schema without an offers object",
           "No machine-readable price or availability.")
    report("title_clash", "bad", "<title> contradicts og:title",
           "The page disagrees with itself about what it sells.")
    report("thin", "warn", "Under 300 readable words in raw HTML",
           "Little for an assistant to quote.")
    report("few_meas", "warn", "Fewer than 5 concrete measurements",
           "Across 70 brands we scanned the median was 2 — this is the most common gap. "
           "Assistants repeat facts, not adjectives.")
    clean = t - len({u for k in issues for u in issues[k]})
    if clean:
        rep.f("ok", f"{clean}/{t} pages clean on every check", "")


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
    # "Is this a storefront?" is better answered by finding Product schema than by
    # having successfully fetched some page — an explicit --url could be anything.
    rep.saw_product = bool(a.get("product")) or a.get("js_injected", False)

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
    wvs = (f"Benchmark: median {BENCH['words'][50]:,} words, top 25% is "
           f"{BENCH['words'][75]:,}+. You: {band_of(w, BENCH['words'])}.")
    if w < 120:
        rep.f("bad", f"Only ~{w} words of readable text",
              "To a crawler that doesn't run JavaScript this page is close to blank, "
              "however it looks in a browser.")
    elif w < 300:
        rep.f("warn", f"~{w} words of readable text", "Thin — not much here to quote.\n" + wvs)
    else:
        rep.f("ok", f"~{w} words of readable text",
              "Enough substance to be quotable.\n" + wvs)

    m = a["meas"]
    vs = (f"Benchmark ({BENCH['n_pages']} pages, {BENCH['measured']}): median "
          f"{BENCH['measurements'][50]}, top 25% is {BENCH['measurements'][75]}+, "
          f"top 10% is {BENCH['measurements'][90]}+. You: "
          f"{band_of(len(m), BENCH['measurements'])}.")
    if len(m) >= 5:
        rep.f("ok", f"{len(m)} concrete measurements", "e.g. " + ", ".join(m[:6]) + "\n" + vs)
    else:
        rep.f("warn", f"Only {len(m)} concrete measurement(s) in the readable text",
              vs + "\nAssistants repeat facts, not adjectives: 'holds 120 lb' survives the "
              "trip, 'premium quality' does not. Dimensions, weight, materials, capacity and "
              "compatibility are the highest-value additions — and note a quarter of the brands "
              "we measured have none at all, so this is the most winnable gap on the list.")

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
    ap.add_argument("store", nargs="?", help="your store domain, e.g. yourstore.com")
    ap.add_argument("--url", help="a specific product page to check")
    ap.add_argument("--pages", type=int, default=1, metavar="N",
                    help="sample N product pages instead of one, and report whether "
                         "problems are systemic (default: 1)")
    ap.add_argument("--no-color", action="store_true")
    ap.add_argument("--training-optout", action="store_true",
                    help="print a robots.txt block that opts out of AI training while "
                         "keeping AI search visibility, then exit")
    ap.add_argument("--no-agent", action="store_true",
                    help="skip the agent-commerce (UCP/MCP) check")
    ap.add_argument("--json", action="store_true",
                    help="machine-readable output (for CI)")
    ap.add_argument("--fail-on", choices=["critical", "warning", "never"],
                    default="critical",
                    help="exit non-zero on this severity or worse (default: critical)")
    ap.add_argument("--version", action="version", version=f"aivis {__version__}")
    args = ap.parse_args()
    if args.training_optout:
        sys.stdout.write(training_optout_robots())
        return 0
    if not args.store:
        # store is nargs="?" only so --training-optout can run without it; every other
        # path still needs it, and must say so rather than crashing on None.
        ap.error("a store domain is required (or use --training-optout)")
    paint(sys.stdout.isatty() and not args.no_color and not args.json)

    host = re.sub(r"^https?://", "", args.store).strip("/").split("/")[0]
    rep = R(quiet=args.json)
    if not args.json:
        print(f"\n{C['b']}aivis {__version__}{C['x']} — can AI assistants read {C['b']}{host}{C['x']}?")
        print(f"{C['d']}Nothing is uploaded. Reading your public pages directly.{C['x']}")

    check_robots(host, rep)
    if args.pages > 1 and not args.url:
        check_catalogue(host, rep, min(args.pages, 25))
    else:
        check_product(host, rep, args.url)
    if not args.no_agent:
        check_agent_commerce(host, rep)

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
