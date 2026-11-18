# Drill 09 — Quotas, ownership and reject-don't-clamp

> Quotas and ownership: is this write allowed, and who gets charged?
>
> The cloud-storage family of ICF problems is built on this. Every write is a two-part
> question: *is it allowed?* and *who is it charged to?*

**Target: 12 minutes.** Traps exercised: T8, T9, T11, T7, T28.

Implement `Drive` in `solution.py`.

- `add_user(user_id: str, capacity: int) -> bool` — `False` if the user exists.
- `add_file(user_id: str, name: str, size: int) -> int | None`
  Stores the file, charged to `user_id`. Returns the user's **remaining** capacity after
  the write. Returns `None`, changing nothing, if:
  - the user doesn't exist, **or**
  - a file with that name already exists (any owner), **or**
  - the user has less than `size` capacity remaining.
- `delete_file(name: str) -> int | None`
  Removes the file and refunds its size to its owner. Returns the **size of the deleted
  file**, or `None` if no such file.
- `get_owner(name: str) -> str | None`
- `merge_users(keep_id: str, drop_id: str) -> int | None`
  Moves every file owned by `drop_id` to `keep_id` and adds `drop_id`'s **total capacity**
  to `keep_id`'s. `drop_id` is then removed. Returns `keep_id`'s remaining capacity, or
  `None` if the ids are equal or either doesn't exist.
- `top_users(n: int) -> list[str]`
  Users ranked by **bytes used**, descending, ties by id ascending, as `"<id>(<used>)"`.

### Example

```
add_user("amy", 1000)              -> True
add_user("amy", 5)                 -> False
add_user("bob", 500)               -> True
add_file("amy", "a.txt", 600)      -> 400
add_file("amy", "a.txt", 1)        -> None      # name taken
add_file("amy", "b.txt", 500)      -> None      # only 400 left
add_file("ghost", "c.txt", 1)      -> None
add_file("bob", "c.txt", 300)      -> 200
top_users(5)                       -> ['amy(600)', 'bob(300)']
delete_file("a.txt")               -> 600
delete_file("a.txt")               -> None
top_users(5)                       -> ['bob(300)', 'amy(0)']
merge_users("amy", "bob")          -> 1200      # 1000 + 500 total, 300 used
get_owner("c.txt")                 -> "amy"
merge_users("amy", "amy")          -> None
top_users(5)                       -> ['amy(300)']
```

Run: `./run d09`
