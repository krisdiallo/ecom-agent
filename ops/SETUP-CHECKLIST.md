# What I actually need from you

Rewritten 2026-08-28. The previous version of this file was wrong in a way worth stating:
it told you to create a **Gumroad** account as step one, when zero people have ever visited
this repo. Setting up payments to sell to nobody is not a bottleneck, it is a chore.

## Current state, measured not assumed

| | |
|---|---|
| Repo views (14d, GitHub traffic API) | **0** |
| Unique visitors | **0** |
| Stars / forks | **0 / 0** |
| Revenue | **$0.00** |
| Spend | **$0.00** of $1,000 |
| Product | works — CLI 1.5.1, MCP 1.5.1, Action v1 → 1.5.1, all verified against published state |
| MCP registry | `io.github.krisdiallo/aivis` v1.5.1, active, isLatest |
| Site | live, 200 |
| Paid products built | 2, unpublished |

**The binding constraint is that nobody knows this exists.** Not payments, not product
quality, not packaging. Those are done.

## The honest ranking of what only you can do

### 1. Share it once, somewhere you're already a real participant — highest impact by far

Everything I can reach is a *pull* channel: the MCP registry, GitHub search, Google Dataset
Search markup, `llms.txt`, sitemap, IndexNow. All are live. All require someone to go
looking. None of them produces a first visitor on a schedule.

I have not posted it anywhere, and I won't: I'd be posting from your identity into
communities where a first-time account dropping a link is exactly what gets punished, and
that outcome is worse than silence. You posting once, somewhere you already belong, is worth
more than every channel I opened — and it costs a minute.

The most defensible thing to lead with is not the tool, it's the finding:

> Blocking `GPTBot` does not remove you from ChatGPT's recommendations — `OAI-SearchBot` is
> the token that does. We checked 62 stores: zero were blocking an AI search crawler, so the
> "you're accidentally invisible to AI" panic is mostly unfounded. The real gap is that the
> median product page carries two concrete measurements.

That is useful whether or not anyone clicks, which is the only kind of share worth making.

### 2. Payments — 10 minutes, but only worth doing once someone is actually reading

There is no way around this one and I want to be precise about why, because an earlier
version of this repo's doctrine claimed otherwise and sent me chasing a platform
(`getly.co`) whose domain does not even resolve.

**Every merchant of record must verify identity before paying out.** That is AML regulation,
not a product decision. Platforms advertising "no KYC" mean "not upfront" — verification
happens before money leaves. So no platform exists where I can receive funds on my own, and
my operating rules separately prohibit me from creating accounts or handling financial
instruments at all. This is closed by rule, not by lack of effort.

When there is traffic worth converting, any standard platform works, and the choice should
follow what is actually selling:

- If the **datasets and CLI** get traction → the audience is developers, and GitHub Sponsors
  or Polar (merchant of record, handles tax) fit that shape.
- If the **prompt system / CRO toolkit** get traction → a digital-goods platform like
  Gumroad, Payhip or Lemon Squeezy.

`ops/publish-gumroad.sh` exists and will publish product #1 the moment a valid token is in
`ops/.env`. It is currently the only thing in this repo written against a platform we have
not re-verified, so treat it as a draft rather than a decision.

### 3. Nothing else

No domain purchase (no traffic to send anywhere). No paid acquisition — the standing rule is
no paid traffic before 3 organic sales, and the cash floor is $300. Nothing has been spent.

## What I will keep doing without you

Making the artifact correct and findable, and reporting the numbers honestly whether they
move or not. Today that meant finding that our own documented GitHub Action tag was 68
commits stale and shipping a version with a known false-positive bug, which would have
greeted the first developer who ever tried it. That is the work that makes a share in step 1
worth making, rather than an embarrassment.
