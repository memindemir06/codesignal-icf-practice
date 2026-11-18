"""Worked reference solution for Mock 3 (in-memory database).

The whole solution is five private methods plus thirteen one-line public wrappers.
`TIMELESS` is the sentinel that lets the Level 1 & 2 API share the Level 3 implementation
without either knowing about the other.
"""
import bisect
import math

INF = math.inf
TIMELESS = None


class InMemoryDB:
    def __init__(self):
        # key -> {field: (value, start, expiry)}   expiry is exclusive
        self.records = {}
        self.backup_ts = []      # increasing timestamps
        self.snaps = []          # parallel: {key: {field: (value, remaining)}}

    # ---------- the single implementation ----------
    @staticmethod
    def _alive(entry, timestamp):
        if entry is None:
            return False
        if timestamp is TIMELESS:
            return True                        # level 1 & 2 have no notion of time
        _value, start, expiry = entry
        return start <= timestamp < expiry     # half-open

    def _write(self, key, field, value, timestamp, ttl):
        start = 0 if timestamp is TIMELESS else timestamp
        expiry = INF if ttl is None else start + ttl
        self.records.setdefault(key, {})[field] = (value, start, expiry)
        return ""

    def _read(self, key, field, timestamp):
        entry = self.records.get(key, {}).get(field)
        return entry[0] if self._alive(entry, timestamp) else ""

    def _remove(self, key, field, timestamp):
        fields = self.records.get(key)
        if fields is None or not self._alive(fields.get(field), timestamp):
            return "false"
        del fields[field]
        return "true"

    def _listing(self, key, prefix, timestamp):
        fields = self.records.get(key, {})
        alive = sorted((f, e[0]) for f, e in fields.items()
                       if f.startswith(prefix) and self._alive(e, timestamp))
        return ", ".join("%s(%s)" % (f, v) for f, v in alive)

    # ---------- level 1 ----------
    def set(self, key, field, value):
        return self._write(key, field, value, TIMELESS, None)

    def get(self, key, field):
        return self._read(key, field, TIMELESS)

    def delete(self, key, field):
        return self._remove(key, field, TIMELESS)

    # ---------- level 2 ----------
    def scan(self, key):
        return self._listing(key, "", TIMELESS)

    def scan_by_prefix(self, key, prefix):
        return self._listing(key, prefix, TIMELESS)

    # ---------- level 3 ----------
    def set_at(self, key, field, value, timestamp):
        return self._write(key, field, value, timestamp, None)

    def set_at_with_ttl(self, key, field, value, timestamp, ttl):
        return self._write(key, field, value, timestamp, ttl)

    def delete_at(self, key, field, timestamp):
        return self._remove(key, field, timestamp)

    def get_at(self, key, field, timestamp):
        return self._read(key, field, timestamp)

    def scan_at(self, key, timestamp):
        return self._listing(key, "", timestamp)

    def scan_by_prefix_at(self, key, prefix, timestamp):
        return self._listing(key, prefix, timestamp)

    # ---------- level 4 ----------
    def backup(self, timestamp):
        snap = {}
        for key, fields in self.records.items():
            saved = {}
            for field, entry in fields.items():
                if not self._alive(entry, timestamp):
                    continue
                value, _start, expiry = entry
                remaining = INF if expiry == INF else expiry - timestamp
                saved[field] = (value, remaining)      # RELATIVE lifespan
            if saved:
                snap[key] = saved
        self.backup_ts.append(timestamp)
        self.snaps.append(snap)
        return str(len(snap))

    def restore(self, timestamp, timestamp_to_restore):
        i = bisect.bisect_right(self.backup_ts, timestamp_to_restore) - 1
        snap = self.snaps[i]
        self.records = {
            key: {f: (v, timestamp, INF if rem == INF else timestamp + rem)
                  for f, (v, rem) in fields.items()}
            for key, fields in snap.items()
        }
        return ""
