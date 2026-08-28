# The raw-HTML fix for Next.js

## The problem

From the 70-brand survey: the most common critical defect is Product schema injected
by JavaScript. In Next.js this happens when you put JSON-LD injection in a
`useEffect` or a client component — it renders after hydration, so AI crawlers
that receive the server-rendered HTML never see it.

## How to check

```bash
# view-source (NOT Inspect — Inspect runs JS)
view-source:https://your-domain.com/products/your-product
# Search for "application/ld+json"
# If it's NOT there, it's client-injected

# Or run the free checker
python3 aivis.py your-domain.com
```

## The fix: server-render via getServerSideProps

Use the `ProductJsonLd` component from `schema-templates/product-jsonld-nextjs.tsx`.
The key is that it renders in the server HTML:

```tsx
// pages/products/[handle].tsx
import { ProductJsonLd } from '@/components/ProductJsonLd';

export async function getServerSideProps({ params }) {
  const product = await fetchProduct(params.handle);
  // product is available as a prop BEFORE the page renders
  return { props: { product } };
}

export default function ProductPage({ product }) {
  return (
    <>
      {/* This renders server-side — JSON-LD is in the raw HTML */}
      <ProductJsonLd product={product} />
      <h1>{product.title}</h1>
    </>
  );
}
```

### Why getServerSideProps matters

`getServerSideProps` runs on the server. The product data is available when the HTML
is rendered, so the JSON-LD is in the raw HTML that AI crawlers receive. If you
fetch the product in a `useEffect` or client-side hook, the data arrives after
hydration — too late for AI crawlers.

### Common wrong pattern (recreates the defect)

```tsx
// WRONG — this injects after JS runs, invisible to AI crawlers
export default function ProductPage() {
  const [product, setProduct] = useState(null);
  useEffect(() => {
    fetch('/api/products/handle').then(r => r.json()).then(setProduct);
  }, []);
  if (!product) return null;
  return <ProductJsonLd product={product} />; // renders after JS — too late
}
```

### Verify the fix

```bash
view-source:https://your-domain.com/products/your-product
# Search for "application/ld+json" — should be in the raw HTML now
python3 aivis.py your-domain.com  # JS-injection warning should be gone
```
