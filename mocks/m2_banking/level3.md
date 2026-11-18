# Banking System — Level 3

*(Only open this once `./run m2 2` is green.)*

Support withdrawals with cashback.

`MILLISECONDS_IN_1_DAY = 86400000`

* `pay(self, timestamp: int, account_id: str, amount: int) -> str | None`
  Withdraws `amount` from the account. Every withdrawal earns **2% cashback, rounded down
  to the nearest integer**, refunded to the account exactly `MILLISECONDS_IN_1_DAY`
  milliseconds later (at `timestamp + 86400000`).
  Returns a unique identifier `"payment<k>"` where `k` is the ordinal number of
  **successful** withdrawals across all accounts — `"payment1"`, `"payment2"`, …
  Returns `None`, changing nothing and consuming no identifier, if:
  * `account_id` doesn't exist, **or**
  * the account has insufficient funds.

* `get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None`
  Returns `"IN_PROGRESS"` or `"CASHBACK_RECEIVED"`. Returns `None` if:
  * `account_id` doesn't exist, **or**
  * `payment` doesn't exist, **or**
  * `payment` belongs to a different account.

Additional rules:

* `top_spenders` must now also count money withdrawn by `pay`. Cashback refunds never
  count as outgoing.
* When cashback becomes due, it must be credited **before** any other operation performed
  at that timestamp. So an operation at exactly `timestamp + 86400000` already sees the
  refund.

### Examples

| Query | Result |
| --- | --- |
| `create_account(1, "acc1")` | `True` |
| `create_account(2, "acc2")` | `True` |
| `deposit(3, "acc1", 2000)` | `2000` |
| `pay(4, "acc1", 1000)` | `"payment1"` |
| `pay(100, "acc1", 1000)` | `"payment2"` |
| `pay(101, "acc1", 1)` | `None` — no funds left |
| `get_payment_status(102, "nope", "payment1")` | `None` |
| `get_payment_status(103, "acc2", "payment1")` | `None` — wrong account |
| `get_payment_status(104, "acc1", "payment1")` | `"IN_PROGRESS"` |
| `top_spenders(105, 2)` | `['acc1(2000)', 'acc2(0)']` |
| `deposit(3 + DAY, "acc1", 100)` | `100` — no cashback yet |
| `get_payment_status(4 + DAY, "acc1", "payment1")` | `"CASHBACK_RECEIVED"` |
| `deposit(5 + DAY, "acc1", 100)` | `220` — 20 cashback from payment1 landed |
| `deposit(99 + DAY, "acc1", 100)` | `320` |
| `deposit(100 + DAY, "acc1", 100)` | `440` — 20 cashback from payment2 landed |
