#!/usr/bin/env python3
"""Contract tests for crawler-consequences.json.

The value of this dataset is entirely that it does not guess. These tests exist
because the first build of it did guess, in four places, and every one of them was
the same failure mode the whole project exists to correct: reading a sentence that
merely mentions scraping as proof of what blocking costs you.
"""
import json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(HERE, "crawler-consequences.json")))
ROWS = D["crawlers"]
BY = {r["token"]: r for r in ROWS}
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


# 1. Regression: these were classified from text that does not support it.
# "Scrapes data." says something is fetched, not what for. "a variety of uses
# including training AI" says the purpose is plural and therefore unstated.
for tok in ("GoogleOther", "GoogleOther-Image", "GoogleOther-Video", "Scrapy",
            "Sidetrade indexer bot", "VelenPublicWebCrawler", "AgentTimes"):
    r = BY.get(tok)
    check(r is not None, f"{tok} missing from dataset")
    if r:
        check(r["blocking_effect"] == "undetermined",
              f"{tok} regressed to {r['blocking_effect']!r} — its source text "
              f"({r['function']!r}) does not establish a consequence")

# 2. Our own vendor-documented registry must survive verbatim. If these ever drift,
# the derived layer is overwriting sourced facts.
ours = {c["token"]: c for c in
        json.load(open(os.path.join(HERE, "crawlers.json")))["crawlers"]}
for tok, c in ours.items():
    r = BY.get(tok)
    check(r is not None, f"vendor-documented {tok} absent from consequences")
    if r:
        check(r["blocking_effect"] == c["blocking_effect"],
              f"{tok}: consequences says {r['blocking_effect']}, "
              f"crawlers.json says {c['blocking_effect']}")
        check(r["basis"] == "vendor-documented",
              f"{tok} should carry basis=vendor-documented, has {r['basis']!r}")

# 3. Every row carries a basis, and every basis is one we defined. A new basis string
# appearing silently would mean a consumer's confidence filter stops working.
VALID = {"vendor-documented", "explicit-purpose-text", "upstream-category",
         "source-does-not-establish-consequence",
         "source-describes-mixed-or-unstated-purpose"}
for r in ROWS:
    check(r.get("basis") in VALID, f"{r['token']}: unknown basis {r.get('basis')!r}")
    check(r.get("blocking_effect"), f"{r['token']}: no blocking_effect")

# 4. Nothing determined may rest on mixed-purpose wording.
for r in ROWS:
    fn = (r["function"] or "").lower()
    if r["blocking_effect"] != "undetermined" and r["basis"] != "vendor-documented":
        check("variety of uses" not in fn,
              f"{r['token']}: classified {r['blocking_effect']} from mixed-purpose text")

# 5. The honest_limitation sentence must state the real undetermined count. A stale
# number here would be the dataset lying about its own coverage.
und = sum(1 for r in ROWS if r["blocking_effect"] == "undetermined")
check(f"{und} of {len(ROWS)}" in D["honest_limitation"],
      f"honest_limitation is stale: {und} of {len(ROWS)} undetermined, text says "
      f"{D['honest_limitation'][:40]!r}")
check(D["summary"]["undetermined"] == und, "summary.undetermined disagrees with rows")

# 6. Attribution to the upstream MIT source must be present. Removing it would make
# this a licence violation, not merely impolite.
src = json.dumps(D["sources"])
check("ai-robots-txt" in src and "MIT" in src, "upstream MIT attribution missing")

# 7. No case-insensitive duplicate tokens. robots.txt matches user-agents
# case-insensitively, so Meta-ExternalAgent and meta-externalagent are one crawler;
# upstream lists both, and emitting both inflates every count a consumer derives here.
import collections
dupes = {k: v for k, v in
         collections.Counter(r["token"].lower() for r in ROWS).items() if v > 1}
check(not dupes, f"case-insensitive duplicate tokens: {sorted(dupes)}")

# 8. The vendor-documented row count must equal the registry exactly. More means the
# dedupe let a case variant through; fewer means a sourced fact was dropped.
check(sum(1 for r in ROWS if r["basis"] == "vendor-documented") == len(ours),
      f"{sum(1 for r in ROWS if r['basis']=='vendor-documented')} vendor-documented rows "
      f"vs {len(ours)} in crawlers.json")

if fails:
    print(f"FAIL ({len(fails)}):")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print(f"crawler-consequences.json OK — {len(ROWS)} tokens, {und} honestly undetermined, "
      f"{len(ROWS)-und} determined")
