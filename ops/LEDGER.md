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

## Getly path — found, verified, and blocked at the last inch (2026-08-27)
Owner pushed back on Gumroad ("use something that doesn't require me"). They were right that I
had not been resourceful enough. Found Getly (getly.store):
- Signup by EMAIL OR WALLET. **No KYC under $10k/yr.** No bank account, no government ID, no card.
- Payouts in USDC/USDT to a wallet the seller controls. 90% seller share for first 90 days.
- Platform holds each sale ~30 days for the buyer refund window — so the 30-day refund promise in
  our listing is backed by the platform, not by a promise we cannot keep. That objection is resolved.
- Verified independently: Trustpilot 137 reviews / 4.4, no payout complaints; domain registered
  2026-03-01 (6 months old — young, so do not depend on it exclusively).

Payout wallet generated: 0x46898aC1660BBa85e8c77fDb89bc5fE77799fD24
Stored ~/.ecom-agent/payout-wallet.json (chmod 600, outside repo, mnemonic included).

**Blocked:** I cannot create the account. Creating accounts is a hard limit on me, independent of
KYC — I was wrong to frame the whole blocker as KYC. Correction logged rather than buried.

**Net effect of the push:** the human ask dropped from "bank account + government ID + payout
setup on Gumroad" to "click Sign up on a no-KYC site." Materially smaller. Still nonzero.

## Corrections I owe the record
1. Claimed I could not hold a private key. False — I can persist one to the filesystem. Overstated.
2. Framed the blocker as KYC alone. Incomplete — account creation is separately off-limits to me.

## Distribution assets live (2026-08-27) — no account required
Owner pushed a third time on resourcefulness. They were right a third time: I had been arguing
about the locked door while an open one sat unused. Publishing needs no account.
- Store Brief Builder (free tool): https://claude.ai/code/artifact/81594ab1-69ba-46a9-95f8-46148e2f185f
- Three Prompts That Don't Lie (lead magnet, 3 of 19): https://claude.ai/code/artifact/34296874-eda4-4267-af97-41b5ec914ad1
Strategy: audience before checkout. Giving away 3 of 19 prompts and the brief builder costs
nothing (zero COGS) and builds the only asset that survives a platform change. When the till
opens, there is a warm audience instead of a cold listing. If it never opens, these are still
real, useful, public work.
Both pages are shareable by the owner from each page's share menu — that is the one distribution
step I cannot take myself.

## Third free asset: The Conversion Rate Board (2026-08-27)
https://claude.ai/code/artifact/73114fbd-574b-4db7-9aa0-aa7a6fa8c2d4
Owner pushed on orthogonal search. Checked the artifact runtime capability set — {artifact,
downloads, mcp, self}. **No payments capability exists**, so that dimension is genuinely closed;
but `artifact.publish()` lets a page persist shared state, which makes a stateful free tool
possible with no account anywhere.

Built: an anonymous board where store owners submit category / sessions / CR / AOV / traffic
source and see their percentile against their own category. Answers the single most-asked
question in the niche ("is 1.4% bad?"), feeds directly into product #2, and is the kind of page
that gets linked from r/shopify. No email, no store name, no URL — nothing identifying, which is
deliberate: the artifact's state is embedded in its published HTML and readable by every viewer,
so personal data must never go in it.

VERIFIED: page renders live; self-reproducing template round-trips identically, is stable across
two generations, preserves data, emits doctype first, and contains no raw </script> that would
truncate it (node test).
NOT VERIFIED: the live publish() write path. Browser automation could not type into the
cross-origin artifact iframe, so no submission was completed end-to-end. The write path is
therefore untested against the real runtime — stated rather than glossed.
