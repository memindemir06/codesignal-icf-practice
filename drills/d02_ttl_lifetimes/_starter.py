class Store:
    def __init__(self):
        pass

    def set_at(self, key: str, value: str, timestamp: int) -> str:
        # -> ""   (no expiry)
        raise NotImplementedError

    def set_at_with_ttl(self, key: str, value: str, timestamp: int, ttl: int) -> str:
        # -> ""   alive on [timestamp, timestamp + ttl)
        raise NotImplementedError

    def get_at(self, key: str, timestamp: int) -> str:
        # -> value | "" if missing or expired
        raise NotImplementedError

    def delete_at(self, key: str, timestamp: int) -> str:
        # -> "true" | "false"   (strings!)
        raise NotImplementedError

    def count_at(self, timestamp: int) -> int:
        raise NotImplementedError

    def keys_at(self, timestamp: int):
        # -> sorted list of alive keys
        raise NotImplementedError
