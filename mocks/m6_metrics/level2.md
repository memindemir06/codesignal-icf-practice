# Metrics Service — Level 2

*(Only open this once `./run m6 1` is green.)*

Support aggregation and ranking.

* `summary(self, timestamp: int, metric: str, window: int) -> str`
  Aggregates the samples recorded in the **closed** interval
  `[timestamp - window, timestamp]`, returning exactly:
  `"min(<min>) max(<max>) avg(<avg>)"` — single spaces, no commas.
  `avg` is the mean **rounded down towards negative infinity** (so `-7 / 2` is `-4`).
  Returns `""` if the metric doesn't exist or has no samples in the window.

* `top_metrics(self, timestamp: int, n: int) -> list[str]`
  The `n` metrics with the most samples, descending; ties by metric name **ascending**.
  Each entry formatted `"<metric>(<count>)"`. If fewer than `n` metrics exist, return all
  of them. `[]` if there are none.

### Examples

| Query | Result |
| --- | --- |
| `record(10, "cpu", 40)` | `1` |
| `record(20, "cpu", 60)` | `2` |
| `record(30, "cpu", 50)` | `3` |
| `record(31, "mem", 7)` | `1` |
| `summary(32, "cpu", 100)` | `"min(40) max(60) avg(50)"` |
| `summary(33, "cpu", 15)` | `"min(50) max(60) avg(55)"` |
| `summary(34, "cpu", 4)` | `"min(50) max(50) avg(50)"` |
| `summary(35, "cpu", 1)` | `""` |
| `summary(36, "disk", 100)` | `""` |
| `top_metrics(40, 5)` | `['cpu(3)', 'mem(1)']` |
| `top_metrics(40, 1)` | `['cpu(3)']` |
