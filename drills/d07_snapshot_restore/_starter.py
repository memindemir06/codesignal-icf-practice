class Cache:
    def __init__(self):
        pass

    def set_at(self, key: str, value: str, timestamp: int, ttl=None) -> str:
        # -> ""   alive on [timestamp, timestamp + ttl), forever if ttl is None
        raise NotImplementedError

    def get_at(self, key: str, timestamp: int) -> str:
        raise NotImplementedError

    def delete_at(self, key: str, timestamp: int) -> str:
        # -> "true" | "false"
        raise NotImplementedError

    def backup(self, timestamp: int) -> int:
        # -> number of alive keys saved
        raise NotImplementedError

    def restore(self, timestamp: int, time_at: int) -> str:
        # -> ""   restore latest backup taken at or before time_at, re-basing lifespans
        raise NotImplementedError
