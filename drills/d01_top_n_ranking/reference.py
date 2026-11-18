class Leaderboard:
    def __init__(self):
        self.teams = {}    # player_id -> team
        self.points = {}   # player_id -> total

    def add_player(self, player_id: str, team: str) -> bool:
        if player_id in self.teams:
            return False
        self.teams[player_id] = team
        self.points[player_id] = 0
        return True

    def record(self, player_id: str, points: int):
        if player_id not in self.points:
            return None
        self.points[player_id] += points
        return self.points[player_id]

    def _ranked(self, n, team=None):
        pool = [(pid, tot) for pid, tot in self.points.items()
                if team is None or self.teams[pid] == team]
        # descending by total, ties ascending by id -- never sorted(reverse=True) on a tuple
        pool.sort(key=lambda kv: (-kv[1], kv[0]))
        return pool[:n]

    def top(self, n: int):
        return ["%s(%d)" % (pid, tot) for pid, tot in self._ranked(n)]

    def top_in_team(self, n: int, team: str) -> str:
        return ", ".join("%s(%d)" % (pid, tot) for pid, tot in self._ranked(n, team))
