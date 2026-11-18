class WorkRegister:
    def __init__(self):
        pass

    # ---------- level 1 ----------
    def add_worker(self, worker_id: str, position: str, compensation: int) -> str:
        # -> "true" | "false"
        raise NotImplementedError

    def register(self, worker_id: str, timestamp: int) -> str:
        # -> "registered" | "invalid_request"
        raise NotImplementedError

    def get(self, worker_id: str) -> str:
        # -> stringified total of finished sessions | ""
        raise NotImplementedError

    # ---------- level 2 ----------
    def top_n_workers(self, n: int, position: str) -> str:
        # -> "id(time), id(time)" | ""
        raise NotImplementedError

    # ---------- level 3 ----------
    def promote(self, worker_id: str, new_position: str,
                new_compensation: int, start_timestamp: int) -> str:
        # -> "success" | "invalid_request"
        raise NotImplementedError

    def calc_salary(self, worker_id: str, start_timestamp: int, end_timestamp: int) -> str:
        # -> stringified salary | ""
        raise NotImplementedError

    # ---------- level 4 ----------
    def add_double_pay_period(self, start_timestamp: int, end_timestamp: int) -> str:
        # -> "true" | "false"
        raise NotImplementedError
