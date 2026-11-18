# FX Platform — Level 2

*(Only open this once `./run m4 1` is green.)*

Compliance wants to see who is moving money out.

* `top_spenders(self, timestamp: int, currency: str, n: int) -> list[str]`
  The `n` clients with the highest **total outgoing** in `currency` — the total amount of
  that currency withdrawn (and, from Level 3, converted away). Sorted descending; ties by
  `client_id` **ascending**. Each entry is formatted `"<client_id>(<total>)"`.
  * Every existing client appears, even with `0`, and even if they have never held that
    currency.
  * If fewer than `n` clients exist, return all of them.
  * Deposits never count. Failed withdrawals never count.

### Examples

| Query | Result |
| --- | --- |
| `create_client(1, "beta")` | `True` |
| `create_client(2, "acme")` | `True` |
| `deposit(3, "acme", "GBP", 1000)` | `1000` |
| `deposit(4, "beta", "GBP", 1000)` | `1000` |
| `deposit(5, "beta", "EUR", 1000)` | `1000` |
| `top_spenders(6, "GBP", 5)` | `['acme(0)', 'beta(0)']` |
| `withdraw(7, "acme", "GBP", 300)` | `700` |
| `withdraw(8, "beta", "EUR", 900)` | `100` |
| `top_spenders(9, "GBP", 5)` | `['acme(300)', 'beta(0)']` |
| `top_spenders(10, "EUR", 5)` | `['beta(900)', 'acme(0)']` |
| `top_spenders(11, "USD", 5)` | `['acme(0)', 'beta(0)']` |
| `top_spenders(12, "GBP", 1)` | `['acme(300)']` |
