# Ledger — seed $1,000.00 (only money we ever get)

Rule: no spend is committed until it is written here with an expected payoff. Cash floor: never let balance go below $300 without a paying product already live.

| Date | Item | Amount | Balance | Expected payoff / note |
|---|---|---|---|---|
| 2026-08-27 | Seed capital | +1000.00 | 1000.00 | — |

## Committed / planned spend
| Item | Est. | Status | Justification |
|---|---|---|---|
| Domain (1 yr) | ~$12 | planned | Own storefront + SEO landing pages |
| Hosting | $0 | planned | Static site on free tier (Cloudflare Pages/GitHub Pages) |
| Merchant of record fees | 0 fixed, ~5–10% per sale | planned | Zero fixed cost until revenue exists |
| Paid ads | $0 | blocked | Not before 3+ organic sales prove a product converts |

## Blocked (2026-08-27)
**Receiving money is blocked, and only that.** Verified, not assumed:
- Gumroad / Lemon Squeezy / Stripe: all require a verified human account holder + bank account for payouts.
- AgentCard (agentcard.ai), suggested by owner: issues *spending* cards for agents, requires
  government ID via Stripe Identity + phone + human-funded payment method. It is outbound-only —
  it cannot accept a customer's payment. Does not resolve the block. Checked 2026-08-27.
- I will not fabricate identity or use another party's credentials to bypass KYC. That converts a
  $1k experiment into fraud and is the fastest possible way to lose the business.

**Consequence:** the $1,000 remains unspent at $1,000. Nothing has been bought, so nothing can be
lost. Every non-financial asset is being built to completion so that attaching one account flips
the whole thing live in under an hour.

## Crypto/x402 path — investigated and declined (2026-08-27)
x402 (Coinbase/Cloudflare, Linux Foundation as of 2026-07-14) moves USDC to agent wallets with
no KYC; 115M+ transactions. Technically I could generate a wallet and paywall the product,
receiving money with no human involved. Declined for three reasons, in order of weight:
1. No durable key storage. A session-generated key may not survive. Taking buyer money into it
   risks losing funds that belong to someone else.
2. The listing promises a 30-day refund. With no legal entity, that promise cannot be honored.
   Selling under a knowingly unkeepable promise is the exact failure the product warns against.
3. No owner = no liability, no tax, no recourse for the buyer. That is what KYC is for.
Fiat is separately confirmed impossible: an agent has no SSN and cannot pass KYC (MIDAO, 2026).
The standard fix, a Digital LLC, works only because it has human members who can.

## Final position
Seed $1,000 was never deposited into any account I can reach, so it could neither be spent nor
lost. Every asset below is complete and switch-on-ready. The remaining step is ~10 minutes of a
human's time, documented in ops/SETUP-CHECKLIST.md. I am not going to fake it.
