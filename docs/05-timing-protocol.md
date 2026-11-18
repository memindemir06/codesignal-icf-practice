# 05 — The 90-minute protocol

CodeSignal's own expected-time table (which sums to 90–165 minutes against a 90-minute cap):

| Level | CodeSignal's expected time |
|---|---|
| 1 | 10–15 min |
| 2 | 20–30 min |
| 3 | 30–60 min |
| 4 | 30–60 min |

So the official expectation is that a strong candidate lands somewhere in Level 3 or early
Level 4. **Your plan is to beat that by being fast where speed is cheap.**

---

## The budget you actually run

| Clock | Phase | Target |
|---|---|---|
| 0:00 – 0:04 | **Read & design.** Four-line level brief → pick entity, metric, time-model, L4 shape. Write empty `_resolve` / `_settle` / dataclass. | Nothing passing yet, and that's correct |
| 0:04 – 0:14 | **Level 1.** Type the CRUD. Run tests. Fix. Submit. | L1 green by 0:15 |
| 0:14 – 0:32 | **Level 2.** Ranking + formatting. Run tests. Submit. | L2 green by 0:33 |
| 0:32 – 0:37 | **Refactor window.** Only now, on green. Introduce `_at` delegation, intervals. | Still green |
| 0:37 – 1:05 | **Level 3.** Time/TTL/deferred. Submit after each test goes green. | L3 green by 1:05 |
| 1:05 – 1:25 | **Level 4.** Attack in the order the checklist gives you — cheapest assertions first. | Partial credit ≫ nothing |
| 1:25 – 1:30 | **Stop coding. Submit.** Re-run all four levels. Revert anything that broke an earlier level. | Nothing regressed |

### Hard rules

- **1:25 is a hard stop.** At 1:25 you stop writing new code, run every level's tests, and submit.
  A Level-4 half-edit that breaks Level 3 costs more than Level 4 was worth.
- **If Level 1 isn't green at 0:20, you misread the spec.** Reread the return values. Don't debug
  logic — debug your reading.
- **If you're at 0:45 and Level 2 isn't green**, skip the refactor window entirely and go
  straight at Level 3 with the ugly code. Passing tests is the only currency.
- **Never refactor on red** (T32).
- **Submit at every green transition.** Partial credit is per test.

---

## The first four minutes, scripted

Do these in order, every time. It's a checklist, not improvisation.

1. Read the four one-line level summaries. Say out loud what Level 4 needs
   (*merge? rollback? history?*).
2. Read Level 1 in full. Highlight every **return value** and every **failure condition**.
3. Open the test file. Skim the assertions — confirm return types.
4. Type the class skeleton: dataclass, `_items`, `_alias`, `_pending`, `_resolve`, `_settle`.
5. Type each Level 1 method as a stub with a one-line comment recording its exact return values:
   ```python
   def transfer(self, timestamp, source_account_id, target_account_id, amount):
       # -> new source balance | None if same/missing/insufficient
       ...
   ```
6. Now fill them in.

---

## Triage: what to skip

If you are behind, these are the cheapest things to drop, in order:

1. **Level 4's hardest single assertion.** Merge usually has six sub-requirements — do balance,
   metric, and identity (3 lines, most of the tests) and skip inherited history if it's fighting
   you.
2. **Optimisation.** Always. Linear scans everywhere.
3. **Elegance.** Duplicated code that passes beats a clean abstraction that doesn't exist yet.

What you never skip:

- Running the previous levels' tests before submitting.
- The exact output formatting.
- Guard clauses on existence and self-reference.

---

## Warm-up ritual (day of)

30 minutes before the test:

1. Re-read `docs/02-traps.md` — the whole thing, it's 5 minutes.
2. Type the skeleton from `docs/04-architecture-playbook.md` from memory into a scratch file.
   If you can't do it in under 3 minutes, do it twice.
3. Do `drills/d01_top_n` and `drills/d02_ttl` cold, timed. They're 8 minutes each.
4. Close everything. Water. Toilet. Do not start the test tired.

During the test: no music with words, phone in another room, one browser tab for docs.
