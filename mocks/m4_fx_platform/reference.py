"""Worked reference solution for Mock 4 (FX platform).

The state model is the whole problem: everything is keyed by (client, currency).  Getting
that right at Level 1 -- balances, outgoing counters and history all nested dicts -- makes
Level 4 a matter of adding numbers together.
"""
import bisect
import math
from collections import defaultdict
from dataclasses import dataclass, field

INF = math.inf


@dataclass
class Series:
    """An append-only (timestamp, value) curve for one (client, currency) pair."""
    ts: list = field(default_factory=list)
    vals: list = field(default_factory=list)

    def record(self, t, v):
        if self.ts and self.ts[-1] == t:
            self.vals[-1] = v
        else:
            self.ts.append(t)
            self.vals.append(v)

    def at(self, t):
        i = bisect.bisect_right(self.ts, t)
        return self.vals[i - 1] if i else 0


@dataclass
class Client:
    id: str
    created_at: int
    balances: dict = field(default_factory=lambda: defaultdict(int))   # ccy -> amount
    outgoing: dict = field(default_factory=lambda: defaultdict(int))   # ccy -> amount
    history: dict = field(default_factory=dict)                        # ccy -> Series

    def series(self, currency):
        if currency not in self.history:
            self.history[currency] = Series()
        return self.history[currency]

    def own_at(self, currency, t):
        s = self.history.get(currency)
        return 0 if s is None else s.at(t)

    def move(self, timestamp, currency, delta, outgoing=0):
        self.balances[currency] += delta
        self.outgoing[currency] += outgoing
        self.series(currency).record(timestamp, self.balances[currency])
        return self.balances[currency]


@dataclass
class Quote:
    id: str
    frm: str
    to: str
    rate_pips: int
    start: int
    expiry: float

    def live(self, t):
        return self.start <= t < self.expiry      # half-open

    def convert(self, amount):
        return amount * self.rate_pips // 10000   # integer maths, rounds down


class FXPlatform:
    def __init__(self):
        self.clients = {}
        self.quotes = {}
        self.quote_seq = 0

    # ---------- level 1 ----------
    def create_client(self, timestamp, client_id):
        if client_id in self.clients:
            return False
        self.clients[client_id] = Client(id=client_id, created_at=timestamp)
        return True

    def deposit(self, timestamp, client_id, currency, amount):
        client = self.clients.get(client_id)
        if client is None:
            return None
        return client.move(timestamp, currency, amount)

    def withdraw(self, timestamp, client_id, currency, amount):
        client = self.clients.get(client_id)
        if client is None or client.balances[currency] < amount:
            return None
        return client.move(timestamp, currency, -amount, outgoing=amount)

    def get_balance(self, timestamp, client_id, currency):
        client = self.clients.get(client_id)
        return None if client is None else client.balances[currency]

    # ---------- level 2 ----------
    def top_spenders(self, timestamp, currency, n):
        pool = [(c.id, c.outgoing[currency]) for c in self.clients.values()]
        pool.sort(key=lambda kv: (-kv[1], kv[0]))
        return ["%s(%d)" % (cid, total) for cid, total in pool[:n]]

    # ---------- level 3 ----------
    def quote(self, timestamp, from_currency, to_currency, rate_pips, ttl):
        self.quote_seq += 1
        quote_id = "quote%d" % self.quote_seq
        self.quotes[quote_id] = Quote(quote_id, from_currency, to_currency,
                                      rate_pips, timestamp, timestamp + ttl)
        return quote_id

    def execute(self, timestamp, client_id, quote_id, amount):
        client = self.clients.get(client_id)
        q = self.quotes.get(quote_id)
        if client is None or q is None or not q.live(timestamp):
            return None
        if client.balances[q.frm] < amount:
            return None
        client.move(timestamp, q.frm, -amount, outgoing=amount)
        return client.move(timestamp, q.to, q.convert(amount))

    # ---------- level 4 ----------
    def merge_clients(self, timestamp, keep_id, drop_id):
        if keep_id == drop_id:
            return False
        keep = self.clients.get(keep_id)
        drop = self.clients.get(drop_id)
        if keep is None or drop is None:
            return False

        for currency in set(keep.history) | set(drop.history):
            # keep.created_at must be a sample point: the keeper exists from then on, even
            # in currencies only the dropped client ever held.
            times = sorted(set(keep.series(currency).ts)
                           | set(drop.series(currency).ts)
                           | {keep.created_at})
            merged = Series()
            for t in times:
                if t < keep.created_at:
                    continue
                merged.record(t, keep.own_at(currency, t) + drop.own_at(currency, t))
            keep.history[currency] = merged

        for currency, amount in drop.balances.items():
            keep.balances[currency] += amount
        for currency, amount in drop.outgoing.items():
            keep.outgoing[currency] += amount
        for currency in set(keep.balances) | set(keep.history):
            keep.series(currency).record(timestamp, keep.balances[currency])

        del self.clients[drop_id]
        return True

    def balance_at(self, timestamp, client_id, currency, time_at):
        client = self.clients.get(client_id)
        if client is None or time_at < client.created_at:
            return None
        return client.own_at(currency, time_at)
