# The raw-HTML fix for Shopify

## The problem

From the 70-brand survey: the most common critical defect is Product schema injected
by JavaScript. It looks perfect in dev tools and in Google's Rich Results Test — both
run JavaScript — while being completely absent from what an AI crawler receives.

**Why this matters:** AI crawlers (OAI-SearchBot, PerplexityBot, Claude-SearchBot) do
not run JavaScript. If your JSON-LD is injected by JS, they never see it. Every tool you'd
normally check with reports success.

## How to check if you have this problem

1. Open a product page on your store
2. `view-source:https://your-store.com/products/your-product` (NOT Inspect)
3. Search the source for `application/ld+json`
4. If the JSON-LD block is NOT in the source HTML, it's JS-injected — invisible to AI crawlers
5. If it IS in the source HTML, you're fine

Or run the free checker:
```bash
python3 aivis.py your-store.com
```
It will report "Structured data is injected by JavaScript" if you have this defect.

## The fix: server-render the JSON-LD

### Option A: Use the Liquid template (recommended)

Copy `schema-templates/product-jsonld-shopify.liquid` into your theme's product
template. This renders the Product schema in the raw HTML using Shopify's Liquid
template engine, which runs server-side.

**Where to put it:**
- `snippets/product.liquid` (or your theme's equivalent product template)
- The JSON-LD must be in the template that Shopify renders server-side, NOT in a
  custom app that injects it via JavaScript

### Option B: Check your theme

Some Shopify themes inject JSON-LD via JavaScript (in a `<script>` that runs after
page load). If yours does this, the fix is to move it to a Liquid template that renders
server-side. The template in this kit does that.

### Verify the fix

After applying the template:
1. `view-source:https://your-store.com/products/your-product`
2. Search for `application/ld+json`
3. The Product JSON-LD should now be in the raw HTML
4. Run `python3 aivis.py your-store.com` — the JS-injection warning should be gone

## What NOT to do

- Do NOT add a JavaScript snippet that injects JSON-LD on page load — that recreates the defect
- Do NOT rely on Google's Rich Results Test to confirm the fix — it runs JS, so it sees
  both the broken and fixed versions as "working"
- The only reliable test is `view-source` (raw HTML) or the free `aivis.py` checker
