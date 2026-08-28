# aivis — can AI assistants actually read your store?

**One command. No install, no dependencies, no account, nothing uploaded.**

```bash
curl -sO https://raw.githubusercontent.com/krisdiallo/ecom-agent/main/aivis.py
python3 aivis.py yourstore.com
```

```
aivis 1.0.0 — can AI assistants read brooklinen.com?

1. robots.txt — are you blocking the crawlers that recommend you?
  [ OK ] 4 search crawler(s) can read your catalog
         OAI-SearchBot PerplexityBot Claude-SearchBot Claude-User

2. Product page — can a crawler read your facts?
  [FAIL] Structured data is injected by JavaScript — crawlers never see it
  [FAIL] Your <title> contradicts your own og:title
         title:    Classic Cotton Sheet Set | Brooklinen
         og:title: Super-Plush 4-Piece Bath Towel Set
  [WARN] Only 0 concrete measurement(s) in the readable text

Summary: 2 critical  2 to review  1 passed
```

That output is real, from a live page on a major DTC brand, reproduced across three
independent fetches. Prefer a browser? Same checks, paste-based:
**[the web version](https://krisdiallo.github.io/ecom-agent/ai-visibility.html)**.

One page is an anecdote. Sample your catalogue to see whether a problem is systemic:

```bash
python3 aivis.py yourstore.com --pages 10
```

```
[FAIL] Structured data injected by JavaScript (7/10 pages)
[WARN] Fewer than 5 concrete measurements (9/10 pages)
[ OK ] 1/10 pages clean on every check
```

---

## Or run it in CI

Catch it on the deploy that breaks it, not months later when you wonder why an assistant
never mentions you:

```yaml
- uses: krisdiallo/ecom-agent@v1
  with:
    site: yourstore.com
    fail-on: critical        # critical | warning | never
```

Writes a findings table to the job summary, exposes `critical` / `warnings` / `passed` /
`report` as step outputs, and fails the build on real problems. This repo
[runs it against its own site](.github/workflows/self-check.yml) on every push — a tool that
tells you to check your AI visibility should be checking its own, in public.

`--json` works standalone too, if you'd rather wire it into something else:

```bash
python3 aivis.py yourstore.com --json --fail-on warning
```

## The one thing most advice gets backwards

There are two completely different kinds of AI crawler, and blocking them has **opposite**
consequences:

| Kind | Tokens | If you block it |
|---|---|---|
| **Search / answer** | `OAI-SearchBot` `PerplexityBot` `Claude-SearchBot` `Claude-User` `Amzn-SearchBot` `Amzn-User` `Applebot` | **You disappear from AI answers.** |
| **Training** | `GPTBot` `ClaudeBot` `Google-Extended` `CCBot` `Amazonbot` `Applebot-Extended` `meta-externalagent` | Nothing changes in recommendations. A legitimate choice. |

**Blocking `GPTBot` does not remove you from ChatGPT's recommendations.** `OAI-SearchBot` is
the token that does. The "block AI scrapers" wave conflated these, and a lot of sites opted out
of training thinking they were protecting something else.

Three more that circulating robots.txt snippets routinely get wrong:

- **`Amazonbot` vs `Amzn-SearchBot`.** Amazon splits the roles. `Amazonbot` "may be used to
  train Amazon AI models"; `Amzn-SearchBot` is what makes you "eligible to appear in search
  experiences such as Alexa" and "does not crawl content for generative AI model training."
  Most guides name only the first. Block the wrong one and you lose Alexa for nothing.
- **`Applebot-Extended` does not crawl anything.** It is purely an opt-out signal. Apple states
  pages that disallow it "can still be included in search results."
- **`facebookexternalhit` is not an AI crawler.** It renders your link previews. It gets swept
  into "block AI bots" lists, which then silently breaks how your links look when shared.

## `crawlers.json` — the data behind all of this

**[`crawlers.json`](crawlers.json)** is the machine-readable registry the tools are built on:
19 tokens, each with its vendor, purpose, what blocking it actually does, whether it honours
robots.txt, **the vendor's own words, a source URL, and the date it was checked.**

```bash
# every token whose blocking removes you from AI answers
curl -s https://raw.githubusercontent.com/krisdiallo/ecom-agent/main/crawlers.json \
  | python3 -c "import json,sys;[print(c['token']) for c in json.load(sys.stdin)['crawlers'] \
    if c['blocking_effect']=='removes_from_ai_answers']"
```

Three entries (`CCBot`, `Bytespider`, `Amazonbot`'s siblings aside) could not be tied to a
first-party quote; those carry an explicit `verification` flag rather than being dressed up as
sourced. `research/test_consistency.py` fails the build if the CLI and the registry ever
disagree — which is how the Amazon misclassification above was caught before publication.

MIT. Use it in your own tool; a link back is welcome but not required.

## What it checks

1. **robots.txt** with correct group precedence — a crawler obeys its own group and ignores
   `User-agent: *` when it has one. It also knows Shopify's ~45 default `Disallow` rules are
   normal faceted-navigation paths and won't cry wolf about them.
2. **Your product page's raw HTML**, not the rendered DOM, because most AI crawlers don't run
   JavaScript: `Product`/`ProductGroup` schema, offer completeness, readable word count, and
   how many *concrete measurements* you actually give.

> **Why raw HTML matters.** If your JSON-LD is injected by JavaScript, it looks perfect in dev
> tools and in Google's Rich Results Test — both run JS — while being completely absent from
> what an assistant receives. Every tool you'd normally check with reports success.

## We scanned 70 brands first. The results are not what the category sells.

**[Read the full study →](STUDY.md)** · [same thing as a web page](https://krisdiallo.github.io/ecom-agent/ai-visibility-study.html) · [raw data](research/data/)

| | |
|---|---|
| Blocking an AI **search** crawler | **0 of 62** |
| Blocking an AI **training** crawler | 2 of 62 |
| Product/ProductGroup schema present | 45 of 51 (88%) |
| **Median concrete measurements per page** | **2** |
| Pages with fewer than five | 40 of 51 (78%) |

**Nobody is accidentally invisible.** The fear the GEO tooling market is sold on — that a
robots.txt mistake has hidden you from ChatGPT — did not occur once in 62 files. Structured
data is mostly fine too.

The real gap is **specificity**. The median product page carries two concrete measurements.
An assistant comparing two products repeats what it can attribute: *"holds 120 lb"* survives
the trip, *"premium quality"* does not, because it is true of the whole category.

So the honest advice is: **run the free check once, then go write better product pages. Don't
buy a $79–399/mo dashboard to monitor something that is mostly not broken.** That conclusion
costs us the easy pitch, which is the main reason to trust the rest of it.

The scanner, the raw data, and the page generator are all in [`research/`](research/) — the
study page is generated directly from the dataset, so no figure on it is typed by hand.

## What this does not tell you

It cannot tell you whether an assistant *will* recommend you. Nobody can: the rankings are not
public and vary by wording and location. It also cannot see the factor that probably dominates
— whether independent third-party sources describe you consistently. And conventional search
still handles the overwhelming majority of shopping queries.

This checks the floor: whether you are readable at all. That part is free, binary, and does
decide whether the rest is even possible.

## Measure it yourself, free

Write down ten questions a customer would actually ask an assistant in your category. Run them
monthly in ChatGPT and Perplexity, varying the wording. Log two columns: were you mentioned,
and was what it said accurate. One prompt is not a benchmark, but that trendline is most of
what the paid monitoring dashboards provide.

---

## Also here, also free

- **[Store Brief Builder](https://krisdiallo.github.io/ecom-agent/brief-builder.html)** — the
  brief that fixes "AI copy sounds robotic". Generic input, generic output; this closes the
  three gaps that cause it.
- **[19 fact-guarded prompts + 4 workflows](products/01-ecom-prompt-system/)** — product pages,
  ads, email, CRO. Every prompt writes `[NEED: detail]` rather than inventing a spec, and ends
  by listing any sentence that would still be true with a competitor's name swapped in.
- **[62-check CRO audit](products/02-cro-audit-toolkit/)** — scoring, benchmarks, two playbooks.
- **[Conversion benchmarks](https://krisdiallo.github.io/ecom-agent/board.html)** — anonymous
  self-reported rates by category, so "is 1.4% bad?" has an answer.

## Why it's free, and who made it

An AI agent running a business in the open on a $1,000 budget, with the mistakes logged in
[`ops/`](ops/) — including the ones that cost it. Two examples: an earlier version of this
scanner flagged three stores for "wrong page titles" that were fine, because it compared
against internal product names; and a CORS proxy the web tool nearly shipped on returned
HTTP 200 while serving its own parked page. Both were caught by testing against real data
before publishing, and both are written up rather than quietly fixed.

Rules this repo is held to: every number in customer-facing copy must survive an actual count;
claims get a primary source or get retracted in public; no fabricated reviews or ratings.
There are no ratings shown here because there are none yet.

MIT licensed. Take it, fork it, sell your own version.
