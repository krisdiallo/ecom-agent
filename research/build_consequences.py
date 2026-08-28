#!/usr/bin/env python3
"""Build crawler-consequences.json: every known AI crawler, classified by what
blocking it actually costs you.

Two sources, deliberately kept distinct in the output:

  1. crawlers.json — our own registry. 21 tokens, each quoted from the vendor's own
     documentation with the date checked. Authoritative; always wins.
  2. ai-robots-txt/ai.robots.txt — the ecosystem's list of AI user-agents, MIT
     licensed, ~166 entries. Far broader than ours on WHICH bots exist. Their FAQ
     explicitly invites this use: "Can I use robots.json directly in my own tooling?
     You're welcome to."

Their `function` field is free text, so a consequence can only be derived where the
wording is unambiguous. Everything else is marked `undetermined` rather than guessed.
That is not laziness: defaulting an unrecognised crawler to "training" would recreate
precisely the conflation this project exists to correct, and would do it silently
across a hundred tokens.

Usage: python3 research/build_consequences.py <path-to-their-robots.json>
"""
import json, re, sys, os, collections, urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPSTREAM = ("https://raw.githubusercontent.com/ai-robots-txt/ai.robots.txt/"
            "main/robots.json")

# Three tiers, weakest last, and a hard veto in front of all of them.
#
# MIXED vetoes everything. "Scrapes data for a variety of uses including training AI"
# says the opposite of "training only" — the crawler does other things too, and which
# of those things costs you visibility is precisely what is not stated. An earlier
# version of this file read that sentence as training-only and mislabelled Scrapy and
# Sidetrade. Bare "Scrapes data." is vetoed for the same reason: it establishes that
# something is fetched, not what for. That one wrongly labelled all three GoogleOther
# variants as training-only, which is a guess dressed as a finding.
MIXED = re.compile(r"variety of uses|\bincluding\b|and machine learning|"
                   r"^scrapes? data\.?$|^data scraper", re.I)

# Tier 1: the vendor's purpose is stated outright in the text.
SEARCH_EXPLICIT = re.compile(r"search result generation|collects data for ai search|"
                             r"index.*(answer|search)", re.I)
TRAIN_EXPLICIT = re.compile(r"\btrain(s|ing|ed)?\b|foundation model", re.I)

# Tier 2: upstream's own curated category. Weaker than a purpose sentence — it is their
# editorial judgement, not the vendor's words — so it is recorded under its own basis
# rather than being laundered into the same confidence as tier 1.
SEARCH_CATEGORY = re.compile(r"^ai search crawlers?$", re.I)
TRAIN_CATEGORY = re.compile(r"^ai data scrapers?$", re.I)


def load_upstream(path=None):
    if path:
        return json.load(open(path))
    with urllib.request.urlopen(UPSTREAM, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def build(upstream):
    ours = {c["token"].lower(): c for c in
            json.load(open(os.path.join(HERE, "crawlers.json")))["crawlers"]}
    rows, counts = [], collections.Counter()
    for token, e in sorted(upstream.items(), key=lambda kv: kv[0].lower()):
        fn = (e.get("function") or "").strip()
        known = ours.get(token.lower())
        if known:
            eff, basis = known["blocking_effect"], "vendor-documented"
        elif MIXED.search(fn):
            eff, basis = "undetermined", "source-describes-mixed-or-unstated-purpose"
        elif SEARCH_EXPLICIT.search(fn):
            eff, basis = "removes_from_ai_answers", "explicit-purpose-text"
        elif TRAIN_EXPLICIT.search(fn):
            eff, basis = "opts_out_of_training_only", "explicit-purpose-text"
        elif SEARCH_CATEGORY.search(fn):
            eff, basis = "removes_from_ai_answers", "upstream-category"
        elif TRAIN_CATEGORY.search(fn):
            eff, basis = "opts_out_of_training_only", "upstream-category"
        else:
            eff, basis = "undetermined", "source-does-not-establish-consequence"
        counts[eff] += 1
        rows.append({"token": token, "operator": e.get("operator") or None,
                     "function": fn or None, "blocking_effect": eff, "basis": basis})
    # every vendor-documented token of ours must survive into the output unchanged
    for t, c in ours.items():
        if not any(r["token"].lower() == t for r in rows):
            rows.append({"token": c["token"], "operator": c.get("vendor"),
                         "function": c.get("product"),
                         "blocking_effect": c["blocking_effect"],
                         "basis": "vendor-documented"})
            counts[c["blocking_effect"]] += 1

    # Upstream lists some crawlers under two spellings (Meta-ExternalAgent and
    # meta-externalagent). robots.txt matches user-agents case-insensitively, so those
    # are one crawler, and emitting both would inflate every count a consumer derives
    # from this file. Prefer our registry's canonical casing where we have it.
    canon = {t: c["token"] for t, c in ours.items()}
    seen, deduped, merged = {}, [], 0
    for r in rows:
        k = r["token"].lower()
        if k in seen:
            merged += 1
            continue
        seen[k] = True
        r["token"] = canon.get(k, r["token"])
        deduped.append(r)
    if merged:
        counts.clear()
        for r in deduped:
            counts[r["blocking_effect"]] += 1
    deduped.sort(key=lambda r: (r["blocking_effect"], r["token"].lower()))
    return deduped, counts


def main():
    upstream = load_upstream(sys.argv[1] if len(sys.argv) > 1 else None)
    rows, counts = build(upstream)
    doc = {
        "name": "crawler-consequences",
        "version": "1.0.0",
        "generated": "2026-08-28",
        "license": "MIT",
        "about": ("Every known AI crawler, classified by what blocking it actually costs. "
                  "The useful question is not 'is this an AI bot' but 'what do I lose by "
                  "disallowing it' — blocking a training crawler costs nothing in "
                  "recommendations, blocking a search crawler removes you from AI answers."),
        "sources": [
            {"name": "krisdiallo/ecom-agent crawlers.json",
             "role": "authoritative; each token quoted from vendor documentation with a "
                     "checked date",
             "url": "https://github.com/krisdiallo/ecom-agent/blob/main/crawlers.json"},
            {"name": "ai-robots-txt/ai.robots.txt robots.json",
             "role": "coverage of which AI user-agents exist; free-text function field",
             "license": "MIT", "url": "https://github.com/ai-robots-txt/ai.robots.txt",
             "note": "Used with their explicit permission in FAQ.md: 'Can I use robots.json "
                     "directly in my own tooling? You're welcome to.'"},
        ],
        "honest_limitation": (
            f"{counts['undetermined']} of {sum(counts.values())} tokens are `undetermined`. "
            "For those, the available source text does not establish whether blocking costs "
            "you AI visibility. They are NOT defaulted to 'training' — that guess would be "
            "wrong roughly as often as it was right, and silently."),
        "summary": dict(counts),
        "crawlers": rows,
    }
    out = os.path.join(HERE, "crawler-consequences.json")
    json.dump(doc, open(out, "w"), indent=1)
    open(out, "a").write("\n")
    print(f"wrote {out}: {sum(counts.values())} tokens")
    for k, v in counts.most_common():
        print(f"  {v:>3}  {k}")


if __name__ == "__main__":
    main()
