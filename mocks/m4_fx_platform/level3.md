# FX Platform — Level 3

*(Only open this once `./run m4 2` is green.)*

Support FX quotes. A quote fixes a rate for a limited window; a client converts money by
executing against a live quote.

* `quote(self, timestamp: int, from_currency: str, to_currency: str, rate_pips: int, ttl: int) -> str`
  Publishes a quote, live during `[timestamp, timestamp + ttl)` — it is **dead at exactly
  `timestamp + ttl`**. Returns a unique identifier `"quote<k>"` numbered by the order of
  all quotes published: `"quote1"`, `"quote2"`, …

* `execute(self, timestamp: int, client_id: str, quote_id: str, amount: int) -> int | None`
  Converts `amount` of the quote's `from_currency` into
  `amount * rate_pips // 10000` of its `to_currency` (integer division — **round down**).
  Returns the client's balance in `to_currency` **after** the conversion.
  Returns `None`, changing nothing, if:
  * `client_id` doesn't exist, **or**
  * `quote_id` doesn't exist, **or**
  * the quote is not live at `timestamp`, **or**
  * the client holds less than `amount` of `from_currency`.

  A successful `execute` counts `amount` toward the client's outgoing total in
  `from_currency` for `top_spenders`. The `to_currency` side never counts as outgoing.
  A quote may be executed any number of times while it is live, by any client.

### Examples

Rates are in **pips**: `11750` means 1.1750, so 1000 units convert to
`1000 * 11750 // 10000 = 1175`.

| Query | Result |
| --- | --- |
| `create_client(1, "acme")` | `True` |
| `deposit(2, "acme", "GBP", 10_000)` | `10000` |
| `quote(3, "GBP", "EUR", 11750, 100)` | `"quote1"` |
| `quote(4, "EUR", "USD", 10500, 100)` | `"quote2"` |
| `execute(5, "acme", "quote1", 1000)` | `1175` — EUR balance |
| `execute(6, "acme", "quote1", 3)` | `1178` — `3 * 11750 // 10000 == 3` |
| `execute(7, "acme", "quote9", 10)` | `None` — no such quote |
| `execute(8, "ghost", "quote1", 10)` | `None` |
| `execute(9, "acme", "quote2", 5000)` | `None` — only 1178 EUR held |
| `execute(10, "acme", "quote2", 1000)` | `1050` — USD balance |
| `get_balance(11, "acme", "GBP")` | `8997` |
| `top_spenders(12, "GBP", 5)` | `['acme(1003)']` |
| `top_spenders(13, "EUR", 5)` | `['acme(1000)']` |
| `execute(102, "acme", "quote1", 10)` | `8987` — quote1 is live until 103 |
| `execute(103, "acme", "quote1", 10)` | `None` — quote1 died at exactly 103 |
