# FX Platform

Your task is to implement a simplified multi-currency payments platform. Plan your design
according to the level specifications below:

* **Level 1:** support creating clients and holding balances in several currencies.
* **Level 2:** support ranking clients by how much they have sent out in a given currency.
* **Level 3:** support FX quotes that expire, and executing conversions against them.
* **Level 4:** support merging two clients, and querying a historical balance.

To move to the next level, pass all the tests at this level.

## Note

Every operation takes a `timestamp` (an integer). Timestamps are unique and operations
arrive in **strictly increasing** timestamp order. All amounts are integers in minor units
(pence, cents) — never use floating point.

---

## Level 1

Implement `FXPlatform` in `solution.py`.

* `create_client(self, timestamp: int, client_id: str) -> bool`
  Creates a client holding nothing. Returns `False` if the client already exists.

* `deposit(self, timestamp: int, client_id: str, currency: str, amount: int) -> int | None`
  Credits `amount` of `currency`. Returns that currency's balance **after** the deposit,
  or `None` if the client doesn't exist.

* `withdraw(self, timestamp: int, client_id: str, currency: str, amount: int) -> int | None`
  Debits `amount` of `currency`. Returns that currency's balance after, or `None` —
  changing nothing — if the client doesn't exist or holds less than `amount` of it.

* `get_balance(self, timestamp: int, client_id: str, currency: str) -> int | None`
  The client's balance in `currency`; `0` for a currency they have never held.
  `None` if the client doesn't exist.

### Examples

| Query | Result |
| --- | --- |
| `create_client(1, "acme")` | `True` |
| `create_client(2, "acme")` | `False` |
| `deposit(3, "ghost", "GBP", 100)` | `None` |
| `deposit(4, "acme", "GBP", 100_000)` | `100000` |
| `deposit(5, "acme", "EUR", 5_000)` | `5000` |
| `get_balance(6, "acme", "GBP")` | `100000` |
| `get_balance(7, "acme", "USD")` | `0` |
| `get_balance(8, "ghost", "GBP")` | `None` |
| `withdraw(9, "acme", "GBP", 100_001)` | `None` |
| `withdraw(10, "acme", "USD", 1)` | `None` |
| `withdraw(11, "acme", "GBP", 40_000)` | `60000` |
