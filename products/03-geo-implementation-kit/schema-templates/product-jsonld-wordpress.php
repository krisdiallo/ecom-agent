<?php
/**
 * JSON-LD Product schema for WordPress/WooCommerce — server-rendered in PHP.
 *
 * Place this in your theme's single-product.php template (or via a functions.php
 * hook on woocommerce_single_product_summary). It renders Product schema
 * in the raw HTML that AI crawlers receive, NOT in a client-side JS script.
 *
 * This is the fix for the #1 defect found in the 70-brand survey:
 * structured data injected by JavaScript is invisible to AI crawlers.
 *
 * WooCommerce gives you the product data in PHP — render the JSON-LD
 * server-side, not via JS after page load.
 */

function render_product_jsonld() {
    global $product;
    if ( ! $product ) return;

    $variant = $product->get_available_variant();
    $image_url = wp_get_attachment_url( $product->get_image_id() );

    $jsonld = array(
        '@context'    => 'https://schema.org',
        '@type'       => 'Product',
        'name'        => $product->get_name(),
        'description' => wp_strip_all_tags( $product->get_short_description() ),
        'sku'         => $product->get_sku(),
        'brand'       => array(
            '@type' => 'Brand',
            'name' => $product->get_attribute( 'pa_brand' ) ?: get_bloginfo( 'name' ),
        ),
        'image'       => $image_url,
        'offers'      => array(
            '@type'         => 'Offer',
            'price'         => $product->get_price(),
            'priceCurrency' => get_woocommerce_currency(),
            'availability'  => $product->is_in_stock()
                ? 'https://schema.org/InStock'
                : 'https://schema.org/OutOfStock',
            'url'           => get_permalink( $product->get_id() ),
            'itemCondition' => 'https://schema.org/NewCondition',
        ),
    );

    echo '<script type="application/ld+json">'
       . wp_json_encode( $jsonld )
       . '</script>';
}

// Hook it into the product page
add_action( 'woocommerce_single_product_summary', 'render_product_jsonld', 5 );

// ---- Why not the JS approach ----
//
// If you're using a JS-based schema plugin (like Yoast's or a JS-injected
// structured data plugin), the schema appears in dev tools and in Google's
// Rich Results Test — both run JavaScript — but is ABSENT from what an
// AI crawler receives. This PHP version renders the same data into the
// raw HTML, where AI crawlers actually read it.
//
// Test: view-source on your product page. Search for "application/ld+json".
// If the JSON-LD is there, AI crawlers can read it. If it's only visible
// in Inspect (after JS runs), it's invisible to them.
