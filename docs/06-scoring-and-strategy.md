# 06 — Score, triage, and what to do when it goes wrong

## What the number means

Your ICF **Coding Score** is 200–600. It is essentially "how far did you get", weighted by
level and by tests passed within a level. Only submitting nothing gives 200.

| You got | Roughly | Practice benchmark |
|---|---|---|
| L1 only | ~300 | Below bar for a mid/senior screen |
| L1 + most of L2 | ~380–420 | Borderline |
| L1–L2 clean, L3 working | ~450–500 | Solid pass at most companies |
| L1–L3 clean, L4 partial | ~500–550 | Strong |
| All four | ~600 | Top decile |

**Target 500.** That means: Levels 1–3 fully green and a visible dent in Level 4. Aiming
for 600 and getting a broken Level 2 scores worse than aiming for 500 and getting it.

Two attempts per 180 days, and only on a new invitation — so treat this as one shot.

## The three ways people lose points they had already earned

1. **Breaking an earlier level while writing a later one.** Run every level's tests before
   each submit. This is the single biggest avoidable loss.
2. **Not submitting.** Partial credit is per test. Submit at every green transition and
   again at 1:25 whatever state you're in.
3. **Perfecting Level 2.** A beautiful ranking implementation is worth exactly the same as
   an ugly one that passes.

## When you're stuck: a decision tree

**Level 1 tests failing and the logic looks right**
→ It's a return-value mismatch. Open the test file, read the assertion, match it exactly.
`assertIsNone` vs `assertEqual(x, "")` vs `assertIs(x, False)` are three different things.

**Level 2 ranking is off by exactly the ordering**
→ You used `reverse=True` on a tuple key. Negate the numeric part instead:
`key=lambda kv: (-kv[1], kv[0])`.

**Level 3 off by one at a boundary**
→ TTL is half-open: alive iff `start <= t < expiry`. Deferred effects settle at
`due <= t`. Those two are the whole boundary surface.

**Level 3 broke Levels 1 and 2**
→ You changed a signature or made the timeless path require a timestamp. Use the sentinel
delegation from `docs/04-architecture-playbook.md`.

**Level 4 merge passes some assertions, not others**
→ Go through the six-line checklist literally: balance, metric, history, identity/alias,
removal, chaining. Each is one line. Find the missing line.

**Level 4 rollback restores the wrong lifetimes**
→ You stored absolute expiry. Store **remaining lifespan** at backup time and re-base it
at restore time.

**You have 15 minutes left and Level 4 is a mess**
→ `git`-style triage: revert Level 4 entirely (the IDE has code restore), confirm 1–3 are
green, submit. Then re-add only the single cheapest Level-4 method with the time left.

## What "good code" is worth here

CodeSignal says the framework measures "software design patterns, code implementation,
problem solving, data structures and data processing, and maintaining codebases via
refactoring and encapsulation". In practice the score is computed from tests. Design is
measured **indirectly** — a good design is what lets you reach Level 4 inside 90 minutes.

So: write the design that makes you fast, not the design that would impress a reviewer.
Concretely, that's:

- one dataclass per entity, with the ranking metric as a field;
- one `_settle(timestamp)` called first in every public method;
- one `_resolve(id)` used for every internal id lookup;
- private helpers doing the work, public methods being one-liners that delegate.

That is also, not coincidentally, the design a reviewer would like.

## The night before

- Do **not** attempt a new mock. Re-read `docs/02-traps.md` and sleep.
- Check your machine: stable internet, charger, no updates pending. CodeSignal is
  browser-based and proctored; a disconnect mid-test is your problem.
- Know the environment: cloud IDE only, no local IDE, internet usually permitted for
  documentation lookup. Have the Python docs open in one tab and nothing else.

## During

- 4 minutes reading and designing, then type.
- Submit at every green transition.
- Hard stop at 1:25.
- If you finish all four early, spend the remainder re-running every level, not polishing.
