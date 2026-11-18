"""Worked reference solution for Mock 6 (metrics service).

One idea does all four levels: a sample is never deleted, only *filtered*.  `_visible()`
is the single choke point through which every read passes, so retention (level 3) is four
lines and rollback (level 4) only has to preserve sample ages.
"""
import bisect
import math
from dataclasses import dataclass, field

INF = math.inf


@dataclass
class Metric:
    name: str
    samples: list = field(default_factory=list)   # [(timestamp, value)] increasing
    retention: float = INF


class MetricsService:
    def __init__(self):
        self.metrics = {}
        self.snap_ts = []      # increasing snapshot timestamps
        self.snaps = []        # parallel: {name: (retention, [(age, value)])}

    # ---------- the single choke point ----------
    @staticmethod
    def _visible(metric, timestamp):
        return [(t, v) for t, v in metric.samples if timestamp - t < metric.retention]

    # ---------- level 1 ----------
    def record(self, timestamp, metric, value):
        m = self.metrics.get(metric)
        if m is None:
            m = self.metrics[metric] = Metric(metric)
        m.samples.append((timestamp, value))
        return len(self._visible(m, timestamp))

    def latest(self, timestamp, metric):
        m = self.metrics.get(metric)
        if m is None:
            return None
        vis = self._visible(m, timestamp)
        return vis[-1][1] if vis else None

    def remove(self, timestamp, metric):
        return self.metrics.pop(metric, None) is not None

    # ---------- level 2 ----------
    def summary(self, timestamp, metric, window):
        m = self.metrics.get(metric)
        if m is None:
            return ""
        values = [v for t, v in self._visible(m, timestamp)
                  if timestamp - window <= t <= timestamp]
        if not values:
            return ""
        # // on ints floors towards negative infinity, which is what the spec asks for
        return "min(%d) max(%d) avg(%d)" % (min(values), max(values),
                                            sum(values) // len(values))

    def top_metrics(self, timestamp, n):
        pool = [(m.name, len(self._visible(m, timestamp))) for m in self.metrics.values()]
        pool.sort(key=lambda kv: (-kv[1], kv[0]))
        return ["%s(%d)" % (name, count) for name, count in pool[:n]]

    # ---------- level 3 ----------
    def set_retention(self, timestamp, metric, ttl):
        m = self.metrics.get(metric)
        if m is None:
            return False
        m.retention = ttl
        return True

    # ---------- level 4 ----------
    def snapshot(self, timestamp):
        snap = {}
        live = 0
        for name, m in self.metrics.items():
            vis = self._visible(m, timestamp)
            snap[name] = (m.retention, [(timestamp - t, v) for t, v in vis])  # ages
            if vis:
                live += 1
        self.snap_ts.append(timestamp)
        self.snaps.append(snap)
        return live

    def rollback(self, timestamp, time_at):
        i = bisect.bisect_right(self.snap_ts, time_at) - 1
        snap = self.snaps[i]
        self.metrics = {}
        for name, (retention, aged) in snap.items():
            m = Metric(name, [(timestamp - age, v) for age, v in aged], retention)
            self.metrics[name] = m
        return ""
