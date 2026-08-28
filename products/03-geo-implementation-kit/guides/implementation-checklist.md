# Implementation checklist

## Step 1: Diagnose

Run the free checker on your store:

```bash
curl -sO https://raw.githubusercontent.com/krisdiallo/ecom-agent/main/aivis.py
python3 aivis.py yourstore.com
```

Note which findings appear:
- [ ] "Blocking N crawler(s) that decide if you appear in AI answers" → use the robots.txt template
- [ ] "Structured data is injected by JavaScript" → use the raw-HTML fix guide
- [ ] "No Product type" or "Product schema has no offers" → use the JSON-LD template
- [ ] "Fewer than 5 concrete measurements" → use the measurement-copy guide
- [ ] "Your title contradicts your og:title" → fix your page <title> to match og:title

## Step 2: Fix (per platform)

### robots.txt
1. Copy the template for your platform from `robots-templates/`
2. Paste it into your robots.txt (Shopify: Preferences; Next.js: /public/; WordPress: root or Yoast)
3. Verify: `curl https://yourstore.com/robots.txt` shows the AI crawler rules

### Product schema (JSON-LD)
1. Copy the template for your platform from `schema-templates/`
2. Place it in your product page template (server-rendered, not JS-injected)
3. Verify: `view-source:https://yourstore.com/products/your-product` contains `application/ld+json`

### Raw-HTML fix (if JS-injection found)
1. Read the guide for your platform from `guides/raw-html-fix-*.md`
2. Move JSON-LD from JS injection to server-side rendering
3. Verify: `view-source` shows the JSON-LD in raw HTML

### Measurement copy
1. Read `guides/measurement-copy.md`
2. Add 3–5 concrete measurements per product page (dimensions, weight, materials, etc.)
3. Run the swap test on each sentence

## Step 3: Verify

Re-run the checker:
```bash
python3 aivis.py yourstore.com
```

Expected result:
- [ ] 0 critical findings (was: however many you had)
- [ ] "No robots.txt" or "blocking AI search crawlers" → resolved
- [ ] "Structured data injected by JavaScript" → resolved
- [ ] Product schema present with offers → resolved
- [ ] 5+ concrete measurements → resolved

## Step 4: Ongoing

Run monthly:
```bash
python3 aivis.py yourstore.com --pages 5
```

This samples 5 product pages and reports systemic vs one-off issues. AI crawler
landscape changes — new crawlers appear, platforms update their defaults. A monthly
check catches regressions from theme updates or platform changes.
