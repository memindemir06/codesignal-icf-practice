import math

INF = math.inf


class Store:
    def __init__(self):
        # key -> (value, start, expiry)   expiry is exclusive
        self.data = {}

    # one writer, two doors
    def set_at(self, key: str, value: str, timestamp: int) -> str:
        return self._write(key, value, timestamp, None)

    def set_at_with_ttl(self, key: str, value: str, timestamp: int, ttl: int) -> str:
        return self._write(key, value, timestamp, ttl)

    def _write(self, key, value, timestamp, ttl):
        expiry = INF if ttl is None else timestamp + ttl
        self.data[key] = (value, timestamp, expiry)   # overwrite resets the whole interval
        return ""

    @staticmethod
    def _alive(entry, t):
        _, start, expiry = entry
        return start <= t < expiry                    # half-open: dead AT expiry

    def get_at(self, key: str, timestamp: int) -> str:
        entry = self.data.get(key)
        if entry is None or not self._alive(entry, timestamp):
            return ""
        return entry[0]

    def delete_at(self, key: str, timestamp: int) -> str:
        entry = self.data.get(key)
        if entry is None or not self._alive(entry, timestamp):
            return "false"
        del self.data[key]
        return "true"

    def count_at(self, timestamp: int) -> int:
        return sum(1 for e in self.data.values() if self._alive(e, timestamp))

    def keys_at(self, timestamp: int):
        return sorted(k for k, e in self.data.items() if self._alive(e, timestamp))
