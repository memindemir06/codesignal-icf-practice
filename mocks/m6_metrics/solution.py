class MetricsService:
    def __init__(self):
        pass

    # ---------- level 1 ----------
    def record(self, timestamp: int, metric: str, value: int) -> int:
        raise NotImplementedError

    def latest(self, timestamp: int, metric: str):
        raise NotImplementedError

    def remove(self, timestamp: int, metric: str) -> bool:
        raise NotImplementedError

    # ---------- level 2 ----------
    def summary(self, timestamp: int, metric: str, window: int) -> str:
        # -> "min(<min>) max(<max>) avg(<avg>)" | ""
        raise NotImplementedError

    def top_metrics(self, timestamp: int, n: int):
        # -> ['name(count)', ...]
        raise NotImplementedError

    # ---------- level 3 ----------
    def set_retention(self, timestamp: int, metric: str, ttl: int) -> bool:
        raise NotImplementedError

    # ---------- level 4 ----------
    def snapshot(self, timestamp: int) -> int:
        raise NotImplementedError

    def rollback(self, timestamp: int, time_at: int) -> str:
        raise NotImplementedError
