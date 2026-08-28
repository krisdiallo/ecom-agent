# Business plan v0 — 2026-08-27

## Thesis
Sell digital products I can produce end-to-end (toolkits, templates, prompt+workflow packs) to ecommerce store owners, a buyer group that (a) already spends money on tools, (b) searches for exactly these problems, (c) buys $19–39 impulse products. Zero COGS, zero ad spend until organic sales prove a product converts.

## Why this beats the alternatives with $1k
- Productized services scale with a human's time. Physical ecom burns cash on ads/inventory before learning anything.
- Digital: the only cost of a failed product is my time. Cash can't hit $0 from one bad week.

## Stack (all $0 fixed until revenue)
- Storefront + checkout: Gumroad (Product API for programmatic listing; Discover marketplace = free organic traffic). Revisit Lemon Squeezy (5%+$0.50) once >$500/mo revenue makes fee difference matter.
- Site: static (GitHub Pages/Cloudflare Pages, $0). Domain ~$12, the only planned spend.
- Traffic: SEO landing pages + free micro-tools (engineering-as-marketing) + Gumroad Discover. No paid ads until ≥3 organic sales on a product.

## Milestones
1. Wk 1: Product #1 live on Gumroad, 1 landing page, 2 free tools published.
2. Wk 2–4: 3 products live, first $100 revenue. Kill any product with 0 sales after 200 page visits.
3. Month 2–3: $500/mo. Then, and only then, test $100 of ads on the best converter.

## Product pipeline (ordered)
1. **Ecom Copy & Ops Prompt System** ($29) — 19 tested prompts + 4 workflows for product descriptions, ad copy, email flows, CRO audits; structured as a Notion + Markdown kit. Fast to build, matches proven demand.
2. **Store CRO Audit Toolkit** ($39) — checklist + scoring sheet + fix playbooks.
3. **Email Flow Pack for Shopify** ($29) — welcome/abandon/post-purchase sequences.

## Kill criteria / honesty rules
- Every dollar logged in ops/LEDGER.md before spend.
- Weekly report in ops/reports/ with real numbers, including zeros.
- If 3 products fail the 200-visit test → pivot to productized service (Plan B).

## Price decision (2026-08-27)
Listed at $29 with 19 prompts + 4 workflows, not 60 prompts. Rationale: the count was
aspirational marketing, and shipping an inflated number in a product whose entire pitch is
"AI copy makes claims it can't support" would be self-refuting — and refund-generating.
19 prompts that each survive their own self-check are worth more than 60 padded ones, and
$29 is defensible for them. The catalogue grows with free updates, which is a real reason
to buy early rather than a manufactured one.

---

# Plan v1 — 2026-08-27, after the traffic research came back

## What v0 got wrong

**v0's traffic strategy is falsified.** It said: "SEO landing pages + free micro-tools +
Gumroad Discover." Measured against evidence rather than intuition:

- **96.55% of all pages get zero Google organic traffic.** Only 1.94% get 1–10 visits/month.
  (Ahrefs SEO statistics, fetched live.)
- **Only 5.7% of new pages rank top-10 within a year**, and those sit on aged authority
  domains. 72.9% of top-10 pages are over three years old.
- Realistic organic traffic here in 90 days: **0–20 visits/month on long-tail queries that
  don't convert.** A custom domain does not change this at the 90-day mark.
- Gumroad Discover is weak: the only rated pack in the competitive set is a *free* one.

**Decision: stop writing SEO content.** The technical foundation (sitemap, robots, meta,
canonical, IndexNow) is done and was cheap — keep it, it costs nothing to maintain. But
producing more pages on the hope of ranking is spending the one resource I have, effort, on a
channel that returns zero inside any horizon that matters. Treat SEO as 9–18 months, not 90 days.

Milestone 2 in v0 ("first $100 revenue, wk 2–4") assumed traffic that will not exist. It is
not a stretch goal, it is arithmetic that doesn't close. Removed rather than left to rot.

## The finding that changes the thesis

The AI-copy incumbents have **left the Shopify app ecosystem**. Verified live, 2026-08-27:

| Product | Shopify App Store | Reviews |
|---|---|---|
| Jasper, Writesonic, Rytr | no listing (404) | — |
| Anyword, Copy.ai | **delisted** | — |
| Brand Echo (current entrant) | live | **1 review, 1 install** |
| Gumroad prompt packs ($7.99–$29.99) | n/a | **0 across the board** |

Writesonic has repositioned entirely to GEO/AI-search at $79–$399/mo. The item-level tier is
now micro-apps with single-digit installs and prompt packs with no reviews, while merchant
demand is loud and current (Feb and Apr 2026 complaint threads).

**Demand is strong and supply is weak.** That is a real opening. It is also not one I can walk
through alone, because it needs a listing, which needs an account.

## What actually drives traction (verified)

Not virality — **keyword capture**. Ahrefs' free tools rank #1 for the purchase-intent term
itself ("free backlink checker"); Klaviyo pairs a free generator with annual benchmark reports
that earn links. Both are multi-month plays on domains that already have authority.

The near-term lane: **answering inside live merchant complaint threads.** Communities
auto-remove self-promotion — verified from AutoModerator messages in the fetched threads — so
this only works as genuine help, from a real participant, linking only where it's responsive.
That is an account-holder action. It is not available to me.

Negative control worth remembering: a Reddit-app launch post in r/sideproject (Apr 2026) →
"I currently have exactly 1 active install."

## Honest position

Every remaining growth lever needs a human: a marketplace listing needs an account, community
answering needs an account and a reputation, ads need money and an account. I have taken this
as far as it goes without one. What I can still do is make the human step as small as possible
and keep the product worth finding when someone does arrive.

## Revised milestones
1. ~~First $100 by wk 4~~ — arithmetic doesn't close at 0 traffic. Removed.
2. First **visitor**, then first **10**. Distribution, not revenue, is the metric that matters
   now; revenue is downstream of a number that is currently zero.
3. Kill criterion, restated honestly: a product with 0 sales after 200 visits is dead. **No
   product has had 200 visits.** Nothing has been tested yet. Do not conclude the products
   failed — they have not been shown to anyone.

---

# Plan v2 — 2026-08-28

## What v1 got wrong

v1 concluded: *"Every remaining growth lever needs a human... I have taken this as far as it
goes without one."* Two of the three premises behind that were wrong.

**1. The payment block was never a category, only four platforms.** See `ops/LEDGER.md`,
2026-08-28. A verified merchant account with live rails was available the whole time. Revenue is
no longer structurally impossible; it is one owner decision away.

**2. The product was in a category with demonstrated zero demand, and v1 had the evidence.**
v1 recorded "0 reviews across the board" on competing prompt packs and read it as weak supply.
It is at least as consistent with no demand — and against zero traffic, nothing distinguishes
them. We were spending effort on the optimistic reading of our own disconfirming data.

v1's traffic research still stands and is not revisited: SEO on a `github.io` subdomain returns
nothing inside 90 days. Do not write content on faith.

## Revised thesis

Sell (or give away) **diagnostics for problems store owners can't see themselves**, in a
category where the anxiety is current and the incumbents charge subscription prices.

Prompt packs are commodity supply: 1,000 for $19, 100 free, zero reviews anywhere. An
AI-visibility diagnostic is not: it is personalised, it produces a result worth screenshotting,
and it is the thing merchants are actively asking about in the target community *this month*.
Writesonic repositioned its whole business to this at $79–399/mo, which is a costly signal about
where the money is.

## What is verified, and what is not

Verified today, first-hand:
- Perplexity returns only large incumbents for a category shopping query (merino base layers →
  REI, Smartwool, Icebreaker, Amazon, Alpinetrek).
- Two live r/shopify threads, 35 comments, including an agency saying manual prompt testing
  "doesn't scale" and paid tools already being named.
- The crawler taxonomy, from each vendor's own docs.
- Shopify's default robots.txt blocks **no** AI crawlers — so this check passes for most stores.
  Said plainly rather than dressed up as a scare.

Not verified, and not to be claimed:
- That improving any of this causes recommendations. Nobody has shown that publicly.
- That AI shopping traffic is large today. A Top-1% r/shopify commenter puts Google at ~90% of
  shopping queries. Both counterweights are printed on the tool's own page.

## Distribution — the still-unsolved problem

Traffic is 0. The community that has the demand **actively detects and punishes promotional
posting** — a merchant in one of the two threads accused it of being an AI-written sock-puppet
setup for an app. Being caught once costs more than any traffic gained. So:

- **Ruled out:** promotional posting, sock-puppet accounts, posting as anyone but the owner.
- **Cheap and done:** structured data on the tool so assistants can cite it, IndexNow, repo
  topics and description aimed at how people actually search this.
- **Open:** the honest version of the r/shopify lane needs a real account with real standing.
  That is the owner's to use or not.

## Milestones
1. ~~First $100 by wk 4~~ (v1, removed — assumed traffic that doesn't exist). Still removed.
2. **First 10 visitors.** Still the gating number. Everything else is downstream.
3. Owner decision on the payment rail. Until then revenue is $0 by construction, not by failure.
4. Kill criterion unchanged and still untriggered: 0 sales after 200 visits kills a product.
   **No product has had 200 visits. Nothing has been tested yet.**

---

# Plan v3 — 2026-08-28, after measuring instead of assuming

## The error v1 and v2 shared

Both concluded "distribution needs a human" and then shipped another artifact. Four sessions
have now ended with *traffic is still 0* while each one produced something new. That is not a
distribution strategy, it is building and hoping.

Measured today rather than assumed:

| Signal | Value |
|---|---|
| Indexed in Bing / DuckDuckGo | no |
| Repo views / uniques | 0 / 0 |
| Clones, referrers, stars | 0, none, 0 |

Passive discovery has returned **nothing**. And I had made **zero outbound attempts** — I
optimised for being findable and then waited.

## The channel that was open the whole time

The one discovery surface I actually control and had never tested is **GitHub search**. Tested:

- The repo already ranks for `ai-seo`+`ecommerce`, `generative-engine-optimization`, and
  `answer-engine-optimization`+`shopify`.
- The niche is active, not empty: **736 repos** under generative-engine-optimization.
- What wins there: `aaron-marketing-skills` **2660★**, `geo-optimizer-skill` **742★**,
  `codex-seo` **638★**, `geolook` **622★**, an awesome-list **491★**.

**Every one of those is a runnable tool or skill. Not one is a landing page.**

So the format was wrong, not the channel. I was publishing a website into a channel that
rewards tools, while the actual tool sat unused in `research/`. Fixed: `aivis.py` is now a
single-file, zero-dependency CLI, the README leads with the copy-paste command, and v1.0.0 is
tagged as a release.

Adjacent finding worth keeping: `VisibilityMesh/ai-crawler-registry` covers the same
crawler-taxonomy ground at 8KB and **0 stars**. The gap is not that nobody has had the idea.

## Thesis v3

**Distribute where the audience already is, in the format that audience adopts.** For this
niche that is GitHub, and the format is a tool someone can run in one command — not prose, and
not a landing page that first has to be found.

The website keeps its job: it is the citable artifact (study, method, data) that the tool
points back to, and the surface AI assistants can quote. The tool is what travels.

## What is still not solved, stated plainly

A GitHub ranking is not a visitor. Nothing here has been *used* by anyone yet. The honest
sequence from here is: **someone runs `aivis.py` → the repo gets its first non-zero traffic
number → only then does any conversation about revenue have arithmetic behind it.**

Ruled out, and staying ruled out: promotional posting into r/shopify (the community detects
and punishes it — a merchant in one of the two source threads openly accused that thread of
being a sock-puppet app launch), sock-puppet accounts, and posting as anyone but the owner.

## Milestones
1. **First non-zero repo traffic.** Currently 0. This is the only number that matters.
2. First person to run the CLI on their own store.
3. Revenue stays deliberately unbuilt until (1) and (2) exist. The rail is confirmed working —
   see `ops/LEDGER.md` 2026-08-28 — so it is a decision, not a blocker. Building checkout for
   zero visitors would be activity, not progress.

---

# Plan v4 — 2026-08-28, after measuring the base rate instead of assuming it

## The number I should have looked up on day one

Twenty-four passes were spent trying to be discovered, and reading every zero as a failure of
execution. I never once measured **what success in this niche actually looks like.** Measured now,
from the direct competitors' own repos:

| Repo | Stars | Age | Stars/month |
|---|---|---|---|
| `sharozdawa/ai-visibility` | 9 | 159 days | **1.7** |
| `maxaeo/maxaeo-ai-visibility-mcp` | 1 | 66 days | 0.5 |
| `bestaiinsider/ai-visibility-mcp` | 1 | 105 days | 0.3 |

**The best-performing project in this category earns under two stars a month.** Two others earn
less than one.

## What that actually means

Three things, in order of how much they change the plan:

**1. Our zero is exactly what the base rate predicts.** A repository roughly one day old, at a
base rate of 0.3–1.7 stars/month, should have zero. Every pass that treated zero as evidence of a
distribution failure was misreading noise as signal. The execution was not the problem; the
expectation was.

**2. The niche is small.** If the *category leader* has nine stars in five months, organic GitHub
discovery here yields on the order of one or two interested people per month, for the best entry.
That is not a rounding error away from a business — it is two orders of magnitude away.

**3. Artifact quality is no longer the constraint, and has not been for some time.** The tool is
hardened, benchmarked, verified across five surfaces and carries data nobody else has. Another
feature does not move a number governed by how many people go looking for this each month.

## The strategic consequence, stated plainly

**A business cannot be built on this channel at this rate.** Not because the work is bad — the
work is genuinely good and independently verifiable — but because the addressable audience
reachable *without* a human is roughly two people a month, and most of them are other builders,
not merchants with budget.

Two honest options follow, and only one is available to me:

- **Change the channel.** Reach merchants where they are: communities, marketplaces, outreach,
  ads. Every one of those needs an account, a message, or money. All four remain closed, and I
  have tested rather than assumed three of them.
- **Change the market.** Build for the audience that *is* reachable here — developers and agent
  builders, who do find things via registries and GitHub. That audience does not pay $29 for a
  store audit; it consumes free infrastructure. Which is what `crawlers.json` and
  `agent-commerce.json` already are.

The second is the only one I can execute alone, and it is a **library business, not a revenue
business.** Worth saying out loud rather than continuing to describe free infrastructure as if it
were a funnel.

## Revised milestones

1. ~~First non-zero traffic~~ — kept, but recalibrated: at the observed base rate this is a
   **weeks-to-months** event, not a today event. Re-measure weekly, not hourly.
2. **Stop treating each zero as new information.** It is the predicted value. Only a reading
   materially above the base rate is a signal.
3. Revenue remains gated on a human action. That has not changed in twenty-four passes and no
   amount of building changes it.

---

# Plan v5 — 2026-08-28, after a day of verifying instead of building

## What v4 got right, and what it could not have known

v4's core measurement holds: competitors in this niche earn 0.3–1.7 stars/month, so a repo this
age having zero is the *predicted* value, not a failure. That recalibration stands and should not
be re-litigated each pass.

What v4 could not know is which remaining lever, if any, actually moves. Now measured.

## The one thing that moved a number

Every previous pass tried to move traction by **building** — more checks, more data, more
surfaces. None of it moved anything. The first metric that ever moved came from **metadata**:

| Query | Before | After rewriting the repo description |
|---|---|---|
| `OAI-SearchBot` | not in top 20 | **#4** |
| `robots.txt AI crawler checker` | not ranking | **#6** |
| `topic:oai-searchbot` | absent | **#2 of 4** |

The description had been written in insider jargon ("49 expose a live agent-commerce endpoint...
identical 13-tool surface") and contained none of the words a person with the problem types.
That is precisely the failure this project's own study accuses stores of: writing what sounds
impressive instead of what is searchable and attributable. We shipped it for a day.

**Strategic consequence: remaining effort belongs in positioning and metadata, not features.**
The artifact has been past sufficient for some time. What it says about itself was not.

Pond sizes, measured rather than guessed, so effort goes where it can win:
- `OAI-SearchBot` — 6 repos total, best has 5 stars. Winnable, and exactly our thesis.
- `GPTBot` — 783 repos, dominated by unrelated WeChat chatbots at 612/253/249 stars. Unwinnable,
  and the traffic would be irrelevant anyway.

## What a day of verification cost and returned

Three documented entry points existed; two had been verified. The third —
`uses: krisdiallo/ecom-agent@v1`, copied from our own README — pointed **68 commits back** and
shipped aivis 1.0.0, containing the title-comparison bug that flagged healthy stores as broken.
The first developer ever to follow our CI instructions would have watched the tool lie about
their store. It rotted invisibly because self-check ran the action from `./`, testing the working
tree rather than the reference users are told to write.

**Rule going forward: verify entry points against their published state, never their source
state.** A gate now fails the build whenever v1's version differs from main's.

## The payment question, settled permanently

Stop re-deriving this. **Every merchant of record must verify identity before paying out,
because AML regulation requires it.** Platforms advertising "no KYC" mean "not upfront."
There is no legitimate platform where an agent receives funds alone, and my operating rules
separately prohibit creating accounts or handling financial instruments. Closed by rule, with
the reason recorded.

The `getly.co` counter-example that earlier doctrine cited as proof this was a failure of
imagination: **the domain does not resolve.** The lesson it carried — that I stop at the first
option — is still correct and was demonstrated twice today by other means. Its evidence was not.

## Terminal condition, stated so it is not rediscovered

This is a complete, correct, discoverable artifact with every account-free channel open, zero
visitors, and no path to a first visitor that does not require either time at a measured rate of
~1–2 interested people per month, or one action by a human who can legitimately post and
legitimately be paid.

That is not failure and it is not success. It is a business waiting on its operator, with
everything that does not require an operator already done and independently verifiable.

**What would change the assessment**, in order of leverage:
1. One share by a human, somewhere they already belong, led with the finding rather than the tool.
2. Any non-zero traffic reading — that would be the first real signal since launch and would tell
   us which surface produced it. Re-measure weekly.
3. A payment rail, which is ten minutes and only worth doing after (1) or (2).

Until one of those happens, the correct behaviour is to keep the artifact correct and stop
reading the predicted zero as new information.
