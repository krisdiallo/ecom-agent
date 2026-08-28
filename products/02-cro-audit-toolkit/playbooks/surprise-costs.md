# Playbook — Surprise costs at checkout
Triggered by check #30 scoring 0 or 1. Usually the single largest recoverable loss in a store.

## The mechanism
A buyer forms a price expectation on the product page. Every unexpected cost after that point
is felt as a betrayal, not as a line item — which is why a $6 shipping surprise loses more
sales than a $6 higher sticker price would have.

## Fixes, in order of impact per hour of work
1. **Put delivered cost on the product page.** A shipping estimator, or plain text: "Shipping
   $6.90, or free over $60." One hour of work, largest single effect.
2. **Show the free-shipping gap in the cart.** "$12 away from free shipping" converts because it
   gives the buyer an action, not a fact.
3. **Fold shipping into price if your margins allow it.** Test it — for some categories the
   higher sticker price loses more than the surprise does. Do not assume; measure.
4. **Show taxes/duties before the final step** for international buyers. An unexpected customs
   charge produces a refused delivery, which costs you the product and the shipping both ways.

## How to know it worked
Watch cart→checkout-start and checkout-start→purchase separately. This fix should move the
second one. If it moves neither but add-to-cart falls, you've priced yourself out honestly —
that's a real finding, not a failure, and it's better to know.

## What not to do
Don't add a "shipping calculated at checkout" note and call it solved. That's a warning that a
surprise is coming, which is worse than either showing the number or saying nothing.
