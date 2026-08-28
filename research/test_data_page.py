#!/usr/bin/env python3
"""Contract tests for site/data.html.

This page exists to be read by machines — Google Dataset Search and any crawler that
consumes schema.org/Dataset. A broken contentUrl or a description under the 50-character
minimum makes it silently ineligible, with no visible symptom on the page itself. That
is the same failure class the whole project is about, so it gets a test.

Network checks are skipped when offline so CI stays deterministic; the structural
checks always run.
"""
import json, os, re, sys, urllib.request, urllib.error

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
page = open(os.path.join(HERE, "site", "data.html")).read()
fails = []


def check(c, m):
    if not c:
        fails.append(m)


blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
check(len(blocks) == 1, f"expected exactly 1 JSON-LD block, found {len(blocks)}")
cat = json.loads(blocks[0]) if blocks else {}

check(cat.get("@type") == "DataCatalog", f"catalog @type is {cat.get('@type')!r}")
sets = cat.get("dataset", [])
check(len(sets) == 4, f"expected 4 datasets, found {len(sets)}")

for ds in sets:
    sid = (ds.get("@id") or "?").split("#")[-1]
    # Google's two hard requirements. Under 50 chars and the dataset is not eligible.
    check(ds.get("@type") == "Dataset", f"{sid}: @type is {ds.get('@type')!r}")
    check(bool(ds.get("name")), f"{sid}: no name")
    d = ds.get("description", "")
    check(50 <= len(d) <= 5000, f"{sid}: description is {len(d)} chars, must be 50-5000")
    dist = ds.get("distribution") or []
    check(bool(dist), f"{sid}: no distribution")
    if dist:
        check(bool(dist[0].get("contentUrl")), f"{sid}: distribution has no contentUrl")
        check(bool(dist[0].get("encodingFormat")), f"{sid}: distribution has no encodingFormat")
    check(bool(ds.get("license")), f"{sid}: no license")

# Record counts printed on the page must match the real files. The page is generated
# from them, so a mismatch means the page was hand-edited or the generator drifted.
def n_json(p, key=None):
    d = json.load(open(os.path.join(HERE, p)))
    return len(d[key]) if key else len(d)


expect = {
    "crawler-consequences.json": n_json("crawler-consequences.json", "crawlers"),
    "crawlers.json": n_json("crawlers.json", "crawlers"),
    "agent-commerce.json": n_json("agent-commerce.json", "hosts"),
    "research/data/survey-2026-08-28.json": n_json("research/data/survey-2026-08-28.json"),
}
for f, n in expect.items():
    check(f"{n} records" in page or f">{n} records<" in page or f"<strong>{n} records</strong>" in page,
          f"page does not state {n} records for {f}")

# Every contentUrl must actually resolve. A Dataset pointing at a 404 is worse than no
# markup: it advertises data that is not there.
if os.environ.get("SKIP_NET") != "1":
    for ds in sets:
        sid = (ds.get("@id") or "?").split("#")[-1]
        url = (ds.get("distribution") or [{}])[0].get("contentUrl")
        if not url:
            continue
        try:
            req = urllib.request.Request(url, method="HEAD",
                                         headers={"User-Agent": "aivis-test"})
            code = urllib.request.urlopen(req, timeout=25).status
            check(code == 200, f"{sid}: contentUrl returned HTTP {code}")
        except urllib.error.HTTPError as e:
            fails.append(f"{sid}: contentUrl returned HTTP {e.code}")
        except Exception as e:
            print(f"  (skipped network check for {sid}: {e})")

if fails:
    print(f"FAIL ({len(fails)}):")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print(f"data.html OK — DataCatalog with {len(sets)} datasets, all required fields present")
