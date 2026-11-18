# Drill 10 — The Level-3 refactor, in isolation

> Extend a working Level 1+2 into Level 3 without breaking it.
>
> This drill is different: **`solution.py` already contains a working Level 1 + 2.**
> Your job is the thing the exam actually scores — extending it without breaking it.

**Target: 15 minutes.** Traps exercised: T26, T21, T19, T20, T32, T33.

A feature-flag service. The existing (timeless) API is already implemented and its tests
already pass:

- `enable(account, flag) -> str` → `""`
- `disable(account, flag) -> str` → `"true"` if the flag was on, else `"false"`
- `is_enabled(account, flag) -> str` → `"true"` / `"false"`
- `list_flags(account, prefix) -> str` → enabled flags starting with `prefix`, sorted
  ascending, joined with `", "`; `""` if none

### Your task — add the time-aware variants

- `enable_at(account, flag, timestamp) -> str` → `""`, no expiry
- `enable_at_with_ttl(account, flag, timestamp, ttl) -> str` → `""`, enabled on
  `[timestamp, timestamp + ttl)`. Re-enabling **resets** the lifetime.
- `disable_at(account, flag, timestamp) -> str` → `"true"` if it was enabled **and alive**
  at `timestamp`, else `"false"`
- `is_enabled_at(account, flag, timestamp) -> str` → `"true"` / `"false"`
- `list_flags_at(account, prefix, timestamp) -> str` → only flags alive at `timestamp`

### The constraint that makes it a drill

`./run d10 12` must **stay green** the entire time. The timeless methods keep their exact
old behaviour: no expiry, no timestamps, and a flag enabled by `enable()` is on forever.

Do it the right way — **one implementation, two doors** (see
`docs/04-architecture-playbook.md`). If you end up with two parallel code paths you've
done the exam-losing version.

```
./run d10 12     # the existing tests -- must never go red
./run d10 3      # the new tests -- make these green
./run d10        # both
./run reset d10  # put solution.py back to the starting Level 1+2 code
```
