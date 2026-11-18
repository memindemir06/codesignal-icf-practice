# 03 — Python for ICF: what to memorise

The honest truth about the algorithms: **ICF is not an algorithms test.** In ~40 real ICF
problems the required toolkit is a dict, a list, `sorted()` with a key, and occasionally a heap.
The difficulty is design and speed. So this page is short on Big-O and long on *typing less*.

---

## 1. The nine things that actually appear

| Pattern | Frequency | Tool |
|---|---|---|
| Keyed lookup / CRUD | Every L1 | `dict` |
| Nested records (key → field → value) | Very common | `defaultdict(dict)` |
| Top-N with tie-break | Every L2 | `sorted(key=lambda x: (-v, name))[:n]` |
| Prefix filter | Common L2 | `s.startswith(p)` — linear scan is fine |
| Formatted output string | Every L2 | f-strings + `", ".join(...)` |
| Alive-at-time (TTL) | Every L3 | half-open interval `[start, expiry)` |
| Deferred/scheduled effects | Common L3 | sorted pending list + lazy settle |
| Point-in-time history | Common L4 | append-only `(timestamp, value)` list + `bisect` |
| Snapshot / restore | Common L4 | `copy.deepcopy` + store *remaining* lifespans |
| Merge two entities | Common L4 | alias `dict` + additive fields |

Things that **essentially never appear**: graphs, DP, tries (a linear `startswith` scan beats
building one, at these input sizes), segment trees, sliding-window optimisation, bit tricks,
recursion beyond trivial. If you find yourself needing one, reread the spec — you've
misunderstood it.

---

## 2. Sorting — the single most-used line in the test

```python
# Descending by score, ties broken ascending by name.  THE ICF sort.
ranked = sorted(items, key=lambda kv: (-kv[1], kv[0]))[:n]

# When the value isn't negatable (e.g. a string), sort twice — stable sort makes this correct:
items.sort(key=lambda x: x.name)              # secondary first
items.sort(key=lambda x: x.score, reverse=True)  # primary last
```

`sorted(..., reverse=True)` on a tuple key reverses **every** component. That is the #1 ranking
bug. Negate the numeric component instead, or do the two-pass stable sort.

Heap for top-N, only if you truly need it:
```python
import heapq
heapq.nlargest(n, items, key=lambda x: x.score)   # ties are NOT broken the way you want
```
`nlargest` does not give you the alphabetical tie-break. **Prefer `sorted`.** It's `O(m log m)`
on a few thousand items — microseconds.

---

## 3. Formatted output

```python
", ".join(f"{name}({value})" for name, value in ranked)     # "a(3), b(1)"
[f"{name}({value})" for name, value in ranked]              # ['a(3)', 'b(1)']
```
Check whether the spec wants the string or the list. Both appear.

---

## 4. Dicts

```python
from collections import defaultdict
records = defaultdict(dict)          # key -> {field: value}
totals  = defaultdict(int)           # id  -> running total, no existence check needed

d.get(k)                 # None if missing
d.get(k, default)
d.pop(k, None)           # delete, no KeyError
k in d
d.setdefault(k, [])      # get-or-create
dict(sorted(d.items()))  # sorted copy
```

`defaultdict(int)` is worth real seconds: `totals[x] += amount` with no `if x not in totals`.
But beware — reading `totals[x]` **creates** the key. If you later iterate `totals` to build a
ranking, phantom keys appear. Use `totals.get(x, 0)` for reads.

---

## 5. Time and TTL

```python
import math
INF = math.inf

# store an interval, not a scalar
self.values[key][field] = (value, start, start + ttl if ttl is not None else INF)

def _alive(self, entry, t):
    _, start, expiry = entry
    return start <= t < expiry        # half-open: dead AT expiry
```

For "timeless" Level-1 calls that must coexist with Level-3 `_at` calls, pick a sentinel:
```python
def get(self, key, field):
    return self.get_at(key, field, timestamp=None)   # None means "ignore time entirely"
```
and inside, `if t is None: return True` from `_alive`. One implementation, two doors.

---

## 6. Point-in-time history

Append-only log per entity, then binary search:

```python
import bisect

class History:
    def __init__(self):
        self.ts = []       # strictly increasing
        self.vals = []

    def record(self, t, v):
        if self.ts and self.ts[-1] == t:
            self.vals[-1] = v                # same timestamp: overwrite
        else:
            self.ts.append(t); self.vals.append(v)

    def at(self, t):
        i = bisect.bisect_right(self.ts, t)  # <= t  →  "after the op at t"
        return self.vals[i - 1] if i else None
```

`bisect_right(ts, t) - 1` = last index with `ts[i] <= t`. That is the **T29** semantics
("reflect the state *after* the query at `time_at`"). If a spec ever wants *before*, use
`bisect_left`.

Honestly: at ICF input sizes a plain reverse linear scan is also fine and harder to get wrong.
Know both; reach for the linear one when flustered.

---

## 7. Deferred effects (cashback, scheduled payments, expiry-with-side-effects)

```python
import heapq

self._pending = []   # min-heap of (due_ts, seq, entity_id, amount, payment_id)

def _settle(self, t):
    while self._pending and self._pending[0][0] <= t:
        due, _, eid, amount, pid = heapq.heappop(self._pending)
        acct = self._resolve(eid)            # merge-aware!
        acct.balance += amount
        acct.history.record(due, acct.balance)   # T31: record at DUE time, not now
        self._status[pid] = "CASHBACK_RECEIVED"
```

Then **the first line of every public method** is `self._settle(timestamp)`. That single
discipline handles T23 for free, in every operation, forever.

---

## 8. Snapshot / restore

```python
import copy

def backup(self, t):
    snap = copy.deepcopy(self._state)
    # convert absolute expiries to REMAINING lifespans  (T27)
    for entry in walk(snap):
        entry.expiry = INF if entry.expiry == INF else entry.expiry - t
    self._backups.append((t, snap))
    return count_of_live_records

def restore(self, t, time_at):
    i = bisect.bisect_right([b[0] for b in self._backups], time_at) - 1
    _, snap = self._backups[i]
    self._state = copy.deepcopy(snap)
    for entry in walk(self._state):
        entry.expiry = INF if entry.expiry == INF else t + entry.expiry
```

`deepcopy` on both sides. Copying on backup and *not* on restore means the second restore to the
same backup gets a mutated snapshot. Silent, brutal, hard to find.

---

## 9. Merge / aliasing

```python
self._alias = {}                      # merged-away id -> surviving id

def _resolve(self, eid):
    while eid in self._alias:
        eid = self._alias[eid]
        return eid                    # or loop fully if chains are possible
```
Build `_resolve()` at Level 1 even though nothing uses it. It costs three lines and it is the
difference between Level 4 taking 8 minutes and taking 40.

---

## 10. Money

Integer minor units only. Never `float`.
```python
cashback = amount * 2 // 100      # 2%, rounded down.  T24.
```
`amount * 2 // 100` not `amount // 100 * 2` (different for amount=75: 1 vs 0) and not
`int(amount * 0.02)` (floats).

---

## 11. Dataclasses, cheaply

```python
from dataclasses import dataclass, field

@dataclass
class Account:
    id: str
    balance: int = 0
    outgoing: int = 0
    history: list = field(default_factory=list)
```
Worth it: attribute access reads better under stress and refactors survive. `field(default_factory=...)`
for anything mutable — a bare `[]` default is shared across instances.

---

## 12. Python 3.10 features you can rely on

CodeSignal has run 3.10.6. Safe: `match`, `X | Y` type unions, `list[str]` builtin generics,
walrus, f-strings with `=`. **Not** safe: 3.11+ (`ExceptionGroup`, `Self`), 3.12 generics syntax.
Your local Python is 3.9, so `int | None` in *annotations* is fine only with
`from __future__ import annotations` — the kit includes it where needed. Don't rely on that habit
in the real test; just write the annotation, it'll work there.

---

## 13. Speed keys

| Need | Do |
|---|---|
| Raise a runtime error | `raise RuntimeError("...")` — for specs that say "throws" |
| Guard clause | `if x not in self.d: return None` — early return, no nesting |
| Count matches | `sum(1 for x in xs if pred(x))` |
| Max with tie-break | `min(xs, key=lambda x: (-x.score, x.name))` |
| Copy a dict shallowly | `dict(d)` / `d.copy()` |
| Stable multi-key sort | sort by secondary key first, then primary |
