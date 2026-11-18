# Cloud Storage — Level 4

*(Only open this once `./run m1 3` is green.)*

Support per-user backup and restore.

* `backup_user(self, user_id: str) -> int | None`
  Saves the state (names and sizes) of **all files currently owned by `user_id`**.
  Returns the number of files saved, or `None` if the user doesn't exist.
  A new backup **replaces** that user's previous backup.

* `restore_user(self, user_id: str) -> bool`
  Returns `False` if the user doesn't exist. Otherwise returns `True` and:
  1. deletes every file currently owned by `user_id` (refunding their space);
  2. re-adds every file from the user's backup, owned by `user_id`, **ignoring the
     capacity limit** — except that a backed-up file whose name is currently taken by
     anything else (another user's file, or an unowned file) is **skipped**;
  3. if the user has no backup, step 2 does nothing, so all their files are simply removed.

Notes:
* A user's remaining capacity may become **negative** after a restore. Further
  `add_file_by` calls then fail until enough space is freed.
* When `user_id_2` is merged into `user_id_1`, `user_id_2`'s backup is discarded and
  `user_id_1` keeps its own backup unchanged.
* Unowned files are never part of any backup.

### Examples

| Query | Result |
| --- | --- |
| `add_user("u1", 100)` | `True` |
| `add_file_by("u1", "/a", 40)` | `60` |
| `add_file_by("u1", "/b", 40)` | `20` |
| `backup_user("u1")` | `2` |
| `delete_file("/a")` | `40` |
| `add_file_by("u1", "/c", 50)` | `10` |
| `restore_user("u1")` | `True` |
| `get_file_size("/a")` | `40` |
| `get_file_size("/b")` | `40` |
| `get_file_size("/c")` | `None` |
| `backup_user("ghost")` | `None` |
