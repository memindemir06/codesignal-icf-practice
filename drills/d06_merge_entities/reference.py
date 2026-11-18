import bisect
from dataclasses import dataclass, field


@dataclass
class Account:
    id: str
    created_at: int
    balance: int = 0
    outgoing: int = 0                                   # additive metric -- merge just adds
    ts: list = field(default_factory=list)              # history timestamps (increasing)
    vals: list = field(default_factory=list)            # balance after each

    def record(self, t, v):
        if self.ts and self.ts[-1] == t:
            self.vals[-1] = v
        else:
            self.ts.append(t)
            self.vals.append(v)

    def own_at(self, t):
        """Balance at end of t, or 0 if this account had no history yet."""
        i = bisect.bisect_right(self.ts, t)
        return self.vals[i - 1] if i else 0


class Registry:
    def __init__(self):
        self.accounts = {}          # live id -> Account

    # ---- level 1 -----------------------------------------------------------
    def create(self, timestamp, account_id):
        if account_id in self.accounts:
            return False
        acct = Account(id=account_id, created_at=timestamp)
        acct.record(timestamp, 0)
        self.accounts[account_id] = acct
        return True

    def deposit(self, timestamp, account_id, amount):
        acct = self.accounts.get(account_id)
        if acct is None:
            return None
        acct.balance += amount
        acct.record(timestamp, acct.balance)
        return acct.balance

    def transfer(self, timestamp, source, target, amount):
        if source == target:
            return None
        src = self.accounts.get(source)
        dst = self.accounts.get(target)
        if src is None or dst is None or src.balance < amount:
            return None
        src.balance -= amount
        dst.balance += amount
        src.outgoing += amount
        src.record(timestamp, src.balance)
        dst.record(timestamp, dst.balance)
        return src.balance

    # ---- level 2 -----------------------------------------------------------
    def top_spenders(self, timestamp, n):
        pool = [(a.id, a.outgoing) for a in self.accounts.values()]
        pool.sort(key=lambda kv: (-kv[1], kv[0]))
        return ["%s(%d)" % (i, v) for i, v in pool[:n]]

    # ---- level 4 -----------------------------------------------------------
    def balance_at(self, timestamp, account_id, time_at):
        acct = self.accounts.get(account_id)
        if acct is None or time_at < acct.created_at:
            return None
        return acct.own_at(time_at)

    def merge(self, timestamp, keep_id, drop_id):
        if keep_id == drop_id:
            return False
        keep = self.accounts.get(keep_id)
        drop = self.accounts.get(drop_id)
        if keep is None or drop is None:
            return False

        # 3. inherit history: combined(t) = keep.own(t) + drop.own(t), for t >= keep.created_at
        times = sorted(set(keep.ts) | set(drop.ts))
        ts, vals = [], []
        for t in times:
            if t < keep.created_at:
                continue
            ts.append(t)
            vals.append(keep.own_at(t) + drop.own_at(t))
        keep.ts, keep.vals = ts, vals

        keep.balance += drop.balance          # 1. value
        keep.outgoing += drop.outgoing        # 2. metric
        keep.record(timestamp, keep.balance)
        del self.accounts[drop_id]            # 5. identity gone
        return True
