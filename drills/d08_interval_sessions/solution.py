class Attendance:
    def __init__(self):
        pass

    def add_worker(self, worker_id: str, rate: int) -> str:
        # -> "true" | "false"
        raise NotImplementedError

    def punch(self, worker_id: str, timestamp: int) -> str:
        # -> "registered" | "invalid_request"
        raise NotImplementedError

    def total(self, worker_id: str) -> str:
        # -> stringified total of FINISHED sessions | ""
        raise NotImplementedError

    def pay(self, worker_id: str, start: int, end: int):
        # -> rate * overlap of finished sessions with [start, end] | None
        raise NotImplementedError

    def top(self, n: int):
        # -> ['id(total)', ...]
        raise NotImplementedError
