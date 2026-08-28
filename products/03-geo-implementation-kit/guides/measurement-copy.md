# Concrete-measurement copy guide

## The finding

From the 70-brand AI visibility survey: the median product page carries **2 concrete
measurements**. 14 of 51 pages carry none at all. Assistants repeat attributable
facts, not adjectives.

- "holds 120 lb" survives the trip from page to answer
- "premium quality" does not, because it's true of every product in the category

This is the most winnable gap: a quarter of well-resourced brands have zero
measurements, so adding even a few puts you ahead.

## The 5 highest-value measurement types

Prioritized by how often an assistant would cite them when comparing products:

### 1. Dimensions and weight
```
Dimensions: 24" × 36" × 2" (61 × 91 × 5 cm)
Weight: 4.2 lb (1.9 kg)
```
Why: the most common question an assistant gets is "will it fit in my space?"

### 2. Materials (specific, not marketing)
```
Shell: 100% organic cotton (GOTS certified)
Fill: recycled polyester made from 12 plastic bottles
```
Why: "what's it made of?" gets asked directly. Specific material names are citable;
"premium materials" is not.

### 3. Capacity and compatibility
```
Capacity: holds 40 L (fits a 15" laptop)
Compatible with: USB-C charging, MacBook Air 13", iPad Pro 12.9"
```
Why: "will it work with my device?" is a dealbreaker question. Compatibility facts
prevent the assistant from hedging.

### 4. Performance specs (measured, not claimed)
```
IPX7 waterproof (tested 30 min at 1m depth)
Tensile strength: 120 lb (ASTM D5034)
```
Why: measured specs with a test standard are the strongest citations. "Waterproof"
alone is a claim; "IPX7, tested 30 min at 1m" is a fact.

### 5. Care and origin
```
Made in: Portland, OR, USA
Care: machine wash cold, tumble dry low
Warranty: lifetime (covers seams and zippers)
```
Why: origin and warranty are trust signals that assistants use to differentiate
otherwise similar products.

## The copy template

For each product page, fill in this structure:

```
[Product name] is [one-line factual description].

Key facts:
- Dimensions: [exact measurements in imperial and metric]
- Weight: [exact weight]
- Materials: [specific material names, certifications if any]
- Capacity: [exact capacity, what it fits]
- Compatible with: [specific devices/products]
- Performance: [measured specs with test standards]
- Made in: [origin]
- Care: [exact care instructions]
- Warranty: [terms]
```

## The self-check

Every prompt in the companion prompt system ends with: **list any sentence that would
still be true with a competitor's name swapped in.** Apply the same test here:

- "Premium quality" → true of every competitor's product → remove
- "Holds 120 lb" → only true of this product → keep
- "Luxurious feel" → true of every competitor's product → remove
- "100% organic cotton, GOTS certified" → only true of this product → keep

If a sentence survives the swap test, it's an attributable fact an assistant can cite.
If it doesn't, it's filler that every competitor can also claim.
