# 02 — The trap catalogue

Every one of these has cost real candidates real levels. Read this the morning of the test.
The drills in `drills/` are built to make you fail these once, here, instead of there.

---

## A. Spec-reading traps

**T1 — The four-line brief in Level 1 is the architecture spec.**
Level 1 tells you all four level *titles* ("Level 4: should support merging two accounts while
retaining both accounts' balance and transaction histories"). That is a free look at the future.
If you read "merge" you know identity must be indirectable. If you read "TTL" you know values
need intervals, not scalars. Spend 90 seconds on those four lines before writing anything.

**T2 — Return type is not what you assume.**
Real ICF specs return: `""` (empty string) not `None`; `"true"`/`"false"` **as strings** not
booleans; `None` in one problem and `-1` in another for "not found". The in-memory DB problem
returns `"true"`/`"false"` strings from `delete`. The banking problem returns real `bool`.
**Grep the spec for the literal return values and write them into your stub docstrings first.**

**T3 — "Returns X if the operation was successful" hides which X.**
`transfer` returns *the source account's balance after the transfer*, not the amount, not `True`.
`deposit` returns *the balance after*. Getting this wrong passes zero tests while your logic is
perfect.

**T4 — Formatted-string outputs have exact punctuation.**
`"account1(2500)"`, joined by `", "` — comma **and space**. `"BC(E), BD(F)"`. No trailing
separator. Some problems want a single joined string, others want a `list[str]`. Read twice.

**T5 — Silent invariants in the "Note" block.**
"It is guaranteed that all timestamps are unique and strictly increasing." That guarantee is a
gift — it means you can process lazily and never sort. Losing it (some problems allow arbitrary
`time_at` in queries) means you *must* keep history. Always find the Note block.

**T6 — Tests are visible and are the real spec.**
"Please check tests for requirements and argument types." When the prose and the test disagree,
**the test wins**. If a level is failing and you can't see why, open the test file and read the
assertion.

---

## B. Level 1 corner-case traps

**T7 — Self-referential operations.** `transfer(a, a, x)` → fail. `merge(a, a)` → fail.
`copy(f, f)` → usually a no-op that still counts as success. Explicitly handle "source == target".

**T8 — Existence checks in the right order.** Check *both* entities exist before mutating
either. A half-applied transfer (debited, never credited) poisons every later test in the file.

**T9 — Overwrite vs. reject.** `FILE_UPLOAD` **throws** if the name exists. `FILE_COPY`
**overwrites** if the destination exists. Same problem, opposite policies, two lines apart.

**T10 — "Returns nothing".** In Python that's `return None`, and the test may assert
`assertIsNone` — not `assertEqual(result, "")`. Conversely some specs literally mean `""`.

**T11 — Insufficient funds / over-capacity is a *rejection*, not a clamp.** Don't partially
apply. Don't go negative. Return the failure value and leave state untouched.

**T12 — Zero and equal-value edge cases.** `n=0` in a top-N. Amount `0`. Empty prefix (matches
everything). A tie between every single entity. Ranking when nothing has any activity yet — the
banking spec expects `['account1(0)', 'account2(0)', 'account3(0)']`, i.e. **entities with zero
activity still appear**, sorted alphabetically.

---

## C. Level 2 ranking / processing traps

**T13 — The tie-break is always there and always specific.**
"Descending by value, **and in case of a tie, ascending alphabetically by id**." In Python:
```python
sorted(items, key=lambda kv: (-kv[1], kv[0]))
```
Never `sorted(..., reverse=True)` on a tuple — that reverses the tie-break too, which is wrong.

**T14 — Fewer than N entities.** "If less than n accounts exist, return all of them." Slicing
handles this for free (`[:n]`); building a heap of exactly n does not.

**T15 — Which entities are in the ranking pool?**
All of them, or only the ones matching a filter (`TOP_N_WORKERS n position` — only that
position)? Only *alive* ones (TTL problems)? Only ones that ever transacted, or all created ones?
Reread.

**T16 — What counts toward the metric.**
Banking: outgoing = transfers out **plus** payments/withdrawals, but **cashback received does not
count** and incoming transfers do not count. These carve-outs are stated once, in a sub-bullet,
and are tested.

**T17 — Prefix search is on the right field.** `scan_by_prefix(key, prefix)` filters **fields**
within one record, not keys. `FILE_SEARCH(prefix)` filters **file names** globally. Not the same
shape at all.

**T18 — Sort by size descending, then by *name*, then take 10.** Hardcoded limits ("top 10")
show up as literals in the spec. Don't invent a parameter.

---

## D. Level 3 time / TTL traps

**T19 — Half-open intervals.** TTL means alive during `[timestamp, timestamp + ttl)`. At exactly
`timestamp + ttl` it is **dead**. The DB spec spells this out; the file spec doesn't but tests it.
Write `t < expiry`, never `t <= expiry`.

**T20 — Re-setting a value with a TTL resets the clock.** `set_at_with_ttl(k, f, v, 5, 10)` after
`set_at_with_ttl(k, f, v, 1, 9)` → expires at 15, not 10. Overwrite replaces the interval.

**T21 — No TTL means infinite, not zero.** Represent it as `math.inf` so the same `t < expiry`
comparison works for both. Do not special-case `None` in five places.

**T22 — Expiry is lazy, not eventful.** Nothing "runs" at the expiry timestamp. You are only ever
asked questions at some `t`; filter at read time. Do not try to schedule deletions.

**T23 — Deferred credits must be applied *before* the query at that timestamp.**
Banking cashback: "the amount must be refunded to the account **before any other transactions**
are performed at the relevant timestamp." So `deposit(t=3+DAY)` — a cashback due at exactly
`3+DAY` has *already landed*. Pattern: every public method starts with
`self._settle_pending(timestamp)`.
And note the boundary in the worked example: cashback for a payment at t=3 lands at `3+DAY`, so a
deposit at `3+DAY` sees it, and a deposit at `2+DAY` does not.

**T24 — Rounding.** "2% of the withdrawn amount **rounded down**." That's `amount * 2 // 100`
(integer floor), not `round()`, not `int()` on a float — `int(-0.5)` and floats will bite you.
Keep money in integer minor units and never touch `float`.

**T25 — Timestamps arrive strictly increasing for *operations*, but query arguments may be any
time.** `get_balance(timestamp=16, account_id, time_at=11)` looks backwards. `restore(10, 7)`
looks backwards. Operation order ≠ argument order.

**T26 — The `_at` variants must not break the non-`_at` ones.** Some problems run L1/L2 tests
again at L3. If you rewrote `get()` to require a timestamp, you just lost Levels 1 and 2.

---

## E. Level 4 traps

**T27 — Rollback must recalculate TTLs.** After `restore(now, target)`, an item that had 6 units
of life left at backup time now expires at `now + 6`. You must store **remaining lifespan**, not
absolute expiry, in the snapshot. (Or store absolute + the backup timestamp and do the arithmetic
on restore.)

**T28 — Merge must preserve *history*, not just balance.**
- Balance of B adds to A. ✅ (easy)
- B's **outgoing totals** add to A's ranking metric. ✅ (needs the metric to be per-entity data,
  not derived)
- B's **pending scheduled effects** (cashback) still fire, but land on **A**. ✅ (needs the
  pending record to point at an entity you can re-target)
- B's **payment ids** must still be queryable **under A's name**. ✅ (needs an alias map)
- B must be **gone** — every lookup of B returns not-found afterwards. ✅
- B's **balance history** is inherited by A for point-in-time queries. ✅

  That's six separate assertions. Build merge as six explicit lines, one per bullet.

**T29 — Point-in-time queries include the operation at that exact timestamp.**
"If queries have been processed at timestamp `time_at`, `get_balance` must reflect the balance
**after** the query has been processed." So it's `<= time_at`, not `<`. Opposite of the TTL rule
in T19. Both appear in the same problem. This is the single most common Level-4 off-by-one.

**T30 — Point-in-time queries must respect lifecycle.** Before the entity was created → `None`.
After it was merged away → `None`. Not "0". The banking spec tests both explicitly.

**T31 — History must include *deferred* effects.** `get_balance(t, acct, time_at)` where a
cashback landed between then and now must include the cashback if it landed at or before
`time_at`. So the history log has to be appended to when cashback settles, at the settle
timestamp — not at the payment timestamp.

---

## F. Process traps

**T32 — Refactoring at Level 3 with no tests green.** Never refactor on red. Get the level
passing ugly, run tests, *then* clean up. You can restore code to a previous state in the IDE,
but you can't get the 12 minutes back.

**T33 — Rewriting instead of extending.** The clock says extend. If you're deleting more than
~15 lines to add a feature, you took a wrong turn at Level 1.

**T34 — Optimising.** `n ≤ 10^4`-ish and a 3-second limit. A linear scan for top-N is fine. A
full re-sort per query is fine. Reach for a heap only if the spec screams volume. Time spent on
`O(log n)` is time not spent on Level 4.

**T35 — Not submitting.** Partial credit is per test. Submit at the end of every level and again
whenever a new test goes green. A crashed final edit with nothing submitted scores 200.

**T36 — Forgetting the tests change between levels.** New test files appear when a level unlocks.
If Level 2's tests suddenly reference a method you haven't seen in the prose, use the diff view.
