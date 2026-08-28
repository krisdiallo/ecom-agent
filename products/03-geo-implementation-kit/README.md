# GEO Implementation Kit

## What this is

Your free AI visibility checker tells you *whether* AI assistants can read your store.
This kit tells you *how to fix it* — ready-to-paste code, templates, and step-by-step
guides that implement AI search visibility on four platforms.

## What's included

### 1. Search-safe robots.txt templates (per platform)

Ready-to-paste blocks that block the 8 training crawlers and allow the 7 search/answer
crawlers. Not generic advice — actual robots.txt text you paste into your file, with
platform-specific path rules.

**Covers:** Shopify, Next.js, WordPress/WooCommerce, generic HTML

**The distinction that matters:** blocking `GPTBot` opts you out of training and costs
nothing in search. Blocking `OAI-SearchBot` removes you from ChatGPT search. Most
"block AI" guides conflate these. These templates don't.

### 2. JSON-LD Product schema templates (per platform)

Copy-paste `Product` and `ProductGroup` JSON-LD templates with all required fields
(`name`, `description`, `offers` with `price`/`priceCurrency`/`availability`, `sku`,
`brand`). Platform-specific placement:

- **Shopify:** where to inject in Liquid templates (`product.liquid`, `theme.liquid`)
- **Next.js:** SSR vs client-side injection — why SSR matters for AI crawlers
- **WordPress/WooCommerce:** WooCommerce template hooks, header injection
- **Generic HTML:** `<script type="application/ld+json">` placement

### 3. The raw-HTML fix (the #1 defect we found)

From the 70-brand survey: the most common critical defect is structured data
injected by JavaScript — invisible to AI crawlers that don't run JS. This section
gives platform-specific fixes:

- **Shopify:** how to move JSON-LD from JS-injected to server-rendered
- **Next.js:** `getServerSideProps` vs `useEffect` for schema injection
- **WordPress:** server-side PHP rendering vs client JS
- **How to test:** `view-source` vs Inspect — the one-command check

### 4. Concrete-measurement copy templates

The study found the median product page carries 2 concrete measurements. Assistants
repeat attributable facts ("holds 120 lb") not adjectives ("premium quality"). This
section gives:

- A copy template that produces measurable, attributable product facts
- The 5 highest-value measurement types (dimensions, weight, materials, capacity,
  compatibility)
- Before/after examples from the study data

### 5. Implementation checklists

Step-by-step per platform, from the checker diagnosis to the fix:

1. Run `aivis.py yourstore.com` → get the diagnosis
2. Find your issue in the checklist
3. Paste the fix from the kit
4. Re-run the checker → confirm it passes

## File structure

```
products/03-geo-implementation-kit/
├── README.md                    ← this file (start here)
├── robots-templates/
│   ├── shopify.txt               ← paste into Shopify robots.txt
│   ├── nextjs.txt
│   ├── wordpress.txt
│   └── generic.txt
├── schema-templates/
│   ├── product-jsonld-shopify.liquid
│   ├── product-jsonld-nextjs.tsx
│   ├── product-jsonld-wordpress.php
│   └── product-jsonld-generic.html
├── guides/
│   ├── raw-html-fix-shopify.md
│   ├── raw-html-fix-nextjs.md
│   ├── raw-html-fix-wordpress.md
│   ├── measurement-copy.md
│   └── implementation-checklist.md
└── INPUTS.md                     ← the structured brief the templates expect
```

## Why $29 and not free

The checker is free because diagnosing a problem is worth giving away — it proves
the kit understands the issue. The fixes are $29 because they save you 2–4 hours of
implementation work per platform. You're paying for the paste-ready code and the
platform-specific knowledge, not for the diagnosis.

Browse the full contents on GitHub before buying. 14-day refund by email if it
doesn't save you time.

MIT licensed.
