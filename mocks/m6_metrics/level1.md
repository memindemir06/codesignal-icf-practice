# Metrics Service

Your task is to implement a simplified metrics collection service. Plan your design
according to the level specifications below:

* **Level 1:** record samples for named metrics and read them back.
* **Level 2:** aggregate a metric over a sliding time window, and rank metrics.
* **Level 3:** support per-metric retention policies.
* **Level 4:** support snapshotting and rolling back the whole service.

To move to the next level, pass all the tests at this level.

## Note

Every operation takes a `timestamp` (an integer). Timestamps are unique and operations
arrive in **strictly increasing** timestamp order. Values are integers and may be negative.

---

## Level 1

Implement `MetricsService` in `solution.py`.

* `record(self, timestamp: int, metric: str, value: int) -> int`
  Records a sample for `metric`, creating the metric if it doesn't exist. Returns the
  number of samples the metric now holds.

* `latest(self, timestamp: int, metric: str) -> int | None`
  The most recently recorded value for `metric`, or `None` if the metric doesn't exist or
  holds no samples.

* `remove(self, timestamp: int, metric: str) -> bool`
  Deletes the metric and all its samples. Returns `False` if the metric doesn't exist.
  Recording under the same name afterwards starts a brand-new metric.

### Examples

| Query | Result |
| --- | --- |
| `record(1, "cpu", 40)` | `1` |
| `record(2, "cpu", 55)` | `2` |
| `record(3, "mem", 10)` | `1` |
| `latest(4, "cpu")` | `55` |
| `latest(5, "disk")` | `None` |
| `remove(6, "cpu")` | `True` |
| `remove(7, "cpu")` | `False` |
| `latest(8, "cpu")` | `None` |
| `record(9, "cpu", 1)` | `1` |
