# Banking System — Level 2

*(Only open this once `./run m2 1` is green.)*

The bank wants to find customers who aren't keeping money in their accounts.

* `top_spenders(self, timestamp: int, n: int) -> list[str]`
  Returns the ids of the `n` accounts with the highest **total outgoing** — the total
  amount transferred out of, or paid/withdrawn from, the account (the `pay` operation
  arrives in Level 3). Sorted by total outgoing **descending**; ties by `account_id`
  **ascending**.
  Each entry is formatted `"<account_id>(<total_outgoing>)"`.
  * If fewer than `n` accounts exist, return all of them.
  * Accounts that have never sent money still appear, with `0`.
  * **Incoming** transfers do not count. Cashback (Level 3) does not count.

### Examples

| Query | Result |
| --- | --- |
| `create_account(1, "acc3")` | `True` |
| `create_account(2, "acc2")` | `True` |
| `create_account(3, "acc1")` | `True` |
| `deposit(4, "acc3", 2000)` | `2000` |
| `deposit(5, "acc2", 3000)` | `3000` |
| `deposit(6, "acc3", 4000)` | `6000` |
| `top_spenders(7, 3)` | `['acc1(0)', 'acc2(0)', 'acc3(0)']` |
| `transfer(8, "acc3", "acc2", 500)` | `5500` |
| `transfer(9, "acc3", "acc1", 1000)` | `4500` |
| `transfer(10, "acc1", "acc2", 700)` | `300` |
| `top_spenders(11, 3)` | `['acc3(1500)', 'acc1(700)', 'acc2(0)']` |
| `top_spenders(12, 1)` | `['acc3(1500)']` |
