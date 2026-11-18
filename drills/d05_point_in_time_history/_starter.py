class Ledger:
    def __init__(self):
        pass

    def open(self, timestamp: int, account_id: str) -> bool:
        raise NotImplementedError

    def credit(self, timestamp: int, account_id: str, amount: int):
        # -> balance after | None
        raise NotImplementedError

    def debit(self, timestamp: int, account_id: str, amount: int):
        # -> balance after | None (missing / insufficient)
        raise NotImplementedError

    def close(self, timestamp: int, account_id: str) -> bool:
        raise NotImplementedError

    def balance_at(self, timestamp: int, account_id: str, time_at: int):
        # -> balance as of the END of time_at | None if it did not exist then
        raise NotImplementedError
