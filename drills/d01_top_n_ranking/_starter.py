class Leaderboard:
    def __init__(self):
        pass

    def add_player(self, player_id: str, team: str) -> bool:
        # -> True if added, False if player_id already exists
        raise NotImplementedError

    def record(self, player_id: str, points: int):
        # -> new total | None if player missing
        raise NotImplementedError

    def top(self, n: int):
        # -> list[str] like ['amy(30)', 'bob(30)']
        raise NotImplementedError

    def top_in_team(self, n: int, team: str) -> str:
        # -> "amy(30), cal(10)"  |  "" if no players in team
        raise NotImplementedError
