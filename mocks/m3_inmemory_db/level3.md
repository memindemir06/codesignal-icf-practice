# In-Memory Database — Level 3

*(Only open this once `./run m3 2` is green.)*

Support a timeline of operations and TTL settings. Every operation from the previous
levels gains a timestamped twin. For each field-value pair, the TTL determines how long
that value persists before disappearing.

Notes:
* Timestamps are integers and are guaranteed to **strictly increase**.
* A single test will not mix the timestamped and untimestamped versions of the operations.
* **You must maintain backward compatibility**: the Level 1 and 2 methods must keep behaving
  exactly as they do today — no expiry, no notion of time.

* `set_at(self, key: str, field: str, value: str, timestamp: int) -> str`
  As `set`, at the given time, with **no expiry**. Returns `""`.

* `set_at_with_ttl(self, key: str, field: str, value: str, timestamp: int, ttl: int) -> str`
  As `set_at`, but the pair is available during the interval
  `[timestamp, timestamp + ttl)` — it is **gone at exactly `timestamp + ttl`**.
  Setting a field again **replaces** its value *and* restarts its lifetime. Returns `""`.

* `delete_at(self, key: str, field: str, timestamp: int) -> str`
  As `delete`, but only deletes a field that is **alive** at `timestamp`.
  Returns `"true"` / `"false"`.

* `get_at(self, key: str, field: str, timestamp: int) -> str`
* `scan_at(self, key: str, timestamp: int) -> str`
* `scan_by_prefix_at(self, key: str, prefix: str, timestamp: int) -> str`
  As their untimed counterparts, but only over field-value pairs alive at `timestamp`.

### Examples

| Query | Result |
| --- | --- |
| `set_at_with_ttl("A", "BC", "E", 1, 9)` | `""` — `{"BC": "E"}` alive on `[1, 10)` |
| `set_at_with_ttl("A", "BC", "E", 5, 10)` | `""` — overwritten, now alive on `[5, 15)` |
| `set_at("A", "BD", "F", 6)` | `""` — no expiry |
| `scan_by_prefix_at("A", "B", 14)` | `"BC(E), BD(F)"` |
| `scan_by_prefix_at("A", "B", 15)` | `"BD(F)"` |
| `get_at("A", "BC", 15)` | `""` |
| `delete_at("A", "BC", 16)` | `"false"` — already expired |
