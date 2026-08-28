# Abandoned Cart Flow (3 emails, no fake urgency)

**Use when:** setting up or rewriting recovery. **Output:** 3 emails with timing + subject lines.

---

## Prompt

```
Write a 3-email abandoned cart sequence.

[STORE BRIEF]

CART CONTEXT:
- Typical abandoned cart value:
- Do you offer a discount? (yes/no — and if yes, max %, and does it cannibalize full-price?)
- Shipping cost and threshold:
- Return policy:
- The real reason people abandon (from support tickets / surveys, if you know):

SEQUENCE LOGIC — respect it:
- Email 1 (1 hour): assume a distraction, not a decision. No discount. Remove friction:
  restate shipping cost, returns, and delivery window. One-click return to cart.
- Email 2 (24 hours): assume an unresolved objection. Address the top 2 objections directly.
  Use real proof (review quote, return rate, guarantee) — only proof I gave you.
- Email 3 (72 hours): assume price or timing. Discount ONLY if I said yes above; otherwise
  offer a lower-commitment path (smaller size, sample, save-cart, restock alert).

RULES:
- No countdown timers, no "only 2 left" unless I gave you real inventory numbers.
  Fake scarcity is illegal in several jurisdictions and obvious to buyers in all of them.
- Subject lines: 3 options each, under 45 characters, no emoji unless the brief says so.
- Preview text must add information, not repeat the subject.
- Plain-text-feeling. Assume it renders in dark mode on a 5-year-old Android.

OUTPUT per email: timing, 3 subject lines, preview text, body, single CTA, and one line
explaining the psychological assumption you're making about the reader.

SELF-CHECK: list any claim in these emails I have not given you evidence for.
```

---

## Benchmark reality
Sequences like this typically recover a single-digit percentage of abandoned carts. If a
vendor tells you their template recovers 30%, they are quoting open rate or measuring
people who would have returned anyway. Set the expectation before you set up the flow.
