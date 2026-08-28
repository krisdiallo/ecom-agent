# Support Macros That Don't Sound Like a Robot

**Use when:** the same 10 tickets keep arriving. **Output:** reusable macros + escalation rules.

---

## Prompt

```
[STORE BRIEF]

Here are my 10 most common support tickets (paste real ones, redact names):

POLICIES (exact, because a macro that contradicts policy costs more than no macro):
- Returns window and who pays return shipping:
- Exchange policy:
- Shipping times, domestic and international:
- What you do when a package is marked delivered but the customer says it wasn't:
- Refund timing:

For each ticket type produce:
1. A macro: acknowledge the specific problem, state what happens next, give a date.
2. The 1–2 variables to fill in (order number, date, item).
3. The condition under which a human must take over instead of sending the macro.

RULES:
- Never apologize twice in one message. Once, specifically, then act.
- Give a date, not "as soon as possible."
- Never promise a refund timeline faster than the policy above.
- An angry customer gets a shorter message, not a longer one.
- If a ticket type reveals a product or logistics defect rather than a communication gap,
  say so — a macro that smooths over a broken product just delays the real fix.
```
