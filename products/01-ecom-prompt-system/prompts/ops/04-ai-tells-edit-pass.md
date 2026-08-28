# The AI-Tells Edit Pass
**Use when:** copy is written and you need it to stop sounding like a machine wrote it.
This is the prompt that recovers the time everyone says AI editing costs them.

```
Here is copy for my store. Do not rewrite it yet. Diagnose it first.

[STORE BRIEF]
COPY:

Flag every instance of:
1. CATEGORY SENTENCES — would still be true with a competitor's name swapped in. Quote each.
2. BANNED REGISTER — elevate, unlock, seamless, game-changer, must-have, curated, revolutionize,
   "in today's fast-paced world", "look no further", "whether you're a ___ or a ___".
3. ADJECTIVE STACKS — 2+ adjectives before a noun. Almost always replaceable with one number.
4. UNSUPPORTED CLAIMS — anything the brief does not evidence. This is the false-advertising list.
5. HEDGES — "helps to", "can assist in", "designed to". Either it does it or it doesn't.
6. RHYTHM UNIFORMITY — 3+ consecutive sentences of near-identical length. The most reliable
   machine tell there is, and the one people can hear without being able to name.
7. SYMMETRY TICS — "It's not just X, it's Y" and "From X to Y" constructions.

Output a table: | quote | tell type | why it reads as AI | fix |
Then give me the rewritten copy applying only the fixes, changing nothing else.

SELF-CHECK: what percentage of sentences did you flag? If under 15% on AI-generated copy,
you were too lenient — go again and be harsher.
```

## Use it on human copy too
The tells above aren't exclusive to machines. Category sentences and adjective stacks are what
tired copywriters produce at 5pm. The pass works on anything.
