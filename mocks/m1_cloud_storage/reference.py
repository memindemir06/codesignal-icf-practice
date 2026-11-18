"""Worked reference solution for Mock 1.

Read `docs/04-architecture-playbook.md` alongside this: the entity, the additive metric
(`used`), and the ownership indirection are all decided at level 1 so that levels 3 and 4
are additive rather than a rewrite.
"""
from dataclasses import dataclass, field

UNOWNED = None
SEARCH_LIMIT = 10


@dataclass
class User:
    id: str
    capacity: int
    used: int = 0
    backup: dict = None          # {name: size} or None if never backed up

    @property
    def remaining(self):
        return self.capacity - self.used


@dataclass
class File:
    name: str
    size: int
    owner: str = UNOWNED


class CloudStorage:
    def __init__(self):
        self.files: dict = {}    # name -> File
        self.users: dict = {}    # user_id -> User

    # ---------- helpers, written at level 1 ----------
    def _charge(self, owner, size):
        if owner is not UNOWNED:
            self.users[owner].used += size

    def _refund(self, owner, size):
        if owner is not UNOWNED:
            self.users[owner].used -= size

    def _affordable(self, owner, size):
        return owner is UNOWNED or self.users[owner].remaining >= size

    # ---------- level 1 ----------
    def add_file(self, name, size):
        if name in self.files:
            return False
        self.files[name] = File(name, size, UNOWNED)
        return True

    def get_file_size(self, name):
        f = self.files.get(name)
        return None if f is None else f.size

    def delete_file(self, name):
        f = self.files.pop(name, None)
        if f is None:
            return None
        self._refund(f.owner, f.size)
        return f.size

    def copy_file(self, source, dest):
        src = self.files.get(source)
        if src is None:
            return False
        if source == dest:
            return True
        existing = self.files.get(dest)
        # overwriting a file you already own frees that space first
        head_room = existing.size if existing is not None and existing.owner == src.owner else 0
        if not self._affordable(src.owner, src.size - head_room):
            return False
        if existing is not None:
            self._refund(existing.owner, existing.size)
        self._charge(src.owner, src.size)
        self.files[dest] = File(dest, src.size, src.owner)
        return True

    # ---------- level 2 ----------
    def find_file(self, prefix, suffix):
        hits = [f for f in self.files.values()
                if f.name.startswith(prefix) and f.name.endswith(suffix)]
        hits.sort(key=lambda f: (-f.size, f.name))
        return ["%s(%d)" % (f.name, f.size) for f in hits[:SEARCH_LIMIT]]

    # ---------- level 3 ----------
    def add_user(self, user_id, capacity):
        if user_id in self.users:
            return False
        self.users[user_id] = User(user_id, capacity)
        return True

    def add_file_by(self, user_id, name, size):
        user = self.users.get(user_id)
        if user is None or name in self.files or user.remaining < size:
            return None
        self.files[name] = File(name, size, user_id)
        user.used += size
        return user.remaining

    def merge_user(self, user_id_1, user_id_2):
        if user_id_1 == user_id_2:
            return None
        keep = self.users.get(user_id_1)
        drop = self.users.get(user_id_2)
        if keep is None or drop is None:
            return None
        for f in self.files.values():
            if f.owner == user_id_2:
                f.owner = user_id_1
        keep.capacity += drop.capacity
        keep.used += drop.used
        del self.users[user_id_2]          # drop's backup goes with it
        return keep.remaining

    # ---------- level 4 ----------
    def backup_user(self, user_id):
        user = self.users.get(user_id)
        if user is None:
            return None
        user.backup = {f.name: f.size for f in self.files.values() if f.owner == user_id}
        return len(user.backup)

    def restore_user(self, user_id):
        user = self.users.get(user_id)
        if user is None:
            return False
        for name in [f.name for f in self.files.values() if f.owner == user_id]:
            self.delete_file(name)
        for name, size in (user.backup or {}).items():
            if name in self.files:
                continue                    # taken by someone else now -- skip
            self.files[name] = File(name, size, user_id)
            user.used += size               # deliberately ignores the capacity limit
        return True
