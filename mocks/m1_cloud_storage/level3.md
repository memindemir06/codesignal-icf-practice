# Cloud Storage — Level 3

*(Only open this once `./run m1 2` is green.)*

Storage may now be owned by users, each with a capacity limit.

* `add_user(self, user_id: str, capacity: int) -> bool`
  Creates a user with `capacity` bytes of quota. Returns `False` if the user already
  exists (and the existing capacity is **not** changed).

* `add_file_by(self, user_id: str, name: str, size: int) -> int | None`
  Adds a file owned by `user_id`. Returns the user's **remaining** capacity after the
  file is added. Returns `None`, changing nothing, if:
  * `user_id` doesn't exist, **or**
  * a file with that `name` already exists (owned by anyone, or unowned), **or**
  * the user's remaining capacity is less than `size`.

* `merge_user(self, user_id_1: str, user_id_2: str) -> int | None`
  Merges `user_id_2` into `user_id_1`: all of `user_id_2`'s files are transferred to
  `user_id_1`, and `user_id_2`'s **total capacity** is added to `user_id_1`'s.
  `user_id_2` is then removed. Returns `user_id_1`'s remaining capacity after the merge,
  or `None` if `user_id_1 == user_id_2` or either user doesn't exist.

### Backward compatibility

Files created by the Level-1 `add_file` are **unowned** — they belong to no user and
occupy no quota. Beyond that:

* `delete_file` refunds the freed space to the file's owner, if it has one.
* `copy_file` charges the new copy to the **source file's owner**. Copying an unowned file
  produces another unowned file and never fails on capacity. Copying an owned file returns
  `False` (changing nothing) if the owner cannot afford it. If `dest` already exists it is
  overwritten and its space is refunded to *its* owner first, so when you overwrite a file
  you already own only the **difference** in size is charged.
* `find_file` searches every file, owned or not.

### Examples

| Query | Result |
| --- | --- |
| `add_user("u1", 200)` | `True` |
| `add_user("u1", 500)` | `False` |
| `add_file_by("u1", "/a.txt", 50)` | `150` |
| `add_file_by("u1", "/a.txt", 1)` | `None` — name taken |
| `add_file_by("u1", "/b.txt", 500)` | `None` — over capacity |
| `add_file_by("ghost", "/c.txt", 1)` | `None` |
| `delete_file("/a.txt")` | `50` — u1 is back to 200 remaining |
| `add_user("u2", 100)` | `True` |
| `add_file_by("u2", "/d.txt", 80)` | `20` |
| `merge_user("u1", "u2")` | `220` — capacity 300, used 80 |
| `merge_user("u1", "u2")` | `None` — u2 is gone |
