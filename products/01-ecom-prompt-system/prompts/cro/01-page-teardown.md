# Product Page Teardown

**Use when:** traffic is fine, conversion isn't. **Time:** 10 min. **Output:** ranked fix list.

---

## Prompt

```
Act as a conversion analyst reviewing a product page. You are paid to find reasons people
leave, not to compliment the page.

[STORE BRIEF]

PAGE (paste the full visible text top to bottom, in order, and describe each image):

DATA (fill in what you have, write "unknown" for the rest):
- Sessions / conversion rate / add-to-cart rate:
- Mobile vs desktop split and CR for each:
- Top exit point if known:
- Average order value:

TASK:
1. Reconstruct the page as a first-time mobile visitor experiences it in the first 5
   seconds. What do they know? What is still unanswered?
2. List every unanswered question a buyer needs resolved before paying. Order by how many
   buyers it blocks.
3. For each question, say where on the page it should be answered and why there.
4. Flag friction: unclear pricing, hidden shipping cost, weak or missing trust signals,
   ambiguous variant selection, slow-loading hero, buried reviews, unclear returns.
5. Rank ALL findings by (buyers blocked) x (ease of fix). Give the top 5 only.

RULES:
- Ground each finding in text I actually pasted. Quote it.
- Do not recommend a redesign. Recommend edits I can ship this afternoon.
- If the data suggests the problem is upstream (wrong traffic, wrong price, wrong product),
  say so plainly instead of optimizing a page that isn't the bottleneck.

OUTPUT — table:
| # | Finding (quote the page) | Buyer question it leaves open | Fix | Effort | Expected impact |

Then: "If you only do one thing this week: ___"

SELF-CHECK: which of your findings are you least confident in, and what would you need to
see (heatmap, recording, data) to confirm it?
```

---

## Note on honesty
Point 5's "the problem is upstream" clause matters. Most CRO advice assumes the page is
the problem because the page is what you're looking at. Sometimes a page converting at
0.4% is a page doing its job for traffic that was never going to buy. A tool that can't
tell you that will happily sell you a month of pointless edits.
