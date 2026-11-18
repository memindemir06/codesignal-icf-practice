"""Worked reference solution for Mock 2 (banking).

The three decisions that make Level 4 cheap, all taken before Level 1 was written:

  1. `outgoing` is a field incremented at write time, so merge is `a.outgoing += b.outgoing`.
  2. Every mutation appends to an append-only (timestamp, balance) history.
  3. `_resolve()` turns a possibly-merged-away id into the surviving one, so pending
     cashback and payment ids follow the merge for free.
"""
import bisect
import heapq
from dataclasses import dataclass, field

MILLISECONDS_IN_1_DAY = 86400000
CASHBACK_PCT = 2


@dataclass
class Account:
    id: str
    created_at: int
    balance: int = 0
    outgoing: int = 0
    ts: list = field(default_factory=list)
    vals: list = field(default_factory=list)

    def record(self, t, v):
        if self.ts and self.ts[-1] == t:
            self.vals[-1] = v
        else:
            self.ts.append(t)
            self.vals.append(v)

    def own_at(self, t):
        """Balance at the end of t; 0 if this account has no history at or before t."""
        i = bisect.bisect_right(self.ts, t)
        return self.vals[i - 1] if i else 0


class BankingSystem:
    def __init__(self):
        self.accounts = {}       # live account_id -> Account
        self.alias = {}          # merged-away id -> surviving id
        self.pending = []        # heap of (due_ts, seq, original_owner_id, amount, payment_id)
        self.payment_owner = {}  # payment_id -> original owner id
        self.cashed = set()      # payment_ids whose cashback has landed
        self.seq = 0

    # ---------- internals ----------
    def _resolve(self, account_id):
        while account_id in self.alias:
            account_id = self.alias[account_id]
        return account_id

    def _settle(self, timestamp):
        """Credit every cashback due at or before timestamp. First line of every method."""
        while self.pending and self.pending[0][0] <= timestamp:
            due, _seq, owner, amount, payment_id = heapq.heappop(self.pending)
            acct = self.accounts.get(self._resolve(owner))
            self.cashed.add(payment_id)
            if acct is None:
                continue
            acct.balance += amount
            acct.record(due, acct.balance)      # recorded at the DUE time, not now
        # cashback never counts toward `outgoing`

    # ---------- level 1 ----------
    def create_account(self, timestamp, account_id):
        self._settle(timestamp)
        if account_id in self.accounts:
            return False
        acct = Account(id=account_id, created_at=timestamp)
        acct.record(timestamp, 0)
        self.accounts[account_id] = acct
        return True

    def deposit(self, timestamp, account_id, amount):
        self._settle(timestamp)
        acct = self.accounts.get(account_id)
        if acct is None:
            return None
        acct.balance += amount
        acct.record(timestamp, acct.balance)
        return acct.balance

    def transfer(self, timestamp, source_account_id, target_account_id, amount):
        self._settle(timestamp)
        if source_account_id == target_account_id:
            return None
        src = self.accounts.get(source_account_id)
        dst = self.accounts.get(target_account_id)
        if src is None or dst is None or src.balance < amount:
            return None
        src.balance -= amount
        dst.balance += amount
        src.outgoing += amount
        src.record(timestamp, src.balance)
        dst.record(timestamp, dst.balance)
        return src.balance

    # ---------- level 2 ----------
    def top_spenders(self, timestamp, n):
        self._settle(timestamp)
        pool = [(a.id, a.outgoing) for a in self.accounts.values()]
        pool.sort(key=lambda kv: (-kv[1], kv[0]))
        return ["%s(%d)" % (aid, out) for aid, out in pool[:n]]

    # ---------- level 3 ----------
    def pay(self, timestamp, account_id, amount):
        self._settle(timestamp)
        acct = self.accounts.get(account_id)
        if acct is None or acct.balance < amount:
            return None
        acct.balance -= amount
        acct.outgoing += amount
        acct.record(timestamp, acct.balance)
        self.seq += 1
        payment_id = "payment%d" % self.seq
        cashback = amount * CASHBACK_PCT // 100          # floor, integer maths
        heapq.heappush(self.pending,
                       (timestamp + MILLISECONDS_IN_1_DAY, self.seq,
                        account_id, cashback, payment_id))
        self.payment_owner[payment_id] = account_id
        return payment_id

    def get_payment_status(self, timestamp, account_id, payment):
        self._settle(timestamp)
        if account_id not in self.accounts:
            return None
        owner = self.payment_owner.get(payment)
        if owner is None or self._resolve(owner) != account_id:
            return None
        return "CASHBACK_RECEIVED" if payment in self.cashed else "IN_PROGRESS"

    # ---------- level 4 ----------
    def merge_accounts(self, timestamp, account_id_1, account_id_2):
        self._settle(timestamp)
        if account_id_1 == account_id_2:
            return False
        keep = self.accounts.get(account_id_1)
        drop = self.accounts.get(account_id_2)
        if keep is None or drop is None:
            return False

        # inherited history: combined(t) = keep.own(t) + drop.own(t) for t >= keep.created_at
        ts, vals = [], []
        for t in sorted(set(keep.ts) | set(drop.ts)):
            if t < keep.created_at:
                continue
            ts.append(t)
            vals.append(keep.own_at(t) + drop.own_at(t))
        keep.ts, keep.vals = ts, vals

        keep.balance += drop.balance
        keep.outgoing += drop.outgoing
        keep.record(timestamp, keep.balance)
        self.alias[account_id_2] = account_id_1     # pending cashback + payment ids follow
        del self.accounts[account_id_2]
        return True

    def get_balance(self, timestamp, account_id, time_at):
        self._settle(timestamp)
        acct = self.accounts.get(account_id)        # deliberately NOT _resolve: a merged-away
        if acct is None or time_at < acct.created_at:   # id must report None
            return None
        return acct.own_at(time_at)
