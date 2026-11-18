# Drill 04 — Deferred effects (the cashback pattern)

> The cashback pattern: something you do now takes effect later.
>
> The classic ICF Level 3. Something you do now takes effect later, and every subsequent
> operation must see it. Get the `_settle()` discipline into your fingers.

**Target: 15 minutes.** Traps exercised: T23, T24, T22, T3, T11.

Implement `Rewards` in `solution.py`. Timestamps are integers, strictly increasing across
calls. `WAIT = 3600`.

- `open_account(timestamp: int, account_id: str) -> bool`
  `False` if it already exists.

- `deposit(timestamp: int, account_id: str, amount: int) -> int | None`
  Returns the balance **after** the deposit, or `None` if the account doesn't exist.

- `spend(timestamp: int, account_id: str, amount: int) -> str | None`
  Withdraws `amount`. Grants **5% cashback, rounded down**, credited back to the account
  exactly `WAIT` ticks later (at `timestamp + WAIT`).
  Returns a unique id `"reward1"`, `"reward2"`, … numbered by the order of **all successful
  spends across all accounts**. Returns `None` if the account doesn't exist or has
  insufficient funds (and in that case nothing happens and no id is consumed).

- `reward_status(timestamp: int, account_id: str, reward_id: str) -> str | None`
  `"PENDING"` or `"PAID"`. `None` if the account doesn't exist, the reward doesn't exist,
  or the reward belongs to a different account.

- `balance(timestamp: int, account_id: str) -> int | None`

**The rule that decides this drill:** a cashback due at time `T` must already be credited
for *any* operation performed at time `T`. Settle pending rewards as the first statement of
every public method.

### Example

```
open_account(1, "a")        -> True
deposit(2, "a", 1000)       -> 1000
spend(3, "a", 250)          -> "reward1"      # 5% of 250 = 12 (floor), due at 3603
spend(4, "a", 90)           -> "reward2"      # 5% of 90 = 4 (floor), due at 3604
spend(5, "a", 10000)        -> None           # insufficient funds
reward_status(6, "a", "reward1")  -> "PENDING"
balance(7, "a")             -> 660
balance(3602, "a")          -> 660
balance(3603, "a")          -> 672            # reward1 credited AT 3603
reward_status(3603, "a", "reward1") -> "PAID"
reward_status(3603, "a", "reward2") -> "PENDING"
balance(3604, "a")          -> 676
```

Run: `./run d04`
