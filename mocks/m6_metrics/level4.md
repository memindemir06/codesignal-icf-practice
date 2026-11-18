# Metrics Service — Level 4

*(Only open this once `./run m6 3` is green.)*

Support snapshotting the service and rolling back to a snapshot.

* `snapshot(self, timestamp: int) -> int`
  Saves the state of the service. For every existing metric it saves the metric's
  retention setting and each of its **visible** samples, recorded as an **age**
  (`timestamp - sample_time`) rather than an absolute time. Metrics with no visible
  samples are still saved, with no samples.
  Returns the number of metrics that have **at least one visible sample** at `timestamp`.

* `rollback(self, timestamp: int, time_at: int) -> str`
  Replaces the entire state with the **latest snapshot taken at or before `time_at`**
  (guaranteed to exist). Each saved sample keeps the **age** it had when the snapshot was
  taken: a sample that was `a` old is placed at time `timestamp - a`. Retention settings
  are restored as they were. Returns `""`.

Rolling back to the same snapshot twice must work — the second rollback sees the pristine
snapshot.

### Examples

| Query | Result |
| --- | --- |
| `record(10, "cpu", 40)` | `1` |
| `record(20, "cpu", 60)` | `2` |
| `set_retention(21, "cpu", 15)` | `True` |
| `snapshot(25)` | `1` — only the sample from 20 is visible, and it is 5 old |
| `record(26, "mem", 1)` | `1` |
| `remove(27, "cpu")` | `True` |
| `snapshot(28)` | `1` |
| `rollback(100, 26)` | `""` — the snapshot from 25 |
| `latest(101, "cpu")` | `60` — replayed at `100 - 5 = 95`, still inside a 15 retention |
| `latest(102, "mem")` | `None` — "mem" did not exist at the snapshot |
| `top_metrics(103, 5)` | `['cpu(1)']` |
| `latest(115, "cpu")` | `None` — the sample is now 20 old |
