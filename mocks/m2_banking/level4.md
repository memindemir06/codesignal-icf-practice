# Banking System — Level 4

*(Only open this once `./run m2 3` is green.)*

Support merging accounts, and querying historical balances.

* `merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool`
  Merges `account_id_2` **into** `account_id_1`. Returns `True`, or `False` if
  `account_id_1 == account_id_2` or either account doesn't exist. On success:
  * `account_id_2`'s balance is added to `account_id_1`'s;
  * `top_spenders` sees the **sum** of both accounts' total outgoing;
  * pending cashback owed to `account_id_2` is still refunded, but lands on
    `account_id_1`;
  * `account_id_2`'s payment identifiers become queryable under `account_id_1`;
  * `account_id_1` inherits `account_id_2`'s balance history (see below);
  * `account_id_2` is removed from the system — every later operation on it fails.
  * It is guaranteed that a merged-away id is never created again.

* `get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None`
  Returns the balance of `account_id` as of the **end of** `time_at` — if an operation was
  processed at exactly `time_at`, its effect **is** included.
  It is guaranteed that `time_at <= timestamp`.
  Returns `None` if the account did not exist at `time_at`, which includes:
  * `time_at` is before the account was created;
  * the account has since been merged away (it returns `None` for *every* `time_at`);
  * the account never existed.

**Inherited history.** After `account_id_2` is merged into `account_id_1` at time `m`, for
any `t >= account_id_1.created_at` the balance of `account_id_1` at `t` is
*`account_id_1`'s own balance at `t`* **plus** *`account_id_2`'s own balance at `t`*
(counting `0` if `account_id_2` did not exist yet at `t`). For `t` before
`account_id_1` was created, the answer is still `None` — merging does not back-date an
account into existence.

### Examples

| Query | Result |
| --- | --- |
| `create_account(1, "acc1")` | `True` |
| `create_account(2, "acc2")` | `True` |
| `deposit(3, "acc1", 2000)` | `2000` |
| `deposit(4, "acc2", 3000)` | `3000` |
| `pay(5, "acc1", 500)` | `"payment1"` |
| `transfer(6, "acc1", "acc2", 500)` | `1000` |
| `merge_accounts(7, "acc1", "nope")` | `False` |
| `merge_accounts(8, "acc1", "acc1")` | `False` |
| `merge_accounts(9, "acc1", "acc2")` | `True` |
| `get_balance(10, "acc1", 10)` | `4500` |
| `get_balance(11, "acc2", 10)` | `None` — acc2 is gone |
| `get_balance(12, "acc2", 4)` | `None` — even though it existed then |
| `get_payment_status(13, "acc1", "payment1")` | `"IN_PROGRESS"` |
| `get_balance(14, "acc1", 3)` | `2000` — acc1's 2000 + acc2's 0 |
| `get_balance(15, "acc1", 4)` | `5000` — acc1's 2000 + acc2's 3000 |
| `top_spenders(16, 5)` | `['acc1(1000)']` |
| `deposit(5 + DAY, "acc1", 100)` | `4610` — 10 cashback from payment1, then 100 |
