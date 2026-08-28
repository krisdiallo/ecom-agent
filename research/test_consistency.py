#!/usr/bin/env python3
"""The CLI hardcodes its bot lists so it stays a single dependency-free file.
That means it can silently drift from crawlers.json. This fails if it does."""
import json, re, sys

reg = json.load(open("crawlers.json"))["crawlers"]
src = open("aivis.py").read()


def block(name):
    m = re.search(name + r"\s*=\s*\[(.*?)\n\]", src, re.S)
    return set(re.findall(r'\("([^"]+)"', m.group(1)))


cli_search, cli_train = block("SEARCH_BOTS"), block("TRAIN_BOTS")
reg_search = {c["token"] for c in reg if c["blocking_effect"] == "removes_from_ai_answers"}
reg_train = {c["token"] for c in reg if c["blocking_effect"] == "opts_out_of_training_only"}

fail = False
# The CLI deliberately omits Googlebot/Amazonbot from its AI-search list (they are
# conventional search, checked elsewhere), so registry ⊇ CLI is the invariant.
for label, cli, regset in (("search", cli_search, reg_search), ("training", cli_train, reg_train)):
    extra = cli - regset
    if extra:
        print(f"FAIL: {label} tokens in CLI but not classified that way in registry: {sorted(extra)}")
        fail = True
    else:
        print(f"ok: all {len(cli)} CLI {label} tokens agree with crawlers.json")

for c in reg:
    if "source_quote" not in c and "verification" not in c:
        print(f"FAIL: {c['token']} has neither a source quote nor a verification flag")
        fail = True
    if "verified" not in c:
        print(f"FAIL: {c['token']} has no verified date")
        fail = True
print("ok: every registry entry is either quoted or explicitly flagged unverified")
sys.exit(1 if fail else 0)
