# Drill 07 — Backup, restore, and TTL recalculation

> Backup and restore, storing remaining lifespan rather than expiry.
>
> Level 4's other favourite. The whole difficulty is one sentence: a snapshot must store
> **remaining lifespan**, not absolute expiry.

**Target: 15 minutes.** Traps exercised: T27, T19, T25, and the deepcopy footgun.

Implement `Cache` in `solution.py`. Operation timestamps are strictly increasing.

- `set_at(key: str, value: str, timestamp: int, ttl: int | None = None) -> str`
  Stores `value`, alive on `[timestamp, timestamp + ttl)`, or forever when `ttl` is `None`.
  Overwriting resets the lifetime. Returns `""`.
- `get_at(key: str, timestamp: int) -> str` — value, or `""` if missing/expired.
- `delete_at(key: str, timestamp: int) -> str` — `"true"` / `"false"`.
- `backup(timestamp: int) -> int`
  Saves the state of every **alive** key, recording how much life each has left.
  Returns the number of alive keys saved.
- `restore(timestamp: int, time_at: int) -> str`
  Replaces the current state with the **latest backup taken at or before `time_at`**
  (guaranteed to exist). Every restored key's lifetime restarts from `timestamp`:
  a key that had `r` ticks of life left when the backup was taken now expires at
  `timestamp + r`. Keys with no expiry stay unexpiring. Returns `""`.

Restoring the same backup twice must work — the second restore must see the pristine
snapshot, not a mutated one.

### Example

```
set_at("a", "1", 1, 10)      # alive [1, 11)
backup(3)          -> 1      # "a" has 8 ticks left
set_at("b", "2", 4)          # no ttl
backup(5)          -> 2      # "a" has 6 left, "b" has forever
delete_at("a", 8)  -> "true"
backup(9)          -> 1
restore(10, 7)     -> ""     # latest backup at or before 7 is the one from t=5
get_at("a", 15)    -> "1"    # 10 + 6 = 16, so alive at 15
get_at("a", 16)    -> ""
get_at("b", 10**9) -> "2"
```

Run: `./run d07`
