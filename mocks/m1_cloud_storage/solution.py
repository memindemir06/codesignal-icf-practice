class CloudStorage:
    def __init__(self):
        pass

    # ---------- level 1 ----------
    def add_file(self, name: str, size: int) -> bool:
        raise NotImplementedError

    def get_file_size(self, name: str):
        raise NotImplementedError

    def delete_file(self, name: str):
        raise NotImplementedError

    def copy_file(self, source: str, dest: str) -> bool:
        raise NotImplementedError

    # ---------- level 2 ----------
    def find_file(self, prefix: str, suffix: str):
        raise NotImplementedError

    # ---------- level 3 ----------
    def add_user(self, user_id: str, capacity: int) -> bool:
        raise NotImplementedError

    def add_file_by(self, user_id: str, name: str, size: int):
        raise NotImplementedError

    def merge_user(self, user_id_1: str, user_id_2: str):
        raise NotImplementedError

    # ---------- level 4 ----------
    def backup_user(self, user_id: str):
        raise NotImplementedError

    def restore_user(self, user_id: str) -> bool:
        raise NotImplementedError
