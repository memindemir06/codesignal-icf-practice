class FXPlatform:
    def __init__(self):
        pass

    # ---------- level 1 ----------
    def create_client(self, timestamp: int, client_id: str) -> bool:
        raise NotImplementedError

    def deposit(self, timestamp: int, client_id: str, currency: str, amount: int):
        raise NotImplementedError

    def withdraw(self, timestamp: int, client_id: str, currency: str, amount: int):
        raise NotImplementedError

    def get_balance(self, timestamp: int, client_id: str, currency: str):
        raise NotImplementedError

    # ---------- level 2 ----------
    def top_spenders(self, timestamp: int, currency: str, n: int):
        raise NotImplementedError

    # ---------- level 3 ----------
    def quote(self, timestamp: int, from_currency: str, to_currency: str,
              rate_pips: int, ttl: int) -> str:
        raise NotImplementedError

    def execute(self, timestamp: int, client_id: str, quote_id: str, amount: int):
        raise NotImplementedError

    # ---------- level 4 ----------
    def merge_clients(self, timestamp: int, keep_id: str, drop_id: str) -> bool:
        raise NotImplementedError

    def balance_at(self, timestamp: int, client_id: str, currency: str, time_at: int):
        raise NotImplementedError
