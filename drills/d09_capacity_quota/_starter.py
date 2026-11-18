class Drive:
    def __init__(self):
        pass

    def add_user(self, user_id: str, capacity: int) -> bool:
        raise NotImplementedError

    def add_file(self, user_id: str, name: str, size: int):
        # -> remaining capacity | None (missing user / name taken / not enough room)
        raise NotImplementedError

    def delete_file(self, name: str):
        # -> size of the deleted file | None
        raise NotImplementedError

    def get_owner(self, name: str):
        raise NotImplementedError

    def merge_users(self, keep_id: str, drop_id: str):
        # -> keep's remaining capacity | None
        raise NotImplementedError

    def top_users(self, n: int):
        # -> ['id(bytes_used)', ...]
        raise NotImplementedError
