# Banking System

Your task is to implement a simplified banking system. Plan your design according to the
level specifications below:

* **Level 1:** support creating accounts, depositing money, and transferring money between
  two accounts.
* **Level 2:** support ranking accounts by outgoing transactions.
* **Level 3:** support payments with cashback, and checking the status of a payment.
* **Level 4:** support merging two accounts, and querying an account's balance at a past
  point in time.

To move to the next level, pass all the tests at this level.

## Note

All operations take a `timestamp` parameter: an integer number of **milliseconds**. All
timestamps are unique, in the range `1` to `10^9`, and operations arrive in **strictly
increasing** timestamp order.

---

## Level 1

Implement `BankingSystem` in `solution.py`.

* `create_account(self, timestamp: int, account_id: str) -> bool`
  Creates an account with balance `0`. Returns `True`, or `False` if an account with that
  id already exists.

* `deposit(self, timestamp: int, account_id: str, amount: int) -> int | None`
  Returns the balance of the account **after** the deposit, or `None` if the account
  doesn't exist.

* `transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None`
  Moves `amount` from source to target. Returns the balance of **`source_account_id`**
  after the transfer. Returns `None`, changing nothing, if:
  * `source_account_id` or `target_account_id` doesn't exist, **or**
  * `source_account_id == target_account_id`, **or**
  * the source has insufficient funds.

### Examples

| Query | Result |
| --- | --- |
| `create_account(1, "acc1")` | `True` |
| `create_account(2, "acc1")` | `False` |
| `create_account(3, "acc2")` | `True` |
| `deposit(4, "nope", 2700)` | `None` |
| `deposit(5, "acc1", 2700)` | `2700` |
| `transfer(6, "acc1", "acc2", 2701)` | `None` — insufficient funds |
| `transfer(7, "acc1", "acc1", 10)` | `None` — same account |
| `transfer(8, "acc1", "acc2", 200)` | `2500` |
