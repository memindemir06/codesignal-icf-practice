# In-Memory Database — Level 2

*(Only open this once `./run m3 1` is green.)*

Support displaying a record.

* `scan(self, key: str) -> str`
  Returns the fields of the record as
  `"<field1>(<value1>), <field2>(<value2>), ..."` with fields sorted **lexicographically
  ascending**. Returns `""` if the record doesn't exist or is empty.

* `scan_by_prefix(self, key: str, prefix: str) -> str`
  The same, but only fields whose name starts with `prefix`.

Note the separator is a comma **and a space**, and there is no trailing separator.

### Examples

| Query | Result |
| --- | --- |
| `set("A", "BC", "E")` | `""` |
| `set("A", "BD", "F")` | `""` |
| `set("A", "C", "G")` | `""` |
| `scan_by_prefix("A", "B")` | `"BC(E), BD(F)"` |
| `scan("A")` | `"BC(E), BD(F), C(G)"` |
| `scan_by_prefix("A", "")` | `"BC(E), BD(F), C(G)"` |
| `scan_by_prefix("B", "B")` | `""` |
| `scan("Z")` | `""` |
