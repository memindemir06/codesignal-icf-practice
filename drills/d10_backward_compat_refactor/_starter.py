"""Feature flag service -- Levels 1 & 2 are done. Add the Level 3 `_at` variants below
without changing the behaviour of the existing methods."""


class Flags:
    def __init__(self):
        # account -> set of enabled flags
        self.enabled = {}

    # ---------- level 1 ----------
    def enable(self, account: str, flag: str) -> str:
        self.enabled.setdefault(account, set()).add(flag)
        return ""

    def disable(self, account: str, flag: str) -> str:
        flags = self.enabled.get(account)
        if flags is None or flag not in flags:
            return "false"
        flags.remove(flag)
        return "true"

    def is_enabled(self, account: str, flag: str) -> str:
        return "true" if flag in self.enabled.get(account, ()) else "false"

    # ---------- level 2 ----------
    def list_flags(self, account: str, prefix: str) -> str:
        flags = self.enabled.get(account, set())
        return ", ".join(sorted(f for f in flags if f.startswith(prefix)))

    # ---------- level 3: your turn ----------
    def enable_at(self, account: str, flag: str, timestamp: int) -> str:
        raise NotImplementedError

    def enable_at_with_ttl(self, account: str, flag: str, timestamp: int, ttl: int) -> str:
        raise NotImplementedError

    def disable_at(self, account: str, flag: str, timestamp: int) -> str:
        raise NotImplementedError

    def is_enabled_at(self, account: str, flag: str, timestamp: int) -> str:
        raise NotImplementedError

    def list_flags_at(self, account: str, prefix: str, timestamp: int) -> str:
        raise NotImplementedError
