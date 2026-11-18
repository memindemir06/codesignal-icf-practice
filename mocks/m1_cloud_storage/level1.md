# Cloud Storage

Your task is to implement a simplified version of a cloud file storage service.
All operations that should be supported are listed below. Partial credit is granted for
each test passed, so run the tests often.

Plan your design according to the level specifications below:

* **Level 1:** support adding, retrieving, deleting and copying files.
* **Level 2:** support searching for files by prefix and suffix.
* **Level 3:** support users with storage quotas, and merging two users.
* **Level 4:** support backing up and restoring a user's files.

Do not change the given method signatures. To move to the next level, pass all the tests
at this level.

---

## Level 1

Implement `CloudStorage` in `solution.py`.

* `add_file(self, name: str, size: int) -> bool`
  Adds a new file. Returns `True` if the file was added, or `False` if a file with that
  name already exists (in which case nothing changes).

* `get_file_size(self, name: str) -> int | None`
  Returns the size of the file, or `None` if it doesn't exist.

* `delete_file(self, name: str) -> int | None`
  Deletes the file and returns its size, or `None` if it doesn't exist.

* `copy_file(self, source: str, dest: str) -> bool`
  Copies `source` to `dest`. Returns `False` if `source` doesn't exist.
  If `dest` already exists it is **overwritten**.
  If `source == dest`, nothing changes and the operation returns `True`.

### Examples

| Query | Result |
| --- | --- |
| `add_file("/dir/file.txt", 100)` | `True` |
| `add_file("/dir/file.txt", 200)` | `False` — name taken |
| `get_file_size("/dir/file.txt")` | `100` |
| `get_file_size("/nope")` | `None` |
| `copy_file("/nope", "/x")` | `False` |
| `copy_file("/dir/file.txt", "/dir/copy.txt")` | `True` |
| `get_file_size("/dir/copy.txt")` | `100` |
| `delete_file("/dir/file.txt")` | `100` |
| `delete_file("/dir/file.txt")` | `None` |
