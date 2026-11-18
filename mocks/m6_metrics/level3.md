# Metrics Service — Level 3

*(Only open this once `./run m6 2` is green.)*

Storage is expensive. Support per-metric retention.

* `set_retention(self, timestamp: int, metric: str, ttl: int) -> bool`
  Sets the retention for `metric`. A sample recorded at time `t` is **visible** at query
  time `q` if and only if `q - t < ttl`; once it is `ttl` or more old it is invisible.
  Returns `False` if the metric doesn't exist. Calling it again **replaces** the previous
  retention. A metric with no retention set keeps every sample visible forever.

From this level on, **every read counts only visible samples**:

* `latest` returns the most recent **visible** value, else `None`.
* `summary` aggregates only visible samples inside the window.
* `top_metrics` ranks by **visible** sample count — a metric whose samples have all aged
  out still appears, with `0`.
* `record` returns the number of **visible** samples the metric holds after recording
  (the sample just recorded is always visible, so this is never `0`).

A metric whose samples have all aged out still **exists**: `set_retention` and `remove`
still return `True` for it.

### Examples

| Query | Result |
| --- | --- |
| `record(10, "cpu", 40)` | `1` |
| `record(20, "cpu", 60)` | `2` |
| `set_retention(21, "cpu", 15)` | `True` |
| `set_retention(22, "disk", 15)` | `False` |
| `record(25, "cpu", 50)` | `2` — the sample from 10 is 15 old, so invisible |
| `latest(26, "cpu")` | `50` |
| `summary(26, "cpu", 100)` | `"min(50) max(60) avg(55)"` |
| `summary(35, "cpu", 100)` | `"min(50) max(50) avg(50)"` |
| `top_metrics(41, 5)` | `['cpu(0)']` |
| `latest(41, "cpu")` | `None` |
| `set_retention(42, "cpu", 1000)` | `True` — nothing was deleted, it all comes back |
| `latest(43, "cpu")` | `50` |
