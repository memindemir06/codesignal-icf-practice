class InMemoryDB:
    def __init__(self):
        pass

    # ---------- level 1 ----------
    def set(self, key: str, field: str, value: str) -> str:
        raise NotImplementedError

    def get(self, key: str, field: str) -> str:
        raise NotImplementedError

    def delete(self, key: str, field: str) -> str:
        raise NotImplementedError

    # ---------- level 2 ----------
    def scan(self, key: str) -> str:
        raise NotImplementedError

    def scan_by_prefix(self, key: str, prefix: str) -> str:
        raise NotImplementedError

    # ---------- level 3 ----------
    def set_at(self, key: str, field: str, value: str, timestamp: int) -> str:
        raise NotImplementedError

    def set_at_with_ttl(self, key: str, field: str, value: str,
                        timestamp: int, ttl: int) -> str:
        raise NotImplementedError

    def delete_at(self, key: str, field: str, timestamp: int) -> str:
        raise NotImplementedError

    def get_at(self, key: str, field: str, timestamp: int) -> str:
        raise NotImplementedError

    def scan_at(self, key: str, timestamp: int) -> str:
        raise NotImplementedError

    def scan_by_prefix_at(self, key: str, prefix: str, timestamp: int) -> str:
        raise NotImplementedError

    # ---------- level 4 ----------
    def backup(self, timestamp: int) -> str:
        raise NotImplementedError

    def restore(self, timestamp: int, timestamp_to_restore: int) -> str:
        raise NotImplementedError
