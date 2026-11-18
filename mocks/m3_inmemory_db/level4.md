# In-Memory Database — Level 4

*(Only open this once `./run m3 3` is green.)*

The database should be backed up from time to time.

* `backup(self, timestamp: int) -> str`
  Saves the database state at `timestamp`, including the **remaining lifespan** of every
  field — the difference between the expiry time and `timestamp`. Expired fields are not
  saved. Returns, **as a string**, the number of non-empty records saved (i.e. records
  with at least one alive field).

* `restore(self, timestamp: int, timestamp_to_restore: int) -> str`
  Restores the database from the **latest backup taken at or before
  `timestamp_to_restore`** (guaranteed to exist). The current state is replaced entirely.
  Expiry times are recalculated relative to `timestamp`: a field that had `r` ticks of life
  left when the backup was taken now expires at `timestamp + r`. Fields with no expiry stay
  unexpiring. Returns `""`.

Restoring the same backup twice must work — the second restore sees the pristine snapshot.

### Examples

| Query | Result |
| --- | --- |
| `set_at_with_ttl("A", "B", "C", 1, 10)` | `""` — alive on `[1, 11)` |
| `backup(3)` | `"1"` — `B` has 8 ticks of life left |
| `set_at("A", "D", "E", 4)` | `""` |
| `backup(5)` | `"1"` |
| `delete_at("A", "B", 8)` | `"true"` |
| `backup(9)` | `"1"` |
| `restore(10, 7)` | `""` — restores the backup taken at 5 |
| `scan_at("A", 15)` | `"B(C), D(E)"` — `B` now expires at `10 + 6 = 16` |
| `scan_at("A", 16)` | `"D(E)"` |
| `set_at("B", "C", "D", 17)` | `""` |
| `backup(18)` | `"2"` |
