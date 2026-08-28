# Product Description (the one that doesn't sound like AI)

**Use when:** launching a product, or replacing a description that reads like a spec sheet.
**Time:** 5 min. **Output:** hero paragraph, 5 benefit bullets, spec block, objection line.

---

## Prompt

```
You are writing a product description for an ecommerce store. Accuracy outranks persuasion:
a claim I cannot prove costs me a chargeback and a bad review.

[STORE BRIEF]

PRODUCT:
- Name:
- What it physically is (materials, dimensions, contents):
- What it does for the buyer:
- Price:
- The 3 things a buyer must know before they'd feel safe clicking Add to Cart:

RULES:
1. Lead with the change in the buyer's life, not the object. The object is evidence.
2. Every benefit must trace to a concrete feature I listed. If you cannot trace it, cut it.
3. Do NOT invent: measurements, materials, certifications, review quotes, origin, counts,
   awards, or comparisons to named competitors. If a detail would help and I did not give
   it to you, write [NEED: <the detail>] instead of guessing.
4. Banned phrases: elevate, game-changer, unlock, seamlessly, must-have, revolutionize,
   "look no further", "whether you're a ___ or a ___", "in today's world".
5. Read the price. A $19 product earns 80 words. A $400 product earns 300 and needs to
   handle risk explicitly.

OUTPUT:
A) HERO — 2–3 sentences. Sentence one names the buyer's trigger moment.
B) BULLETS — 5, each ≤14 words, format: <Benefit> — <the feature that proves it>.
C) SPECS — plain table, only facts I supplied.
D) OBJECTION — one sentence answering the single biggest reason they won't buy.

SELF-CHECK (print this, do not skip):
- Claims I made that you did NOT give me evidence for: <list, or "none">
- [NEED] items: <list>
- Sentences that would survive if the product name were swapped for a competitor's:
  <list them — these are the generic ones, and they should be rewritten>
```

---

## Why the self-check is the point
The last line is the highest-leverage part of the prompt. Any sentence that still makes
sense with a competitor's name in it is a sentence describing the category, not your
product — that's the exact texture people mean when they say copy "sounds AI-written."
Rewrite those and the description stops being interchangeable.

## Iterating
- Too flat? Add: `Rewrite B) so each bullet leads with a verb.`
- Too hypey? Add: `Cut adjective density by half. Replace adjectives with numbers.`
- Wrong register? Paste 2 paragraphs you love and add: `Match this rhythm, not its content.`
