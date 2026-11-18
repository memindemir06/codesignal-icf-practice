# Working Hours Register

Your task is to implement a program that registers the working hours of contract workers
at a facility. Plan your design according to the level specifications below:

* **Level 1:** add workers, register when they enter or leave, and report time worked.
* **Level 2:** rank workers by time spent in the office.
* **Level 3:** promote workers to a new position and compensation, and calculate salary.
* **Level 4:** support periods of time that are paid double.

To move to the next level, pass all the tests at this level.

## Note

**Every operation returns a string.** `register` calls arrive in strictly increasing order
of `timestamp`, across all workers.

---

## Level 1

Implement `WorkRegister` in `solution.py`.

* `add_worker(self, worker_id: str, position: str, compensation: int) -> str`
  Adds a worker with a position and an hourly compensation. Returns `"true"`, or
  `"false"` if `worker_id` already exists (nothing is updated in that case).

* `register(self, worker_id: str, timestamp: int) -> str`
  Registers the worker entering or leaving. The first call for a worker is an entry, the
  next is an exit, and so on. Returns `"registered"`, or `"invalid_request"` if the worker
  doesn't exist.

* `get(self, worker_id: str) -> str`
  The total time the worker has spent in the office, as a string, counting **finished**
  sessions only — a worker who has entered but not left contributes nothing for that
  visit. Returns `""` if the worker doesn't exist.

### Examples

| Query | Result |
| --- | --- |
| `add_worker("Ashley", "Middle Developer", 150)` | `"true"` |
| `add_worker("Ashley", "Junior Developer", 100)` | `"false"` |
| `register("Ashley", 10)` | `"registered"` — entered |
| `register("Ashley", 25)` | `"registered"` — left, 15 worked |
| `get("Ashley")` | `"15"` |
| `register("Ashley", 40)` | `"registered"` — entered, still in |
| `get("Ashley")` | `"15"` |
| `register("Ashley", 67)` | `"registered"` |
| `get("Ashley")` | `"42"` |
| `get("Walter")` | `""` |
| `register("Walter", 120)` | `"invalid_request"` |
