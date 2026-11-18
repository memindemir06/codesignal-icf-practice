# Working Hours Register — Level 3

*(Only open this once `./run m5 2` is green.)*

Support promotions and salary calculation.

* `promote(self, worker_id: str, new_position: str, new_compensation: int, start_timestamp: int) -> str`
  Registers a pending promotion. The new position and compensation become active **the
  first time the worker enters the office at or after `start_timestamp`** — that entry
  begins the first session paid at the new rate.
  `new_position` is guaranteed to differ from the worker's current position, and
  `start_timestamp` is guaranteed to be greater than the timestamp of the last `register`
  call for any worker.
  Returns `"success"`, or `"invalid_request"` if:
  * `worker_id` doesn't exist, **or**
  * a promotion is already pending for that worker (they haven't yet entered the office
    with the new position).

* `calc_salary(self, worker_id: str, start_timestamp: int, end_timestamp: int) -> str`
  The net salary earned between `start_timestamp` and `end_timestamp`, as a string.
  Workers are paid only for finished sessions, and only for the part of each session that
  falls inside the window. For a finished session `[s, e)` overlapping the window on
  `[a, b)`, the pay is `(b - a) * compensation_in_force_for_that_session`.
  It is guaranteed that `end_timestamp > start_timestamp >= 0`.
  Returns `""` if the worker doesn't exist.

Notes:
* `top_n_workers` considers only the worker's **current** position.
* `get` returns the total across all positions the worker has held.

### Examples

| Query | Result |
| --- | --- |
| `add_worker("John", "Middle Developer", 200)` | `"true"` |
| `register("John", 100)` / `register("John", 125)` | 25 worked at 200 |
| `promote("John", "Senior Developer", 500, 200)` | `"success"` |
| `promote("John", "Staff Developer", 900, 300)` | `"invalid_request"` — one is pending |
| `register("John", 300)` | `"registered"` — enters as Senior Developer at 500 |
| `register("John", 350)` | 50 worked at 500 |
| `get("John")` | `"75"` |
| `top_n_workers(5, "Middle Developer")` | `""` |
| `top_n_workers(5, "Senior Developer")` | `"John(75)"` |
| `calc_salary("John", 0, 1000)` | `"30000"` — `25*200 + 50*500` |
| `calc_salary("John", 110, 320)` | `"13000"` — `15*200 + 20*500` |
| `calc_salary("John", 0, 100)` | `"0"` |
| `calc_salary("Walter", 0, 10)` | `""` |
