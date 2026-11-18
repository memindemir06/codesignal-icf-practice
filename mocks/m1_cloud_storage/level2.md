# Cloud Storage — Level 2

*(Only open this once `./run m1 1` is green.)*

Support searching the storage.

* `find_file(self, prefix: str, suffix: str) -> list[str]`
  Returns the **top 10** files whose name **starts with** `prefix` **and ends with**
  `suffix`, ordered by size **descending**; ties broken by file name **ascending**.
  Each entry is formatted `"<name>(<size>)"`.
  Returns `[]` if nothing matches. An empty `prefix` or `suffix` matches everything.

### Examples

| Query | Result |
| --- | --- |
| `add_file("/dir/file.txt", 100)` | `True` |
| `add_file("/dir/file.med", 200)` | `True` |
| `add_file("/dir/deep/file.txt", 300)` | `True` |
| `add_file("/other/file.txt", 300)` | `True` |
| `find_file("/dir", ".txt")` | `['/dir/deep/file.txt(300)', '/dir/file.txt(100)']` |
| `find_file("/", "")` | `['/dir/deep/file.txt(300)', '/other/file.txt(300)', '/dir/file.med(200)', '/dir/file.txt(100)']` |
| `find_file("/zzz", "")` | `[]` |
