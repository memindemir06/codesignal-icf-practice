# Drill 06 — Merging two entities

> Fold one entity into another. The hardest single Level 4 requirement.
>
> The hardest single Level 4 requirement, and the one that punishes a bad Level 1 design.
> Six separate things must survive the merge. Miss one and you lose several tests.

**Target: 18 minutes.** Traps exercised: T28, T30, T7, T2, and the "additive metric" rule
from `docs/04-architecture-playbook.md`.

Implement `Registry` in `solution.py`. Operation timestamps are strictly increasing.

- `create(timestamp: int, account_id: str) -> bool` — `False` if it exists.
- `deposit(timestamp: int, account_id: str, amount: int) -> int | None` — balance after.
- `transfer(timestamp: int, source: str, target: str, amount: int) -> int | None`
  Returns the **source's** balance after. `None` if source == target, either is missing, or
  funds are insufficient (nothing changes).
- `top_spenders(timestamp: int, n: int) -> list[str]`
  Accounts ranked by **total transferred out**, descending; ties by id ascending.
  Format `"<id>(<total_out>)"`. Accounts with zero outgoing still appear. Fewer than `n`
  accounts → return all.
- `balance_at(timestamp: int, account_id: str, time_at: int) -> int | None`
  Balance as of the **end of** `time_at`. `None` if the account did not exist at `time_at`.
- `merge(timestamp: int, keep_id: str, drop_id: str) -> bool`
  Merges `drop_id` into `keep_id`. `False` if they're equal or either doesn't exist.

### What "merge" must do — the six-line checklist

1. `keep.balance += drop.balance`
2. `keep.outgoing += drop.outgoing` (so `top_spenders` reflects the combined history)
3. `keep` **inherits** `drop`'s balance history: for any `t >= keep.created_at`,
   `balance_at(keep, t)` equals *keep's own balance at t* **plus** *drop's own balance at t*
   (0 if `drop` didn't exist yet at `t`).
4. For `t < keep.created_at`, `balance_at(keep, t)` is still `None` — merging does not
   back-date `keep` into existence.
5. `drop_id` is removed: every later `deposit` / `transfer` / `balance_at` on it returns
   `None`, and it never appears in `top_spenders`.
6. Merges can chain: merging `c` into `b`, then `b` into `a`, must roll everything into `a`.

### Example

```
create(1, "a"); create(2, "b")
deposit(3, "a", 1000)        -> 1000
deposit(4, "b", 500)         -> 500
transfer(5, "a", "b", 200)   -> 800
transfer(6, "b", "a", 100)   -> 600
top_spenders(7, 5)           -> ['a(200)', 'b(100)']
merge(8, "a", "b")           -> True
merge(9, "a", "a")           -> False
merge(10, "a", "ghost")      -> False
top_spenders(11, 5)          -> ['a(300)']
balance_at(12, "a", 12)      -> 1500
balance_at(12, "a", 4)       -> 1500     # a's 1000 + b's 500 at t=4
balance_at(12, "a", 3)       -> 1000     # a's 1000 + b's 0
balance_at(12, "a", 1)       -> 0
balance_at(12, "a", 0)       -> None
balance_at(12, "b", 4)       -> None     # b is gone
deposit(13, "b", 1)          -> None
```

Run: `./run d06`
