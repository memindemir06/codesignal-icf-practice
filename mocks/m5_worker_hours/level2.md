# Working Hours Register — Level 2

*(Only open this once `./run m5 1` is green.)*

Report ordered statistics about the workers.

* `top_n_workers(self, n: int, position: str) -> str`
  The ids of the top `n` workers **holding that position**, sorted by total time spent in
  the office **descending**; ties by `worker_id` **ascending**. Finished sessions only.
  Returned as one string:
  `"<id1>(<time1>), <id2>(<time2>), ..."`.
  * A worker with no finished sessions counts as `0` and still appears.
  * If fewer than `n` workers hold that position, return all of them.
  * If no worker holds that position, return `""`.

### Examples

| Query | Result |
| --- | --- |
| `add_worker("John", "Junior Developer", 120)` | `"true"` |
| `add_worker("Jason", "Junior Developer", 120)` | `"true"` |
| `add_worker("Ashley", "Junior Developer", 120)` | `"true"` |
| `add_worker("Ellie", "Senior Developer", 400)` | `"true"` |
| `register("John", 100)` / `register("John", 150)` | 50 worked |
| `register("Jason", 200)` / `register("Jason", 250)` | 50 worked |
| `register("Ashley", 300)` / `register("Ashley", 310)` | 10 worked |
| `top_n_workers(3, "Junior Developer")` | `"Jason(50), John(50), Ashley(10)"` |
| `top_n_workers(1, "Junior Developer")` | `"Jason(50)"` |
| `top_n_workers(5, "Senior Developer")` | `"Ellie(0)"` |
| `top_n_workers(5, "Designer")` | `""` |
