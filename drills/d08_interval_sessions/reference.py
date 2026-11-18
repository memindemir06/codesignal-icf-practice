class Worker:
    def __init__(self, rate):
        self.rate = rate
        self.sessions = []     # list of (start, end) -- finished only
        self.open_at = None    # timestamp of an unfinished entry


class Attendance:
    def __init__(self):
        self.workers = {}

    def add_worker(self, worker_id, rate):
        if worker_id in self.workers:
            return "false"
        self.workers[worker_id] = Worker(rate)
        return "true"

    def punch(self, worker_id, timestamp):
        w = self.workers.get(worker_id)
        if w is None:
            return "invalid_request"
        if w.open_at is None:
            w.open_at = timestamp
        else:
            w.sessions.append((w.open_at, timestamp))
            w.open_at = None
        return "registered"

    @staticmethod
    def _total(w):
        return sum(e - s for s, e in w.sessions)

    def total(self, worker_id):
        w = self.workers.get(worker_id)
        return "" if w is None else str(self._total(w))

    def pay(self, worker_id, start, end):
        w = self.workers.get(worker_id)
        if w is None:
            return None
        worked = 0
        for s, e in w.sessions:
            overlap = min(e, end) - max(s, start)     # clamp, then discard negatives
            if overlap > 0:
                worked += overlap
        return worked * w.rate

    def top(self, n):
        pool = [(wid, self._total(w)) for wid, w in self.workers.items()]
        pool.sort(key=lambda kv: (-kv[1], kv[0]))
        return ["%s(%d)" % (wid, t) for wid, t in pool[:n]]
