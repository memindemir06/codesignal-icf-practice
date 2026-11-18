# In-Memory Database

Your task is to implement a simplified in-memory database. Plan your design according to
the level specifications below:

* **Level 1:** basic operations on records, fields and values.
* **Level 2:** display a record's fields, optionally filtered by prefix.
* **Level 3:** timestamped operations and TTL (time-to-live) on field-value pairs.
* **Level 4:** backup and restore.

To move to the next level, pass all the tests at this level.

---

## Level 1

The database holds **records**. A record is identified by a `key` (a string) and holds
**field → value** pairs (both strings).

Implement `InMemoryDB` in `solution.py`.

* `set(self, key: str, field: str, value: str) -> str`
  Inserts a field-value pair into the record for `key`, creating the record if needed and
  replacing the value if the field already exists. Returns `""`.

* `get(self, key: str, field: str) -> str`
  Returns the value, or `""` if the record or the field doesn't exist.

* `delete(self, key: str, field: str) -> str`
  Removes the field from the record. Returns `"true"` if it was removed, `"false"` if the
  record or the field doesn't exist. **These are strings, not booleans.**

### Examples

| Query | Result |
| --- | --- |
| `set("A", "B", "E")` | `""` — state `{"A": {"B": "E"}}` |
| `set("A", "C", "F")` | `""` — state `{"A": {"B": "E", "C": "F"}}` |
| `get("A", "B")` | `"E"` |
| `get("A", "D")` | `""` |
| `get("Z", "B")` | `""` |
| `delete("A", "B")` | `"true"` |
| `delete("A", "B")` | `"false"` |
| `delete("Z", "B")` | `"false"` |
