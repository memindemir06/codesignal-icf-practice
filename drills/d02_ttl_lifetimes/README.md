# Drill 02 — TTL and the half-open interval

> TTL and the half-open interval. Get the boundary right once, here.
>
> Level 3 is almost always "add a timestamp to everything". Get the boundary right once, here.

**Target: 15 minutes.** Traps exercised: T19, T20, T21, T22, T10.

Implement `Store` in `solution.py`. All timestamps are integers and strictly increasing
across calls (queries included).

- `set_at(key: str, value: str, timestamp: int) -> str`
  Stores `value` under `key` with **no expiry**. Overwrites any existing entry.
  Returns `""`.

- `set_at_with_ttl(key: str, value: str, timestamp: int, ttl: int) -> str`
  Stores `value` under `key`, alive during the interval `[timestamp, timestamp + ttl)` —
  i.e. **dead at exactly `timestamp + ttl`**. Overwriting an existing key **resets** its
  lifetime completely. Returns `""`.

- `get_at(key: str, timestamp: int) -> str`
  The value if the key exists and is alive at `timestamp`, otherwise `""`.

- `delete_at(key: str, timestamp: int) -> str`
  Removes the key. Returns `"true"` if it existed **and was alive**, `"false"` otherwise.
  (Note: strings, not booleans.)

- `count_at(timestamp: int) -> int`
  How many keys are alive at `timestamp`.

- `keys_at(timestamp: int) -> list[str]`
  All alive keys at `timestamp`, sorted lexicographically ascending.

### Example

```
set_at_with_ttl("a", "1", 1, 9)   -> ""      # alive [1, 10)
get_at("a", 9)                    -> "1"
get_at("a", 10)                   -> ""      # dead AT expiry
set_at_with_ttl("a", "2", 5, 10)  -> ""      # overwrite: now alive [5, 15)
get_at("a", 14)                   -> "2"
get_at("a", 15)                   -> ""
set_at("b", "9", 16)              -> ""      # no ttl = forever
count_at(1000000)                 -> 1
delete_at("a", 16)                -> "false" # already expired
delete_at("b", 17)                -> "true"
```

Run: `./run d02`
