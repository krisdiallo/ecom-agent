# Directory submissions — prepared, not posted

These are awesome-lists where this repo fills a documented gap and the list explicitly
invites submissions. I prepared the issue/PR text so posting is a copy-paste action, but
I did not post any of them, because each would be authored as `krisdiallo` and is an
outward-facing promotional action that requires your decision.

## Why I didn't post these myself

Every path to a first visitor requires either time (organic discovery at ~1–2 people/month
per the measured base rate) or an outward-facing action from a real identity. I can't
manufacture the first, and the second requires your account. An awesome-list PR or issue
is the *least* promotional form of this — it's a suggestion to a maintainer who decides,
not a community post — but it is still you publicly asking someone to list your product.

If you want to post any of these, each is ready below. If you'd rather not, the search-
ranking work already done (description rewrite, README term coverage, topics) means the
lists' maintainers may find this on their own when curating.

---

## 1. amplifying-ai/awesome-generative-engine-optimization (491★)

**Channel:** Open an issue (the list accepts suggestions this way — see issues #117, #115,
#113, #97 for the pattern).

**Gap:** The "Tools & Software" section lists ~15 paid SaaS platforms (SEMrush $99/mo,
Otterly.AI, GeckoCheck, etc.) and no free, open-source, primary-data tool.

**Title:** `Tool suggestion: aivis — free, open-source AI visibility checker for ecommerce (robots.txt + raw-HTML schema)`

**Body:**

> Suggesting [krisdiallo/ecom-agent](https://github.com/krisdiallo/ecom-agent) for the Tools & Software section.
>
> It's a free, zero-dependency CLI (and MCP server) that checks the two things that decide whether an AI answer engine can read an ecommerce store at all:
>
> 1. **robots.txt** — correctly classifies 165 AI crawler user-agents by what blocking each one actually costs (removes you from AI answers vs. opts out of training only), with vendor-sourced evidence per entry. The key correction it carries: blocking `GPTBot` does not remove you from ChatGPT's recommendations — `OAI-SearchBot` is the token that does.
> 2. **Product page raw HTML** — structured data, offer completeness, and concrete-measurement count, checked against what a crawler that doesn't run JavaScript receives (not the rendered DOM).
>
> It comes with four open datasets: the 165-crawler consequence registry, a 21-entry vendor-sourced crawler registry, a 70-storefront agent-commerce survey, and a 70-brand AI visibility survey. All MIT.
>
> The "Dedicated GEO Platforms" section currently has only paid SaaS. This would be the first free, open-source, primary-data tool in the list. It's also ecommerce-specific, which is a niche none of the current entries address.
>
> Happy to adjust the description to match the list's format.

---

## 2. alternbits/awesome-ai-visibility (21★)

**Channel:** PR (contributing guide says "send us a Pull Request") or issue.

**Gap:** The "Open-Source Tools" section has two entries — both are prompt-based visibility
trackers (run queries against ChatGPT/Claude, log results). Neither checks whether crawlers
can read the store at the mechanical level.

**Suggested addition to the "Open-Source Tools" section:**

> - [**aivis**](https://github.com/krisdiallo/ecom-agent) — Free, zero-dependency CLI and MCP server that checks whether AI crawlers can read an ecommerce store at all: robots.txt AI-crawler classification (165 tokens, vendor-sourced, split by what blocking costs — answers vs. training), and product-page structured data in raw HTML rather than the rendered DOM. Includes open datasets: a 70-brand visibility survey and a 165-crawler consequence registry. The complement to prompt-based trackers — it checks the floor that decides whether there's anything to track.

---

## 3. Illyism/awesome-ai-seo-llmo (4★)

Smaller list, same category. A PR adding to the tools section would fit.

---

## What I did instead of posting

Made the repo the obvious inclusion for anyone curating these lists independently:
- Description rewritten to match real search intent (moved `OAI-SearchBot` from unranked to #4)
- README now covers GEO, generative engine optimization, LLM SEO, answer engine optimization — the terms curators search
- `topic:oai-searchbot` — #2 of 4; `topic:gptbot` — #1 of 64

If a maintainer scans the category, this is now findable. That's the passive path; the issues above are the active one.
