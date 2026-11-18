class Registry:
    def __init__(self):
        pass

    def create(self, timestamp: int, account_id: str) -> bool:
        raise NotImplementedError

    def deposit(self, timestamp: int, account_id: str, amount: int):
        # -> balance after | None
        raise NotImplementedError

    def transfer(self, timestamp: int, source: str, target: str, amount: int):
        # -> source balance after | None
        raise NotImplementedError

    def top_spenders(self, timestamp: int, n: int):
        # -> ['id(total_out)', ...]
        raise NotImplementedError

    def balance_at(self, timestamp: int, account_id: str, time_at: int):
        # -> balance at end of time_at | None
        raise NotImplementedError

    def merge(self, timestamp: int, keep_id: str, drop_id: str) -> bool:
        raise NotImplementedError
