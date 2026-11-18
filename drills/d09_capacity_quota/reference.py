class User:
    def __init__(self, user_id, capacity):
        self.id = user_id
        self.capacity = capacity
        self.used = 0

    @property
    def remaining(self):
        return self.capacity - self.used


class Drive:
    def __init__(self):
        self.users = {}
        self.files = {}     # name -> (size, owner_id)

    def add_user(self, user_id, capacity):
        if user_id in self.users:
            return False
        self.users[user_id] = User(user_id, capacity)
        return True

    def add_file(self, user_id, name, size):
        user = self.users.get(user_id)
        # validate everything BEFORE mutating anything
        if user is None or name in self.files or user.remaining < size:
            return None
        self.files[name] = (size, user_id)
        user.used += size
        return user.remaining

    def delete_file(self, name):
        entry = self.files.pop(name, None)
        if entry is None:
            return None
        size, owner = entry
        self.users[owner].used -= size
        return size

    def get_owner(self, name):
        entry = self.files.get(name)
        return None if entry is None else entry[1]

    def merge_users(self, keep_id, drop_id):
        if keep_id == drop_id:
            return None
        keep = self.users.get(keep_id)
        drop = self.users.get(drop_id)
        if keep is None or drop is None:
            return None
        for name, (size, owner) in list(self.files.items()):
            if owner == drop_id:
                self.files[name] = (size, keep_id)
        keep.capacity += drop.capacity
        keep.used += drop.used
        del self.users[drop_id]
        return keep.remaining

    def top_users(self, n):
        pool = [(u.id, u.used) for u in self.users.values()]
        pool.sort(key=lambda kv: (-kv[1], kv[0]))
        return ["%s(%d)" % (uid, used) for uid, used in pool[:n]]
