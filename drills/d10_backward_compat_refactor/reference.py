"""One implementation, two doors.

Every timeless method delegates to its timed twin with TIMELESS as the timestamp, and
`_alive` short-circuits on TIMELESS.  The Level 1 & 2 tests never notice.
"""
import math

INF = math.inf
TIMELESS = None


class Flags:
    def __init__(self):
        # account -> {flag: (start, expiry)}
        self.enabled = {}

    # ---------- the single implementation ----------
    def _write(self, account, flag, timestamp, ttl):
        start = 0 if timestamp is TIMELESS else timestamp
        expiry = INF if ttl is None else start + ttl
        self.enabled.setdefault(account, {})[flag] = (start, expiry)
        return ""

    @staticmethod
    def _alive(entry, timestamp):
        if entry is None:
            return False
        if timestamp is TIMELESS:
            return True                       # level-1 semantics: time does not exist
        start, expiry = entry
        return start <= timestamp < expiry    # half-open

    def _remove(self, account, flag, timestamp):
        flags = self.enabled.get(account)
        if flags is None or not self._alive(flags.get(flag), timestamp):
            return "false"
        del flags[flag]
        return "true"

    def _query(self, account, flag, timestamp):
        return "true" if self._alive(self.enabled.get(account, {}).get(flag), timestamp) else "false"

    def _listing(self, account, prefix, timestamp):
        flags = self.enabled.get(account, {})
        return ", ".join(sorted(f for f, e in flags.items()
                                if f.startswith(prefix) and self._alive(e, timestamp)))

    # ---------- level 1 & 2: unchanged behaviour ----------
    def enable(self, account, flag):
        return self._write(account, flag, TIMELESS, None)

    def disable(self, account, flag):
        return self._remove(account, flag, TIMELESS)

    def is_enabled(self, account, flag):
        return self._query(account, flag, TIMELESS)

    def list_flags(self, account, prefix):
        return self._listing(account, prefix, TIMELESS)

    # ---------- level 3 ----------
    def enable_at(self, account, flag, timestamp):
        return self._write(account, flag, timestamp, None)

    def enable_at_with_ttl(self, account, flag, timestamp, ttl):
        return self._write(account, flag, timestamp, ttl)

    def disable_at(self, account, flag, timestamp):
        return self._remove(account, flag, timestamp)

    def is_enabled_at(self, account, flag, timestamp):
        return self._query(account, flag, timestamp)

    def list_flags_at(self, account, prefix, timestamp):
        return self._listing(account, prefix, timestamp)
