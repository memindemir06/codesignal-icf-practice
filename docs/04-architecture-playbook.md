# 04 — The playbook: one skeleton, four levels

The whole test is winnable with a single shape of solution that you can type from memory.
Learn this shape, then every problem becomes "fill in the domain nouns".

---

## The shape

```python
from __future__ import annotations
import bisect, copy, heapq, math
from collections import defaultdict
from dataclasses import dataclass, field

INF = math.inf


@dataclass
class Entity:                      # the noun of the problem: Account / File / Worker / Record
    id: str
    created_at: int = 0
    removed_at: int | None = None  # lifecycle — needed for L4 point-in-time
    metric: int = 0                # the L2 ranking number
    history: list = field(default_factory=list)   # [(ts, value)] — L4 point-in-time


class System:                      # the exact class name the spec gives you
    def __init__(self):
        self._items: dict[str, Entity] = {}
        self._alias: dict[str, str] = {}    # L4 merge:  dead id -> surviving id
        self._pending: list = []            # L3 deferred effects (min-heap by due ts)
        self._backups: list = []            # L4 snapshots [(ts, deepcopy)]
        self._seq = 0                       # for "payment1", "payment2", ...

    # ---------- internals: write these FIRST, at level 1 ----------

    def _resolve(self, eid: str) -> str:
        while eid in self._alias:
            eid = self._alias[eid]
        return eid

    def _get(self, eid: str) -> Entity | None:
        return self._items.get(self._resolve(eid))

    def _settle(self, t: int) -> None:
        """Apply every deferred effect due at or before t. First line of every public method."""
        while self._pending and self._pending[0][0] <= t:
            ...

    @staticmethod
    def _alive(entry, t) -> bool:
        return entry.start <= t < entry.expiry        # half-open

    # ---------- level 1: public API ----------

    def create(self, timestamp, eid): ...
    def read(self, timestamp, eid): ...
    def update(self, timestamp, eid, x): ...

    # ---------- level 2: ranking / processing ----------

    def top_n(self, timestamp, n):
        self._settle(timestamp)
        pool = [(e.id, e.metric) for e in self._items.values()]
        ranked = sorted(pool, key=lambda kv: (-kv[1], kv[0]))[:n]
        return [f"{i}({v})" for i, v in ranked]

    # ---------- level 3: _at variants ----------
    # L1/L2 methods delegate here with a sentinel timestamp.

    # ---------- level 4: merge / rollback / history ----------
```

You will not need every slot. **Write the slots anyway** — empty `_resolve` and `_settle` cost
six lines at Level 1 and save you a rewrite at Levels 3 and 4.

---

## The five decisions you make in the first three minutes

Before typing anything, answer these from the four-line level brief:

1. **What is the entity?** (account / file / record / worker) → that's your dataclass.
2. **What is the ranking metric?** (outgoing total / size / hours) → **store it as a field on the
   entity, incremented at write time.** Never derive it by scanning a transaction log at query
   time — Level 4 merge needs it to be additive.
3. **Does time enter at L3?** (almost always yes) → every value becomes an interval, and every
   public method starts with `_settle(timestamp)`.
4. **Is L4 merge, rollback, or history?**
   - *merge* → you need `_alias` and every metric must be additive.
   - *rollback* → you need `deepcopy` snapshots and **relative** lifespans.
   - *history* → you need an append-only `(ts, value)` log written on every mutation.
5. **What are the exact return values?** → write them as comments in each stub before coding.

Three minutes of this buys back twenty at Level 4.

---

## Backward compatibility: the delegation pattern

Level 3 gives you `set_at(key, field, value, timestamp)` next to Level 1's
`set(key, field, value)`. Do **not** maintain two code paths.

```python
TIMELESS = None

def set(self, key, field, value):
    return self.set_at(key, field, value, TIMELESS)

def set_at(self, key, field, value, timestamp):
    t = 0 if timestamp is TIMELESS else timestamp
    ...

def _alive(self, entry, t):
    if t is TIMELESS:
        return True          # level-1 semantics: time doesn't exist
    return entry.start <= t < entry.expiry
```

One rule, applied everywhere: **the timeless variants call the timed ones with a sentinel, and
the sentinel short-circuits every time check.** Level 1 and 2 tests keep passing untouched.

If the spec instead gives L3 a *different signature order* (e.g. `set_at(key, field, value, ts)`
vs `upload_at(ts, name, size)`), just match it exactly and delegate — the sentinel trick is
unaffected.

---

## Ranking metrics must be additive

The Level 2 ranking looks trivial, and it is — until Level 4 says "merged accounts' totals must
be the sum of both". If your metric is a field you `+=` on every outgoing operation, merge is:

```python
a.metric += b.metric
```

If your metric is computed by filtering a global transaction list by `account_id`, merge means
rewriting every historical transaction's owner, or maintaining a set of owned ids, and you will
lose ten minutes. **Decide this at Level 2, for Level 4.**

Same logic for history: `a.history` and `b.history` merged means you need the surviving entity to
answer point-in-time questions across both. Easiest correct approach: keep A's own history, and
on merge, *add B's balance-at-time curve into A's* by replaying:

```python
# merged history = for each event time in either, A(t) + B(t)
times = sorted({t for t, _ in a.history} | {t for t, _ in b.history})
a.history = [(t, value_at(a, t) + value_at(b, t)) for t in times]
```
This is the single fiddliest thing in the whole framework. Drill 06 is exactly this.

---

## Rollback: store remaining lifespan, not expiry

```python
def backup(self, t):
    snap = {}
    for k, rec in self._items.items():
        fields = {}
        for f, (v, start, expiry) in rec.items():
            if not (start <= t < expiry):
                continue                                   # don't snapshot dead entries
            remaining = INF if expiry == INF else expiry - t
            fields[f] = (v, remaining)
        if fields:
            snap[k] = fields
    self._backups.append((t, snap))
    return len(snap)                                       # spec often wants the live count

def restore(self, t, time_at):
    idx = bisect.bisect_right([b[0] for b in self._backups], time_at) - 1
    _, snap = self._backups[idx]
    self._items = {}
    for k, fields in snap.items():
        self._items[k] = {
            f: (v, t, INF if rem == INF else t + rem)
            for f, (v, rem) in fields.items()
        }
```

Note `bisect_right(..., time_at) - 1` = "latest backup at or before `time_at`". The spec usually
says *before* `timestampToRestore` and guarantees one exists — read whether it's `<` or `<=`;
`bisect_right` gives `<=`, `bisect_left` gives `<`.

---

## Merge: the six-line checklist

Write merge as literally six labelled lines so you can't forget one:

```python
def merge(self, t, keep_id, drop_id):
    self._settle(t)
    if keep_id == drop_id: return False                  # 1. self-merge
    a, b = self._items.get(keep_id), self._items.get(drop_id)
    if a is None or b is None: return False              # 2. existence

    a.balance += b.balance                               # 3. value
    a.metric  += b.metric                                # 4. ranking metric
    self._merge_history(a, b, t)                         # 5. point-in-time history
    self._alias[drop_id] = keep_id                       # 6. identity: pending effects,
    del self._items[drop_id]                             #    id lookups, payment ids
    b.removed_at = t
    return True
```

Because `_settle` and every lookup go through `_resolve`, line 6 alone re-targets pending
cashback *and* makes `get_payment_status(keep_id, "payment_from_b")` work. That is the payoff
for writing `_resolve` at Level 1.

Careful: after `del self._items[drop_id]`, a point-in-time query for `drop_id` must return
"didn't exist" (**T30**) — so `_resolve` must **not** be used for `get_balance(drop_id, ...)`.
Read the spec: the banking one says `get_balance(11, "account2", 10)` → `None`. So keep a
separate "was this id merged away" check for history queries. Two lookup helpers:
`_resolve()` for *pending effects and payment ids*, raw `self._items.get()` for *user-facing
identity*.

---

## Level 1 code you should be able to type in 90 seconds

```python
def create_account(self, timestamp: int, account_id: str) -> bool:
    self._settle(timestamp)
    if account_id in self._items:
        return False
    self._items[account_id] = Account(id=account_id, created_at=timestamp)
    self._items[account_id].history.append((timestamp, 0))
    return True

def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
    self._settle(timestamp)
    acct = self._items.get(account_id)
    if acct is None:
        return None
    acct.balance += amount
    acct.history.append((timestamp, acct.balance))
    return acct.balance

def transfer(self, timestamp, source_account_id, target_account_id, amount):
    self._settle(timestamp)
    if source_account_id == target_account_id:
        return None
    src = self._items.get(source_account_id)
    dst = self._items.get(target_account_id)
    if src is None or dst is None or src.balance < amount:
        return None
    src.balance -= amount
    dst.balance += amount
    src.metric  += amount            # outgoing total, for L2
    src.history.append((timestamp, src.balance))
    dst.history.append((timestamp, dst.balance))
    return src.balance
```

Every line there is doing double duty for a later level. That is what a good Level 1 looks like.
