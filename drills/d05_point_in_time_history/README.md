# Drill 05 — Point-in-time queries

> "What was the balance at time X?" and its notorious off-by-one.
>
> "What was the balance at time X?" is a standard Level 4 requirement, and it has a
> notorious off-by-one that is the *opposite* of the TTL one you learned in Drill 02.

**Target: 15 minutes.** Traps exercised: T29, T30, T25, T5.

Implement `Ledger` in `solution.py`. Operation timestamps are strictly increasing.
The `time_at` **argument** may be any value — past, present, or future.

- `open(timestamp: int, account_id: str) -> bool`
  `False` if it already exists. A new account has balance `0`.

- `credit(timestamp: int, account_id: str, amount: int) -> int | None`
  Returns the balance after, or `None` if missing.

- `debit(timestamp: int, account_id: str, amount: int) -> int | None`
  Returns the balance after, or `None` if the account is missing **or** has insufficient
  funds (nothing changes in that case).

- `close(timestamp: int, account_id: str) -> bool`
  Removes the account. `False` if it doesn't exist. After closing, the id may be reopened
  by `open` and starts fresh from `0`.

- `balance_at(timestamp: int, account_id: str, time_at: int) -> int | None`
  The balance of the account **as of the end of** `time_at` — i.e. if an operation was
  processed at exactly `time_at`, its effect **is** included.
  Returns `None` if the account did not exist at `time_at`:
  - `time_at` is before it was opened → `None`
  - `time_at` is at or after it was closed → `None`
    (an account closed at `t` still has a balance *at* `t`? **No** — treat the close as
    taking effect at `t`, so `balance_at(..., t)` is `None`.)

### Example

```
open(1, "a")                -> True
credit(2, "a", 100)         -> 100
credit(5, "a", 50)          -> 150
debit(7, "a", 30)           -> 120
debit(8, "a", 999)          -> None
balance_at(9, "a", 0)       -> None      # before it existed
balance_at(9, "a", 1)       -> 0
balance_at(9, "a", 2)       -> 100       # includes the op AT time_at
balance_at(9, "a", 4)       -> 100
balance_at(9, "a", 8)       -> 120       # the failed debit changed nothing
balance_at(9, "a", 100)     -> 120       # future time_at = current state
close(10, "a")              -> True
balance_at(11, "a", 9)      -> 120
balance_at(11, "a", 10)     -> None      # closed at 10
balance_at(11, "a", 11)     -> None
```

Run: `./run d05`
