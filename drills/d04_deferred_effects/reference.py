import heapq

WAIT = 3600
CASHBACK_PCT = 5


class Rewards:
    def __init__(self):
        self.balances = {}     # account_id -> int
        self.pending = []      # min-heap of (due_ts, seq, account_id, amount, reward_id)
        self.owner = {}        # reward_id -> account_id
        self.paid = set()      # reward_ids already credited
        self.seq = 0

    # ---- the discipline ----------------------------------------------------
    def _settle(self, timestamp: int) -> None:
        while self.pending and self.pending[0][0] <= timestamp:
            _due, _s, acct, amount, rid = heapq.heappop(self.pending)
            self.balances[acct] = self.balances.get(acct, 0) + amount
            self.paid.add(rid)

    # ---- public API --------------------------------------------------------
    def open_account(self, timestamp: int, account_id: str) -> bool:
        self._settle(timestamp)
        if account_id in self.balances:
            return False
        self.balances[account_id] = 0
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int):
        self._settle(timestamp)
        if account_id not in self.balances:
            return None
        self.balances[account_id] += amount
        return self.balances[account_id]

    def spend(self, timestamp: int, account_id: str, amount: int):
        self._settle(timestamp)
        if account_id not in self.balances:
            return None
        if self.balances[account_id] < amount:
            return None                      # reject, don't clamp; no id consumed
        self.balances[account_id] -= amount
        self.seq += 1
        rid = "reward%d" % self.seq
        cashback = amount * CASHBACK_PCT // 100      # floor, integer maths only
        heapq.heappush(self.pending, (timestamp + WAIT, self.seq, account_id, cashback, rid))
        self.owner[rid] = account_id
        return rid

    def reward_status(self, timestamp: int, account_id: str, reward_id: str):
        self._settle(timestamp)
        if account_id not in self.balances:
            return None
        if self.owner.get(reward_id) != account_id:
            return None
        return "PAID" if reward_id in self.paid else "PENDING"

    def balance(self, timestamp: int, account_id: str):
        self._settle(timestamp)
        return self.balances.get(account_id)
