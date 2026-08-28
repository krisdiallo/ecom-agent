/**
 * JSON-LD Product schema for Next.js — server-rendered via getServerSideProps.
 *
 * Place this component in your product page (e.g. pages/products/[handle].tsx).
 * It renders Product schema in the raw HTML that AI crawlers receive,
 * NOT in a client-side useEffect that only runs after JS.
 *
 * This is the fix for the #1 defect found in the 70-brand survey:
 * structured data injected by JavaScript is invisible to AI crawlers.
 *
 * The key: the JSON-LD must be in the server-rendered HTML, not injected
 * client-side. Next.js makes this easy with getServerSideProps.
 */

import { Product } from '@/types';

interface Props {
  product: Product;
}

export function ProductJsonLd({ product }: Props) {
  const variant = product.variants?.[0] ?? product.variants?.[0];
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.title,
    description: product.description?.slice(0, 300),
    sku: variant?.sku,
    brand: {
      '@type': 'Brand',
      name: product.vendor,
    },
    image: product.featuredImage
      ? `https://${process.env.NEXT_PUBLIC_STORE_URL}${product.featuredImage}`
      : undefined,
    offers: {
      '@type': 'Offer',
      price: variant?.price,
      priceCurrency: variant?.currency,
      availability: product.available
        ? 'https://schema.org/InStock'
        : 'https://schema.org/OutOfStock',
      url: `${process.env.NEXT_PUBLIC_STORE_URL}/products/${product.handle}`,
      itemCondition: 'https://schema.org/NewCondition',
    },
  };

  return (
    <script
      type="application/ld+json"
      // eslint-disable-next-line react/no-danger
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  );
}

// ---- Usage in getServerSideProps ----
//
// export async function getServerSideProps({ params }) {
//   const product = await fetchProduct(params.handle);
//   return { props: { product } };
// }
//
// export default function ProductPage({ product }) {
//   return (
//     <>
//       <ProductJsonLd product={product} />
//       <h1>{product.title}</h1>
//       {/* ...your product page... */}
//     </>
//   );
// }
//
// The JSON-LD is rendered server-side and present in the raw HTML that
// AI crawlers (OAI-SearchBot, PerplexityBot, Claude-SearchBot) receive.
// Do NOT move this to a useEffect or client component — that recreates
// the JS-injection defect this fixes.
