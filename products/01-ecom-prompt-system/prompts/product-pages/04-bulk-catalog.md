# Bulk Catalog Descriptions (100–5,000 SKUs)
**Use when:** you have a catalog, not a product. Nobody else's prompt pack covers this.

The failure mode at scale isn't quality, it's *sameness*: run the same prompt 800 times and you
get 800 descriptions with the same three sentence shapes. Search engines read that as thin,
duplicate content, and shoppers browsing a collection feel it immediately.

```
[STORE BRIEF]
BATCH: paste rows as CSV — sku, name, category, key attributes, price, differentiator
VARIATION CONTROL — rotate deterministically across the batch so no two neighbours match:
  openings: [problem, use-case, material, comparison, sensory, spec-led]
  lengths:  [60w, 90w, 120w] assigned by price tier
STRUCTURE (identical for every row, so the template stays scannable):
  1 hero line · 3 bullets · 1 spec line · 1 fit/compat line

RULES:
- Use ONLY the attributes in that SKU's row. Any gap becomes [NEED: sku, field]. Never carry a
  fact from a neighbouring row — that is how a catalog acquires wrong specs at scale.
- Vary opening word AND sentence shape between consecutive rows. State which opening you used.
- Output CSV: sku, description, opening_used, needs_flags

Process in batches of 25. After each batch, print:
- duplicate 6-word sequences appearing in 3+ rows (these are your template tells — I will rewrite them)
- rows flagged [NEED] and the field missing
```

## Before you run 2,000 rows
Run 25. Read all 25 in a row, the way a shopper scrolling a collection does. If you can feel the
template, fix the variation control before spending the tokens on the full catalog.
