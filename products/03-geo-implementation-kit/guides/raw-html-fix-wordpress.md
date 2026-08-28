# The raw-HTML fix for WordPress/WooCommerce

## The problem

From the 70-brand survey: Product schema injected by JavaScript is invisible to AI
crawlers. In WordPress, this happens when a schema plugin (Yoast, RankMath, or a
JS-injected structured data plugin) renders JSON-LD via JavaScript after page load.

## How to check

```bash
# view-source (NOT Inspect)
view-source:https://your-domain.com/product/your-product
# Search for "application/ld+json"
# If it's NOT in the source, it's JS-injected

# Or run the free checker
python3 aivis.py your-domain.com
```

## The fix: server-render via PHP

Use the PHP template from `schema-templates/product-jsonld-wordpress.php`.
It hooks into WooCommerce's product template and renders the JSON-LD in the
server-side HTML.

### Install

Add the PHP code to your theme's `functions.php` (or a custom plugin file). The
`add_action('woocommerce_single_product_summary', ...)` hook places the JSON-LD
in the product page's server-rendered HTML.

### Why not the JS approach

If you're using Yoast's schema output or a JS-injected structured data plugin, the
schema appears in Google's Rich Results Test (which runs JS) but is absent from what
an AI crawler receives. This PHP version renders the same data into the raw HTML.

### Common wrong pattern (recreates the defect)

```php
// WRONG — this injects after JS runs, invisible to AI crawlers
add_action('wp_footer', function() {
    echo '<script>document.querySelector("head").appendChild(...JSON-LD...)</script>';
});
```

### Verify the fix

```bash
view-source:https://your-domain.com/product/your-product
# Search for "application/ld+json" — should be in the raw HTML
python3 aivis.py your-domain.com  # JS-injection warning should be gone
```
