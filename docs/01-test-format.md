# 01 — What the ICF test actually is

> Sources: CodeSignal Knowledge Base, *What are the Industry Coding Assessment (ICA) rules?*
> (last updated 2 Aug 2026), CodeSignal *Industry Coding Skills Evaluation Framework*
> technical brief, and three real ICF problem sets in the wild.

## The one-paragraph version

You get **one problem**, split into **four levels**, in **90 minutes**, in a browser IDE, with
**visible unit tests you can run as often as you like**. Each level bolts new requirements onto
the same object you have been building. There is no clever algorithm. The entire test is:
*can you build a small system, then extend it three times without breaking it, fast.*

## Hard facts

| Thing | Value |
|---|---|
| Questions | 1, domain-agnostic, project-based |
| Levels | 4, progressive — each builds on the last |
| Time | 90 minutes total, self-managed across levels |
| Score | **200–600**. 200 = submitted nothing. Higher = more levels passed. |
| Retakes | 2 attempts per rolling 180 days, and only on a new invitation |
| Environment | CodeSignal cloud IDE only. No local IDE. |
| Tests | Visible. You run them. Partial credit per test passed. |
| Internet | Usually allowed for docs/syntax lookup (company-configurable). Assume yes, plan as if no. |
| Language | Your choice from ~25. You picked **Python**. CodeSignal has historically run **3.10.6**. |

**You are not expected to finish.** CodeSignal says so explicitly. The test is calibrated so
that the expected time to do all four properly is 90–165 minutes, and they cap it at 90 to
measure *how far you get*. That reframes everything: this is a **race with partial credit**,
not a puzzle to solve.

## What each level is for

CodeSignal's own description, level by level:

1. **Level 1 — Initial design & basic functions.** Basic implementation operations "while
   accounting for corner cases". CRUD on a dict. The corner cases are the whole point.
2. **Level 2 — Data structures & data processing.** "Calculations or exports": top-N rankings,
   prefix searches, formatted string output, aggregations.
3. **Level 3 — Refactoring & encapsulation.** "Extends the previous functionality to support
   new advanced features." In practice this is nearly always **time**: every operation gains a
   `timestamp`, and things gain a TTL / expiry / scheduled effect.
4. **Level 4 — Extending design & functionality.** "Culminates the project with a further
   extension." In practice: **history** (query the state at a past timestamp), **rollback /
   restore**, or **merge two entities into one**.

> "Given the progressive nature of the requirements, candidates must reuse, encapsulate, and
> refactor earlier code to maintain backward compatibility."

That sentence is the exam. Level 4 is not hard because of Level 4; it is hard because of how you
wrote Level 1.

## The workspace, concretely

- Left pane: the problem statement for **the current level only**. Level 1 shows you a one-line
  summary of all four levels — read those four lines, they are your architecture brief — then
  full detail for Level 1 only.
- You unlock the next level's spec by **passing the current level's tests**.
- It is a *progressive workspace* question: **the question author can change files between
  levels.** New test files appear. Sometimes existing ones are replaced. There is a "view changes
  between levels" diff feature — use it.
- You can run tests per level. Submit early, submit often — partial credit is per test.
- There is a README panel and a code-restore feature (roll your file back to a previous state)
  if you wreck your solution mid-refactor.

## Method signatures are law

Every ICF spec contains a line like *"Please do not change the existing method signatures."*
The tests call your methods by exact name and arity. Rename or reorder a parameter and you lose
every test in that level. Copy signatures character-for-character from the spec.

## What "backward compatibility" means in practice

Level 3 typically introduces `foo_at(timestamp, ...)` alongside the existing `foo(...)`. The
spec will usually say something like: *"each test will not mix both versions, but previously
defined methods must still work as before."*

So Level 1's `set(key, field, value)` must keep working with no notion of time, while
`set_at(key, field, value, timestamp)` is time-aware. The clean move — the one that makes Level 4
tractable — is:

```python
def set(self, key, field, value):
    return self.set_at(key, field, value, timestamp=0)   # or None for "timeless"
```

One implementation, two doors. See `docs/04-architecture-playbook.md`.

## Score, and what "good" is

The score is 200–600 and is essentially a function of how many level tests you pass, weighted by
level. Useful reference points reported by candidates:

- **~300** — Level 1 solid, some of Level 2.
- **~450–480** — Levels 1–2 clean and a working Level 3. Roughly 80th percentile.
- **~500+** — comfortably clears most screens. Levels 1–3 clean plus real progress on 4.
- **600** — all four levels passing.

For practice, **treat 500 as your target and 4 levels as the stretch**. A clean 1-2-3 with
Level 4 half-built beats a scattered attempt at all four with Level 2 broken.

## Sources

- <https://support.codesignal.com/hc/en-us/articles/19116922232983-What-are-the-Industry-Coding-Assessment-ICA-rules>
- <https://codesignal.com/resource/industry-coding-framework/>
- <https://github.com/PaulLockett/CodeSignal_Practice_Industry_Coding_Framework>
- <https://github.com/EricZheng0404/LibreSignal>
