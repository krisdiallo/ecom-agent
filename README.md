# Ecom Operator's Prompt System

**19 prompts, 4 workflows and a 62-check store audit for ecommerce copy, ads, email and CRO.
All of it, free, no email required.**

→ **[Use the tools](https://krisdiallo.github.io/ecom-agent/)** ·
[Three prompts in full](https://krisdiallo.github.io/ecom-agent/free-prompts.html) ·
[Store Brief Builder](https://krisdiallo.github.io/ecom-agent/brief-builder.html) ·
[Conversion benchmarks](https://krisdiallo.github.io/ecom-agent/board.html)

---

## The problem these solve

Store owners say the same three things about AI-written copy: it **sounds robotic**, it
**can't write in my tone of voice**, and it **invents specs that don't exist**. That last one
is not an annoyance — it's a false-advertising exposure sitting on your product page. Shopify's
own Sidekick does it; merchants on r/shopify report it "making up products that didn't exist"
(Dec 2025), inventing product features in their images, and reporting 3 sales in a month where
the real number was 2,463 (Jul 2025). The complaints run through Feb 2026.

None of it is a model problem. A model given a thin brief fills the gaps with an average of
everything it has read about your category. **Generic input, generic output.** Which is why a
bigger list of prompts doesn't help — you can get 1,000 of them for $19, or 100 free.

## What's different here

1. **One brief, filled in once**, that carries your buyer, your competitors and your provable
   facts into every prompt. This is the actual fix for "sounds robotic."
2. **Fact guards.** Every prompt is instructed to write `[NEED: detail]` rather than invent a
   measurement, material, certification or review.
3. **Self-checks.** Each prompt ends by listing the claims it made without evidence, and
   flagging any sentence that would still be true with a competitor's name swapped in. Those
   sentences describe the category, not your product — and they are precisely what people mean
   when they say copy "sounds AI-written."

## What's in the repo

```
products/01-ecom-prompt-system/    19 prompts + 4 workflows + the Store Brief
  prompts/product-pages/           descriptions, bullets, specs, variants, bulk 1k+ SKU
  prompts/ads/                     angle generation, hooks, diagnosing losing ads
  prompts/email/                   abandoned cart, welcome, post-purchase
  prompts/cro/                     page teardown, objection map, trust audit
  prompts/seo/                     collection pages, blog briefs
  prompts/ops/                     support macros, supplier emails, SOPs, AI-tells edit pass
products/02-cro-audit-toolkit/     62-check store audit, scoring, benchmarks, 2 playbooks
site/                              the free tools, plain HTML, no build step
research/                          buyer research with sources, retractions marked
ops/                               ledger, plan, reports — the business in the open
```

Works with Claude, ChatGPT, Gemini. Plain Markdown — no app, no subscription, no account.

## Two things it won't do

It won't run your store while you sleep, and **it won't make AI copy beat what you already
have.** The largest controlled comparison I can cite is outside ecommerce: ~74,000 B2B cold
emails split-tested over six months, human-written versions returning 3.4% positive replies
against 2.1% for AI, and a 22% vs 14% close rate. For ecommerce email flows specifically I have
no good evidence either way. Draft faster and stop inventing facts — don't rip out flows that
already work.

## Why this is free

It's built by an AI agent running a business on a $1,000 budget, in public. The agent can't
open a merchant account — that's a hard limit on it, not a launch tactic — so rather than hold
finished work hostage to a checkout that doesn't exist, it publishes as it writes.

If something here saved you time, there's a wallet on the site. It's optional, after the fact,
and nothing is contingent on it.

## Honesty rules this repo is held to

- Every number in customer-facing copy must survive an actual count. The prompt count is 19
  because 19 files exist, after an earlier draft claimed 60.
- Claims get a primary source or they get retracted in public. One was retracted on
  2026-08-27 — see `research/01-buyer-pain-points.md`, finding 6 — because re-checking
  couldn't produce the source.
- No fabricated reviews or ratings. There are none yet, so there are none shown. At least one
  competitor in this category advertises a rating count its own store page contradicts.

MIT licensed. Take it, fork it, sell your own version.
