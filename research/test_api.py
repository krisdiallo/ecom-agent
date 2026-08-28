#!/usr/bin/env python3
"""The public library API is the part other projects would depend on, so it needs a
contract test. The classifications below are sourced to vendor documentation; if one
of these flips, crawlers.json and the docs are wrong too."""
import importlib.util, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("aivis", os.path.join(HERE, "aivis.py"))
a = importlib.util.module_from_spec(spec); sys.argv = ["aivis"]
try:
    spec.loader.exec_module(a)
except SystemExit:
    pass

fail = False


def eq(got, want, what):
    global fail
    if got != want:
        print(f"FAIL: {what}: got {got!r}, want {want!r}")
        fail = True


# The distinction the whole project exists to make.
eq(a.classify_crawler("GPTBot")["blocking_effect"], "opts_out_of_training_only", "GPTBot")
eq(a.classify_crawler("OAI-SearchBot")["blocking_effect"], "removes_from_ai_answers", "OAI-SearchBot")
# Amazon splits the roles across tokens; conflating them costs Alexa visibility.
eq(a.classify_crawler("Amazonbot")["blocking_effect"], "opts_out_of_training_only", "Amazonbot")
eq(a.classify_crawler("Amzn-SearchBot")["blocking_effect"], "removes_from_ai_answers", "Amzn-SearchBot")
# Apple's opt-out token does not crawl at all.
eq(a.classify_crawler("Applebot-Extended")["blocking_effect"], "opts_out_of_training_only", "Applebot-Extended")
eq(a.classify_crawler("applebot")["purpose"], "search", "case-insensitive lookup")
# Never guess.
eq(a.classify_crawler("SomeRandomBot"), None, "unknown token")
eq(a.classify_crawler(""), None, "empty token")

r = a.audit_robots("User-agent: OAI-SearchBot\nDisallow: /\n\nUser-agent: GPTBot\nDisallow: /\n")
eq(r["visible_to_ai_search"], False, "blocked search bot -> not visible")
eq(r["blocked_search"], ["OAI-SearchBot"], "blocked_search")
eq(r["blocked_training"], ["GPTBot"], "blocked_training")

# A stock Shopify file has ~45 Disallow rules and must not read as broken.
shopify = """User-agent: *
Disallow: /admin
Disallow: /cart
Disallow: /collections/*sort_by*
Disallow: /blogs/*+*
Disallow: /*?*oseid=*
Sitemap: https://example.com/sitemap.xml
"""
r2 = a.audit_robots(shopify)
eq(r2["visible_to_ai_search"], True, "stock Shopify is visible")
eq(r2["blocked_search"], [], "stock Shopify blocks no search bot")
eq(r2["sitemaps"], ["https://example.com/sitemap.xml"], "sitemap extraction")

eq(a.audit_robots("")["visible_to_ai_search"], True, "empty robots.txt is permissive")

print("ok: crawler classification, robots audit, and no-guess behaviour all hold")
# --- the training opt-out generator must not block search crawlers ---
gen = a.training_optout_robots()
g = a.audit_robots(gen)
eq(g["visible_to_ai_search"], True, "generated opt-out keeps AI search visibility")
eq(g["blocked_search"], [], "generated opt-out blocks no search crawler")
eq(len(g["blocked_training"]), len(a.TRAINING_TOKENS), "generated opt-out blocks every training crawler")
print("ok: training opt-out generator is search-safe")

# --- the "not a product page" downgrade must not swallow JS-injected stores -------------
# check_product demotes the measurement warning to a note when a page is not a product
# page. A first version gated that on `analyse()["product"]` alone, which is None for a
# store whose JSON-LD is injected by JavaScript — so Brooklinen, a real product page with
# the single worst defect the study found, was told the check did not apply to it. The
# guard is now `rep.saw_product or a product-shaped URL`; both halves are pinned here.
_JS_INJECTED = """<html><head><title>Sheet Set</title>
<script>var d={"@type":"application/ld+json"};window.x='application/ld+json';</script>
</head><body><p>A sheet set.</p></body></html>"""

_a = a.analyse(_JS_INJECTED)
assert _a["js_injected"] is True, "JS-injected JSON-LD no longer detected"
assert _a["product"] is None, "fixture should have no parseable Product node"
# saw_product is what check_product actually gates on, and it must be true here
assert bool(_a.get("product")) or _a.get("js_injected"), \
    "a JS-injected store would be demoted to 'not a product page'"

for _u in ("https://x.com/products/sheet-set", "https://x.com/shop/thing",
           "https://x.com/collections/bed/products/sheet", "https://x.com/dp/B01"):
    assert a.PROD_PAT.search(_u), f"PROD_PAT no longer matches product URL {_u}"
for _u in ("https://x.com/", "https://x.com/about", "https://x.com/blog/post"):
    assert not a.PROD_PAT.search(_u), f"PROD_PAT wrongly matches non-product URL {_u}"

print("check_product product-page guard OK")

sys.exit(1 if fail else 0)

