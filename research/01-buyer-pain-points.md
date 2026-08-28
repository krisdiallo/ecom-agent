# Buyer research — ecom owners + AI copy (2026-08-27)
Sources: r/shopify, r/ecommerce, r/Klaviyo, Shopify Community (scraped directly); Gumroad live metadata.
Etsy pricing UNVERIFIED (blocked scraping). Full quotes/URLs in the agent report; key findings:

## Verified pain points driving purchase
1. "Generic input → generic output... AI slop tsunami" — merchants know the cause is context, not model.
2. "it can't write in my tone of voice" — brand voice is the #1 named failure.
3. Hallucinated specs: Shopify's own Sidekick invents products/features that don't exist.
   RE-VERIFIED 2026-08-27, still live and current. Primary sources:
   r/shopify 1ps7ug6 (2025-12-21) "kept making up products that didn't exist"; same thread,
   invents product features in images. r/shopify 1m4169l (2025-07-19) sales figure reported
   as 3 vs actual 2463. r/shopify 1rbtguj (2026-02-22) still complaining.
   CAVEAT: the "support confirmed there is no setting to disable it" half is NOT verified.
   Do not state it. Also note Sidekick docs are absent from the 2026 Help Center and a
   Shopify "AI Toolkit" shipped ~Apr 2026 — the product may have been renamed/absorbed.
4. Editing overhead cancels the savings: "spend 20 minutes fixing output that doesn't sound like their brand."
5. Email flows come out as 5 copies of email #1: "the model has no idea what it already said...
   you spend more time de-duplicating than you saved."
6. ~~Measured harm: AI-generated Klaviyo flows UNDERPERFORMED traditional ones on welcome,
   abandonment, and post-purchase.~~ **RETRACTED 2026-08-27 — could not be substantiated.**
   Re-verification found no primary source for Shopify/Klaviyo merchants A/B testing AI flows
   and finding them worse. One counter-example exists (r/emailmarketing 1orob0g, 2025-11-13:
   slightly *higher* open rates with Klaviyo AI).
   What IS verified, but outside ecommerce: r/salesdevelopment 1sk965x (2026-04-13) — ~74,000
   B2B cold emails, 6 months, 9 accounts: human 3.4% positive reply vs AI 2.1%; close rate
   22% vs 14%; described as consistent and statistically significant.
   Usable claim: "AI copy does not automatically outperform human copy, and one large controlled
   test outside ecommerce found it materially worse." NOT usable: any claim about ecommerce
   flow performance specifically.
7. Bulk catalogs (1k+ SKUs) get no help; merchants write their own Python/API pipelines.
8. SEO drift: "AI content is fine for drafts but needs heavy editing to avoid duplicate or thin text."

## Buyer's exact words (use verbatim in copy + SEO)
"sounds robotic" · "sounds so corporate and generic" · "can't write in my tone of voice" · "brand voice"
· "AI slop" · "hallucinates" · "prompts that actually work" · "1k+ SKUs" · "bulk product descriptions"
· "de-duplicating" · "a solid system or SOP" · "Not looking for generic advice"
Mocked clichés (advertise AGAINST these): "elevate your", "in today's fast-paced world", "seamless", "unlock".

## Competitive set (Gumroad, verified)
- Free 100+ variation pack (Weaverse, 4.9/14 ratings) — price floor is $0. Do not compete on count.
- 1,000 prompts / $19.99 — 0 ratings. 700+ prompts / $29.99 — 0 ratings. 500 prompts / $7.99 — 0 ratings.
- 50 ad frameworks / $24.99 — 4.8/4 ratings, ads only.
- One seller advertises "4.8/5 – Rated by 5,000+" while its real Gumroad rating count is 0.

## Strategic read
Every competitor sells a LIST. Merchants are asking for a SYSTEM. The category has near-zero genuine
reviews and at least one seller fabricating social proof — trust is the open position, and it is the
cheapest one for us to take because we can simply not lie.

## What this changes in our product
- KEEP: brief-first architecture, [NEED] fact-guards, self-checks, flow-level arcs. All directly
  target verified complaints 1-6. This was the right bet.
- ADD: bulk/1k+ SKU workflow (gap 7, nobody serves it).
- ADD: an AI-tells editing checklist (gap 4/8 — the merchant's real cost is editing time).
- REFRAME copy in buyer's verbatim language: "sounds robotic", "brand voice", "invents specs".
- DO NOT claim AI flows beat traditional flows. Finding 6 says merchants tested that and it's false.
