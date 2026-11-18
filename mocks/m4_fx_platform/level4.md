# FX Platform — Level 4

*(Only open this once `./run m4 3` is green.)*

Support consolidating clients, and looking at the past.

* `merge_clients(self, timestamp: int, keep_id: str, drop_id: str) -> bool`
  Merges `drop_id` into `keep_id`. Returns `False` if `keep_id == drop_id` or either
  client doesn't exist. On success:
  * every currency balance of `drop_id` is added to `keep_id`'s;
  * every per-currency outgoing total of `drop_id` is added to `keep_id`'s, so
    `top_spenders` sees the combined history;
  * `keep_id` inherits `drop_id`'s balance history (see below);
  * `drop_id` is removed — every later operation on it fails, and it never appears in
    `top_spenders`.
  * It is guaranteed that a merged-away id is never created again.

* `balance_at(self, timestamp: int, client_id: str, currency: str, time_at: int) -> int | None`
  The client's balance in `currency` as of the **end of** `time_at` — an operation
  processed at exactly `time_at` **is** included. It is guaranteed that
  `time_at <= timestamp`.
  Returns `None` if the client did not exist at `time_at`: before it was created, or
  because it has since been merged away (in which case it returns `None` for every
  `time_at`). Returns `0` for a currency the client had not yet held at `time_at`.

**Inherited history.** After `drop_id` is merged into `keep_id`, for every currency and
every `t >= keep_id.created_at`, `keep_id`'s balance at `t` is *its own balance at `t`*
plus *`drop_id`'s own balance at `t`* (0 where `drop_id` had none). For `t` before
`keep_id` was created the answer stays `None`.

### Examples

| Query | Result |
| --- | --- |
| `create_client(1, "acme")` | `True` |
| `create_client(2, "acme-eu")` | `True` |
| `deposit(3, "acme", "GBP", 1000)` | `1000` |
| `deposit(4, "acme-eu", "EUR", 700)` | `700` |
| `deposit(5, "acme-eu", "GBP", 300)` | `300` |
| `withdraw(6, "acme-eu", "GBP", 100)` | `200` |
| `merge_clients(7, "acme", "acme")` | `False` |
| `merge_clients(8, "acme", "ghost")` | `False` |
| `merge_clients(9, "acme", "acme-eu")` | `True` |
| `get_balance(10, "acme", "GBP")` | `1200` |
| `get_balance(11, "acme", "EUR")` | `700` |
| `get_balance(12, "acme-eu", "GBP")` | `None` |
| `top_spenders(13, "GBP", 5)` | `['acme(100)']` |
| `balance_at(14, "acme", "GBP", 3)` | `1000` |
| `balance_at(15, "acme", "GBP", 5)` | `1300` |
| `balance_at(16, "acme", "EUR", 3)` | `0` |
| `balance_at(17, "acme", "EUR", 4)` | `700` |
| `balance_at(18, "acme", "GBP", 0)` | `None` |
| `balance_at(19, "acme-eu", "GBP", 5)` | `None` |
