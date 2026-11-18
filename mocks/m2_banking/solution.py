MILLISECONDS_IN_1_DAY = 86400000


class BankingSystem:
    def __init__(self):
        pass

    # ---------- level 1 ----------
    def create_account(self, timestamp: int, account_id: str) -> bool:
        raise NotImplementedError

    def deposit(self, timestamp: int, account_id: str, amount: int):
        raise NotImplementedError

    def transfer(self, timestamp: int, source_account_id: str,
                 target_account_id: str, amount: int):
        raise NotImplementedError

    # ---------- level 2 ----------
    def top_spenders(self, timestamp: int, n: int):
        raise NotImplementedError

    # ---------- level 3 ----------
    def pay(self, timestamp: int, account_id: str, amount: int):
        raise NotImplementedError

    def get_payment_status(self, timestamp: int, account_id: str, payment: str):
        raise NotImplementedError

    # ---------- level 4 ----------
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        raise NotImplementedError

    def get_balance(self, timestamp: int, account_id: str, time_at: int):
        raise NotImplementedError
