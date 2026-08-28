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
sys.exit(1 if fail else 0)
