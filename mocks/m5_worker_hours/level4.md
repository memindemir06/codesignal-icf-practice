# Working Hours Register — Level 4

*(Only open this once `./run m5 3` is green.)*

The facility pays double for work done during certain periods.

* `add_double_pay_period(self, start_timestamp: int, end_timestamp: int) -> str`
  Marks `[start_timestamp, end_timestamp)` as a double-pay period. Returns `"true"`, or
  `"false"` — registering nothing — if:
  * `end_timestamp <= start_timestamp`, **or**
  * the period **overlaps** an existing double-pay period. Two periods that merely touch
    at an endpoint (one ends exactly where the next begins) do **not** overlap.

  Double-pay periods may be added at any time, including after the work they affect was
  registered, and they apply to every worker.

* `calc_salary` must now pay **twice** the compensation for the part of a paid session
  that falls inside a double-pay period. Concretely, for a session `[s, e)` at
  compensation `c`, overlapping the salary window on `[a, b)`:

  ```
  pay = (b - a) * c  +  (total length of [a, b) inside double-pay periods) * c
  ```

### Examples

| Query | Result |
| --- | --- |
| `add_worker("John", "Dev", 10)` | `"true"` |
| `register("John", 0)` / `register("John", 100)` | 100 worked at 10 |
| `calc_salary("John", 0, 100)` | `"1000"` |
| `add_double_pay_period(20, 40)` | `"true"` |
| `calc_salary("John", 0, 100)` | `"1200"` — 20 extra units at rate 10 |
| `add_double_pay_period(30, 50)` | `"false"` — overlaps |
| `add_double_pay_period(40, 60)` | `"true"` — touching is fine |
| `add_double_pay_period(90, 90)` | `"false"` — empty |
| `calc_salary("John", 0, 100)` | `"1400"` |
| `calc_salary("John", 0, 30)` | `"400"` — 30 base + 10 doubled |
