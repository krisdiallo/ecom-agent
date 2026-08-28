#!/usr/bin/env python3
"""
Turn the raw survey into figures. Every statistic prints its own denominator,
because the denominators genuinely differ: some hosts refuse a research
user-agent, some disable products.json, some aren't Shopify at all.
"""
import json, sys, statistics

d = json.load(open(sys.argv[1]))
N = len(d)


def pct(n, dd):
    return f"{n}/{dd} ({100.0*n/dd:.0f}%)" if dd else f"{n}/0 (n/a)"


print(f"# AI visibility survey — {N} hosts attempted\n")

# --- reachability ---
robots_ok = [r for r in d if r.get("robots_status") == 200 and not r.get("robots_is_html")]
blocked_ua = [r for r in d if r.get("robots_status") in (403, 429) or
              str(r.get("robots_error", "")).startswith("HTTP")]
prod_ok = [r for r in d if r.get("words") is not None]
shopify = [r for r in robots_ok if r.get("is_shopify_robots")]

print("## Reachability")
print(f"- robots.txt readable:            {pct(len(robots_ok), N)}")
print(f"- refused our research UA (403/429): {pct(len(blocked_ua), N)}")
print(f"- Shopify fingerprint in robots:  {pct(len(shopify), len(robots_ok))} of readable")
print(f"- product page analysed:          {pct(len(prod_ok), N)}")
print()

# --- robots.txt / AI crawlers ---
print("## robots.txt — are AI crawlers blocked?")
if robots_ok:
    sb = [r for r in robots_ok if r.get("search_blocked")]
    tb = [r for r in robots_ok if r.get("train_blocked")]
    ex = [r for r in robots_ok if r.get("has_explicit_ai_rules")]
    star = [r for r in robots_ok if r.get("star_blocks_all")]
    risky = [r for r in robots_ok if r.get("search_risky")]
    print(f"- block >=1 AI SEARCH crawler:    {pct(len(sb), len(robots_ok))}")
    print(f"- block >=1 AI TRAINING crawler:  {pct(len(tb), len(robots_ok))}")
    print(f"- any explicit AI crawler rule:   {pct(len(ex), len(robots_ok))}")
    print(f"- User-agent: * disallows all:    {pct(len(star), len(robots_ok))}")
    print(f"- search bot blocked from catalog paths: {pct(len(risky), len(robots_ok))}")
    for r in sb:
        print(f"    ! {r['host']}: blocks {', '.join(r['search_blocked'])}")
    for r in tb:
        print(f"    · {r['host']}: training opt-out {', '.join(r['train_blocked'])}")
print()

# --- product pages ---
print("## Product pages — can a crawler read the facts?")
if prod_ok:
    n = len(prod_ok)
    has = [r for r in prod_ok if r.get("has_product_schema")]
    nojs = [r for r in prod_ok if r.get("jsonld_js_injected")]
    noschema = [r for r in prod_ok if not r.get("has_product_schema")]
    mal = [r for r in prod_ok if r.get("jsonld_malformed")]
    grp = [r for r in has if r.get("is_product_group")]
    print(f"- has Product/ProductGroup schema: {pct(len(has), n)}")
    print(f"- NO product schema in raw HTML:   {pct(len(noschema), n)}")
    print(f"    of which JS-injected (invisible but 'passes' JS-running testers): {len(nojs)}")
    print(f"- malformed JSON-LD blocks:        {pct(len(mal), n)}")
    print(f"- uses ProductGroup (variants):    {pct(len(grp), len(has)) if has else 'n/a'}")

    offers = [r for r in has if r.get("has_offers")]
    print(f"- schema includes offers:          {pct(len(offers), len(has)) if has else 'n/a'}")
    if offers:
        for k, lab in (("offer_price", "price"), ("offer_currency", "priceCurrency"),
                       ("offer_availability", "availability")):
            good = [r for r in offers if r.get(k)]
            print(f"    · {lab:<14} present:      {pct(len(good), len(offers))}")
        full = [r for r in offers if r.get("offer_price") and r.get("offer_currency")
                and r.get("offer_availability")]
        print(f"    · ALL THREE present:          {pct(len(full), len(offers))}")
    for k, lab in (("has_brand", "brand"), ("has_sku", "sku/gtin"),
                   ("has_rating", "aggregateRating"), ("has_description", "description")):
        good = [r for r in has if r.get(k)]
        print(f"- schema has {lab:<16} {pct(len(good), len(has)) if has else 'n/a'}")
    print()

    print("## Readable text in raw HTML (what a non-JS crawler sees)")
    w = sorted(r["words"] for r in prod_ok)
    print(f"- median words: {int(statistics.median(w))}   min: {w[0]}   max: {w[-1]}")
    for thresh in (120, 300):
        thin = [r for r in prod_ok if r["words"] < thresh]
        print(f"- under {thresh} words: {pct(len(thin), n)}")
    for r in sorted(prod_ok, key=lambda r: r["words"])[:6]:
        print(f"    · {r['host']}: {r['words']} words, {r.get('product_bytes',0)//1024}KB page")
    print()

    named = [r for r in prod_ok if "name_in_raw_html" in r]
    if named:
        miss = [r for r in named if not r["name_in_raw_html"]]
        print(f"- product NAME missing from raw HTML: {pct(len(miss), len(named))}")
        for r in miss:
            print(f"    ! {r['host']}")
    priced = [r for r in prod_ok if "price_in_raw_html" in r]
    if priced:
        miss = [r for r in priced if not r["price_in_raw_html"]]
        print(f"- PRICE missing from raw HTML:       {pct(len(miss), len(priced))}")

    tm = [r for r in prod_ok if r.get("title_og_consistent") is not None]
    if tm:
        bad = [r for r in tm if not r["title_og_consistent"]]
        print(f"- <title> contradicts og:title:      {pct(len(bad), len(tm))}")
        for r in bad:
            print(f"    ! {r['host']}")
            print(f"        title = {r.get('title','')[:70]!r}")
            print(f"        og    = {str(r.get('og_title'))[:70]!r}")

    meas = [r["measurements"] for r in prod_ok if "measurements" in r]
    if meas:
        few = [m for m in meas if m < 5]
        print(f"- fewer than 5 concrete measurements: {pct(len(few), len(meas))}"
              f"   median={int(statistics.median(sorted(meas)))}")
    nocanon = [r for r in prod_ok if not r.get("has_canonical")]
    print(f"- no canonical link:                 {pct(len(nocanon), n)}")
