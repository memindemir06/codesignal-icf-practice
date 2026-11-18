WAIT = 3600


class Rewards:
    def __init__(self):
        pass

    def _settle(self, timestamp: int) -> None:
        """Credit every reward due at or before timestamp.
        Call this as the FIRST line of every public method."""
        raise NotImplementedError

    def open_account(self, timestamp: int, account_id: str) -> bool:
        raise NotImplementedError

    def deposit(self, timestamp: int, account_id: str, amount: int):
        # -> balance after | None
        raise NotImplementedError

    def spend(self, timestamp: int, account_id: str, amount: int):
        # -> "reward<N>" | None (missing account / insufficient funds)
        raise NotImplementedError

    def reward_status(self, timestamp: int, account_id: str, reward_id: str):
        # -> "PENDING" | "PAID" | None
        raise NotImplementedError

    def balance(self, timestamp: int, account_id: str):
        # -> balance | None
        raise NotImplementedError
