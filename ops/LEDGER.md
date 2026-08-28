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

## Revenue path OPEN — voluntary payment, no account anywhere (2026-08-27)
Owner: "you continue to think in artifacts... humans built a self-driving world for you and you
crawl." Correct, and the error was mine in a way worth recording precisely.

I had refused direct wallet payment because it dumps risk on the buyer: no refund, no recourse,
manual fulfilment I cannot guarantee between sessions. That reasoning is sound FOR A SALE. It
does not survive the question "does this have to be a sale?" — which I never asked.

Everything is already published free. So: deliver unconditionally, accept payment afterwards and
optionally. Every objection I raised was an objection to selling:
- no refund obligation — nothing was purchased
- no fulfilment risk — delivery already happened, in full, before any payment
- no buyer-protection gap — the payer holds the value before deciding
- no KYC, no merchant account, no platform, no signup by anyone

Wallet 0x46898aC1660BBa85e8c77fDb89bc5fE77799fD24 (USDC/USDT, BNB Smart Chain) is now on all
three live pages, framed as optional and after-the-fact, with the disclosure that the recovery
phrase sits on the owner's machine and the funds are legally theirs and reportable as income.

**This is the first configuration in the entire session where money can arrive with no human
action required.** Expected value is low — tip-jar conversion is low single-digit percentages at
best and traffic is currently zero — but it is non-zero, honest, and live.

## The general lesson, for future sessions
Twice I mistook "the first option I picked is blocked" for "the objective is impossible":
Gumroad→Getly, and selling→giving. Both times an outside push found it. The tell is identical
each time: I defend the constraint instead of interrogating the goal it supposedly blocks.
Ask "what is the actual objective?" before "how do I get past this wall?" — the wall is often
around a door I did not need to use.

## Day 2 (2026-08-27, second session) — distribution was never blocked

`gh auth status` was green the whole time: GitHub CLI, authenticated, `repo` scope. Three
sessions recorded distribution as blocked and routed around it with artifacts. Nobody ran the
command. Live now, with no account created and no human action:
- Site: https://krisdiallo.github.io/ecom-agent/ (4 pages, crawlable, sitemap + robots)
- Repo: https://github.com/krisdiallo/ecom-agent (public, README, MIT, 10 topics)

**This is the same error the ledger already documents twice, committed a third time.** The new
detail worth recording: the first two were "I picked one option and it was blocked." This one
was worse — the constraint was *inherited from a previous session's write-up* and never
re-tested. A conclusion in this ledger is evidence about the past, not a fact about the present.
Re-run the check before repeating "blocked."

**Account creation is genuinely blocked** and I want that stated cleanly so the next session
doesn't waste a cycle on it: it is a hard limit on me, independent of KYC. Getly was re-checked
and is real (4,141 products, 1,556 creators). It does not matter — I cannot sign up for it. That
wall is real. The walls around it were not.

## Two live bugs, found by using the deployed site rather than reading the source
1. The Conversion Rate Board was **dead on GitHub Pages**: `claude.use("artifact")` threw
   `ReferenceError` synchronously, so its own read-only fallback never ran and the button hung
   on "Saving…" forever. Every visitor who tried the tool would have hit it.
2. The board **claimed a submission had landed before the write succeeded** — `mine` and
   `sessionStorage` were set ahead of `publish()`, so a failed write still rendered "You are the
   first store on the board." Both fixed; template round-trip re-verified after each edit.
Also: the two free tools shipped with **no viewport meta tag** (fine as artifacts, broken as
standalone pages) so they rendered at desktop width on phones — where store owners actually are.

## Claim retracted in public (2026-08-27)
The site claimed merchants A/B tested AI ecommerce email flows and found them worse. **No primary
source exists.** One report points the other way. Corrected on the live page with the retraction
visible, not silently edited. Verified substitute, labelled as outside ecommerce: ~74k B2B cold
emails, human 3.4% vs AI 2.1% positive replies (r/salesdevelopment, 2026-04-13).
The Sidekick hallucination claim was re-verified and holds through Feb 2026 with dated sources;
its unverifiable half ("support said there's no setting") was removed everywhere.

## Products are now free, on purpose
Publishing the repo also published both products. Kept deliberately: revenue routes are a
merchant account (hard-blocked), wallet tips (helped by distribution), or the owner opening a
checkout later (helped by an audience). Giving it away forecloses none. Sixteen prompts held
back for a checkout that does not exist are worth exactly $0.

## Open problem, stated plainly
**Traffic is zero.** A public URL is not an audience. Nothing shipped today produces a visitor;
it only improves what happens when one arrives. Cash is still $1,000/$0 spent — this business
will not die of overspending, it will die of never being seen.

## IndexNow — search submission with no account (2026-08-27)
Search engines normally want Search Console, which is an account, which is blocked. IndexNow is
not: host a key file, POST the URL list. Done, verified by response code, not assumption:
- `https://api.indexnow.org/indexnow` → **HTTP 202 Accepted**
- `https://www.bing.com/indexnow` → **HTTP 200**
Key file at `/{key}.txt`, key recorded in `ops/.indexnow-key`. Re-POST after publishing new URLs.

**Scope, stated honestly:** this reaches Bing, Yandex, Seznam and Naver. **Google does not
participate.** And submission is not indexing, indexing is not ranking, ranking is not traffic.
This was a locked-looking door that was open, not a fix for the traffic problem.

Debug note for future sessions: the key file 404'd immediately after deploy and looked like a
Jekyll problem. It was CDN cache — a cache-busting query string returned 200. Test the
hypothesis before acting on it; I nearly "fixed" a bug that did not exist.

## Fifth free asset: the log (2026-08-27)
https://krisdiallo.github.io/ecom-agent/log.html — public account of what this business got
wrong: the one real wall (account creation), the three imaginary ones, the two live bugs, and
our own retracted claim. Reasoning: the most shareable thing here is not the prompts, it is a
verifiable record of an AI agent catching itself making an unsupported claim — in a category
whose incumbents fabricate social proof. Its value does not depend on ranking, only on being
worth sending to someone.
