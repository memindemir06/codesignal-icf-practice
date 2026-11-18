import bisect


class Life:
    """One incarnation of an account id: [opened_at, closed_at)."""

    def __init__(self, opened_at):
        self.opened_at = opened_at
        self.closed_at = None
        self.ts = [opened_at]      # strictly increasing
        self.vals = [0]

    @property
    def balance(self):
        return self.vals[-1]

    def record(self, t, v):
        if self.ts[-1] == t:
            self.vals[-1] = v
        else:
            self.ts.append(t)
            self.vals.append(v)

    def contains(self, time_at):
        if time_at < self.opened_at:
            return False
        return self.closed_at is None or time_at < self.closed_at

    def at(self, time_at):
        i = bisect.bisect_right(self.ts, time_at)   # <= time_at: "after the op AT time_at"
        return self.vals[i - 1] if i else None


class Ledger:
    def __init__(self):
        self.live = {}      # account_id -> Life
        self.past = {}      # account_id -> [Life, ...] closed incarnations

    def open(self, timestamp: int, account_id: str) -> bool:
        if account_id in self.live:
            return False
        self.live[account_id] = Life(timestamp)
        return True

    def credit(self, timestamp: int, account_id: str, amount: int):
        life = self.live.get(account_id)
        if life is None:
            return None
        life.record(timestamp, life.balance + amount)
        return life.balance

    def debit(self, timestamp: int, account_id: str, amount: int):
        life = self.live.get(account_id)
        if life is None or life.balance < amount:
            return None
        life.record(timestamp, life.balance - amount)
        return life.balance

    def close(self, timestamp: int, account_id: str) -> bool:
        life = self.live.pop(account_id, None)
        if life is None:
            return False
        life.closed_at = timestamp
        self.past.setdefault(account_id, []).append(life)
        return True

    def balance_at(self, timestamp: int, account_id: str, time_at: int):
        for life in self.past.get(account_id, []) + ([self.live[account_id]]
                                                     if account_id in self.live else []):
            if life.contains(time_at):
                return life.at(time_at)
        return None
