# Scoring — turning 62 checks into one action

## How to score
Each check in `AUDIT.md` is scored **0, 1, or 2**:
- **0** — absent or actively harmful
- **1** — present but weak, buried, or unclear
- **2** — present, clear, and where the buyer needs it

Checks marked **★** are weighted ×3. They are the ones that block purchases rather than
merely dampen them.

## The math
```
Surface score = (points earned / points possible) × 100
```
Score each of the 7 surfaces separately. **Do not average them into one number.** A single
sitewide score hides the fact that one broken surface is doing all the damage — which is
exactly the thing you're auditing to find.

## Reading the result
| Surface score | Read |
|---|---|
| 0–40 | Broken. Fix before spending another dollar on traffic. |
| 41–65 | Leaking. Worth a focused week. |
| 66–85 | Working. Only worth touching once lower surfaces are fixed. |
| 86–100 | Leave it alone and go work on something else. |

## The ranking rule
Sort every check you scored 0 or 1 by:
```
priority = (weight) × (buyers affected) ÷ (hours to fix)
```
Then **do the top three and stop.** Ship them one at a time, with enough sessions between
each to attribute the change. A store that ships fifteen fixes in a week learns nothing
about which of them worked, and has to keep all fifteen forever.

## When the audit says "not a conversion problem"
If Traffic Quality (Surface 1) scores below 40 while Product Page scores above 70, stop
auditing. You are sending the wrong people to a page that works. No amount of copy fixes
that, and the four weeks you'd spend trying is the most expensive outcome of this kit.
