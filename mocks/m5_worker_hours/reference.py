"""Worked reference solution for Mock 5 (working hours register).

The design decision that carries all four levels: a finished session is stored as
`(start, end, compensation)` -- the *rate in force at the time* is baked into the record.
Promotions then never have to be replayed, and `calc_salary` is pure interval arithmetic.
"""
from dataclasses import dataclass, field


def overlap(a1, a2, b1, b2):
    """Length of the intersection of [a1, a2) and [b1, b2); 0 if they don't meet."""
    return max(0, min(a2, b2) - max(a1, b1))


@dataclass
class Worker:
    id: str
    position: str
    compensation: int
    sessions: list = field(default_factory=list)   # (start, end, compensation_then)
    open_at: int = None                            # unfinished entry
    pending: tuple = None                          # (position, compensation, start_ts)

    @property
    def total(self):
        return sum(e - s for s, e, _c in self.sessions)


class WorkRegister:
    def __init__(self):
        self.workers = {}
        self.double_pay = []            # non-overlapping [start, end)

    # ---------- level 1 ----------
    def add_worker(self, worker_id, position, compensation):
        if worker_id in self.workers:
            return "false"
        self.workers[worker_id] = Worker(worker_id, position, compensation)
        return "true"

    def register(self, worker_id, timestamp):
        w = self.workers.get(worker_id)
        if w is None:
            return "invalid_request"
        if w.open_at is None:
            # an entry: a pending promotion becomes effective right now
            if w.pending is not None and timestamp >= w.pending[2]:
                w.position, w.compensation, _ = w.pending
                w.pending = None
            w.open_at = timestamp
        else:
            w.sessions.append((w.open_at, timestamp, w.compensation))
            w.open_at = None
        return "registered"

    def get(self, worker_id):
        w = self.workers.get(worker_id)
        return "" if w is None else str(w.total)

    # ---------- level 2 ----------
    def top_n_workers(self, n, position):
        pool = [(w.id, w.total) for w in self.workers.values() if w.position == position]
        pool.sort(key=lambda kv: (-kv[1], kv[0]))
        return ", ".join("%s(%d)" % (wid, t) for wid, t in pool[:n])

    # ---------- level 3 ----------
    def promote(self, worker_id, new_position, new_compensation, start_timestamp):
        w = self.workers.get(worker_id)
        if w is None or w.pending is not None:
            return "invalid_request"
        w.pending = (new_position, new_compensation, start_timestamp)
        return "success"

    def calc_salary(self, worker_id, start_timestamp, end_timestamp):
        w = self.workers.get(worker_id)
        if w is None:
            return ""
        total = 0
        for s, e, comp in w.sessions:
            a, b = max(s, start_timestamp), min(e, end_timestamp)
            if b <= a:
                continue
            total += (b - a) * comp
            # level 4: every unit inside a double-pay period is paid once more
            for d1, d2 in self.double_pay:
                total += overlap(a, b, d1, d2) * comp
        return str(total)

    # ---------- level 4 ----------
    def add_double_pay_period(self, start_timestamp, end_timestamp):
        if end_timestamp <= start_timestamp:
            return "false"
        for d1, d2 in self.double_pay:
            if overlap(start_timestamp, end_timestamp, d1, d2) > 0:
                return "false"
        self.double_pay.append((start_timestamp, end_timestamp))
        return "true"
