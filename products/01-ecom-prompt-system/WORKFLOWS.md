# Workflows — chaining prompts into a finished job

A single prompt does a task. These chains do a job. Each step's output is the next
step's input; the arrows are where you paste.

---

## Workflow 1: Launch a new product (≈45 min)
1. `INPUTS.md` — fill the brief once. →
2. `product-pages/01-product-description.md` — get hero, bullets, specs. →
3. Resolve every `[NEED]` the self-check surfaced. **Do not skip this.** Unresolved
   [NEED]s are exactly the claims that become refund requests. →
4. `seo/01-collection-page.md` — place the product in a collection and link it. →
5. `ads/01-angle-generation.md` — 8 angles, pick top 3 for cold traffic. →
6. `email/01-abandoned-cart.md` — the flow catches the traffic those ads send.

## Workflow 2: Fix a page that isn't converting (≈30 min)
1. `cro/01-page-teardown.md` — get the ranked findings. →
2. If the teardown says the problem is upstream (traffic/price/product), **stop.**
   Fix that instead. Rewriting copy for the wrong audience is the most expensive
   way to be busy. →
3. Otherwise, take the top finding → `product-pages/01-product-description.md`,
   feeding the specific unanswered question in as a constraint. →
4. Ship one change. Wait for enough sessions to matter. Then the next.
   Shipping five changes at once means learning nothing from any of them.

## Workflow 3: Creative is fatiguing (≈25 min)
1. `ads/01-angle-generation.md`, pasting in the ads that are dying and their metrics. →
2. Pick angles from families you have **not** tested. Repeating a family you already
   burned is why fatigue feels permanent. →
3. New landing copy per angle via the description prompt — an angle that promises
   something the page doesn't repeat will convert badly and look like a creative problem.

## Workflow 4: Weekly hour (recurring)
Monday: teardown one page. Ship one fix.
Wednesday: 3 new ad angles from an untested family.
Friday: read 10 support tickets → `ops/01-support-macros.md`. Support tickets are the
cheapest customer research you will ever get, and the only kind that's already paid for.

---

## The rule that makes all of this work
Change one thing. Measure. The reason most stores can't tell you what improved their
conversion rate is that they changed six things in a week and attributed it to the one
they were proudest of.
