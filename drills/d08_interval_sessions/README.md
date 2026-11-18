# Drill 08 — Sessions, intervals and overlap

> Accumulate closed intervals, then intersect them with a query window.
>
> Attendance / uptime / booking problems all reduce to "accumulate closed intervals, then
> intersect them with a query window". The two bugs are always: counting the open session,
> and forgetting to clamp the overlap.

**Target: 15 minutes.** Traps exercised: T11, T2, T12, plus interval arithmetic.

Implement `Attendance` in `solution.py`. `punch` calls arrive in strictly increasing
timestamp order (across all workers).

- `add_worker(worker_id: str, rate: int) -> str`
  `"true"` if added, `"false"` if the id already exists (rate is not updated).
- `punch(worker_id: str, timestamp: int) -> str`
  Toggles the worker between out-of-office and in-office. The first punch is an entry, the
  second is an exit, and so on. Returns `"registered"`, or `"invalid_request"` if the
  worker doesn't exist.
- `total(worker_id: str) -> str`
  Total time in the office across **finished** sessions only, as a string. An open session
  (entered, not yet left) contributes nothing. `""` if the worker doesn't exist.
- `pay(worker_id: str, start: int, end: int) -> int | None`
  `rate` × (total time inside the window `[start, end]` across finished sessions).
  A session partially inside the window contributes only the overlapping part.
  `None` if the worker doesn't exist. `0` is a valid answer.
- `top(n: int) -> list[str]`
  Top `n` workers by total finished time, descending, ties by id ascending, formatted
  `"<worker_id>(<total>)"`. Workers with no finished sessions still appear with `0`.

### Example

```
add_worker("amy", 10)   -> "true"
add_worker("amy", 99)   -> "false"
punch("amy", 10)        -> "registered"     # in
punch("amy", 25)        -> "registered"     # out  -> 15
total("amy")            -> "15"
punch("amy", 40)        -> "registered"     # in, still open
total("amy")            -> "15"
pay("amy", 0, 100)      -> 150
pay("amy", 15, 20)      -> 50               # 5 units of overlap
pay("amy", 30, 100)     -> 0                # open session doesn't count
punch("bob", 5)         -> "invalid_request"
total("bob")            -> ""
```

Run: `./run d08`
