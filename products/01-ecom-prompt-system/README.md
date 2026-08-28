# The Ecom Operator's Prompt System

**19 tested prompts + 4 workflows for running a store's copy, ads, email, and CRO with AI.**

Not a list of prompts. A system: every prompt takes structured inputs, states its assumptions,
and ends with a self-check that catches the specific way AI output fails for ecommerce
(invented specs, fake reviews, unsupported claims, generic "elevate your everyday" filler).

## What's inside
- `prompts/product-pages/` — descriptions, bullets, spec tables, variant copy, A+ content
- `prompts/ads/` — Meta/Google/TikTok hooks, angles, iteration on losers
- `prompts/email/` — welcome, abandoned cart, post-purchase, winback flows
- `prompts/cro/` — page teardown, objection mapping, trust-signal audit
- `prompts/seo/` — collection pages, category copy, schema, internal links
- `prompts/ops/` — support macros, supplier emails, returns policy, SOPs
- `WORKFLOWS.md` — chains that connect prompts into a full job (e.g. "launch a new product")
- `INPUTS.md` — the store brief you fill in once and paste into any prompt

## How to use it
1. Fill in `INPUTS.md` once. It's the context every prompt expects.
2. Pick the prompt for the job. Paste your brief where marked.
3. Run the self-check block at the bottom. It is the part that makes output usable.

Works with Claude, ChatGPT, Gemini — any model. No subscription, no tool lock-in.
