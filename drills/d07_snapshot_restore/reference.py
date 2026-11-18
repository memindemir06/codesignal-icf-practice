import bisect
import math

INF = math.inf


class Cache:
    def __init__(self):
        self.data = {}          # key -> (value, start, expiry)
        self.backup_ts = []     # increasing
        self.snaps = []         # parallel: {key: (value, remaining)}

    @staticmethod
    def _alive(entry, t):
        _, start, expiry = entry
        return start <= t < expiry

    def set_at(self, key, value, timestamp, ttl=None):
        expiry = INF if ttl is None else timestamp + ttl
        self.data[key] = (value, timestamp, expiry)
        return ""

    def get_at(self, key, timestamp):
        e = self.data.get(key)
        return e[0] if e is not None and self._alive(e, timestamp) else ""

    def delete_at(self, key, timestamp):
        e = self.data.get(key)
        if e is None or not self._alive(e, timestamp):
            return "false"
        del self.data[key]
        return "true"

    def backup(self, timestamp):
        snap = {}
        for k, (v, start, expiry) in self.data.items():
            if not self._alive((v, start, expiry), timestamp):
                continue                                  # dead entries are not snapshotted
            remaining = INF if expiry == INF else expiry - timestamp
            snap[k] = (v, remaining)                      # RELATIVE, not absolute
        self.backup_ts.append(timestamp)
        self.snaps.append(snap)
        return len(snap)

    def restore(self, timestamp, time_at):
        i = bisect.bisect_right(self.backup_ts, time_at) - 1   # latest at or before
        snap = self.snaps[i]
        # rebuild fresh objects -- never hand the live state a reference into the snapshot
        self.data = {
            k: (v, timestamp, INF if rem == INF else timestamp + rem)
            for k, (v, rem) in snap.items()
        }
        return ""
