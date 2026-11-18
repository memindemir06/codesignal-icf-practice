# Drill 01 — Top-N ranking with tie-breaks

> Rank N things with a tie-break. The single most common Level 2 task.
>
> The single most common Level 2 task. If this isn't automatic, you lose 10 minutes in the exam.

**Target: 12 minutes.** Traps exercised: T12, T13, T14, T15, T18, T4.

Implement `Leaderboard` in `solution.py`.

- `add_player(player_id: str, team: str) -> bool`
  Registers a player. Returns `True` if added, `False` if `player_id` already exists
  (the existing player's team is **not** changed).

- `record(player_id: str, points: int) -> int | None`
  Adds `points` to the player's total. Returns the new total, or `None` if the player
  doesn't exist. `points` may be negative; totals may go negative.

- `top(n: int) -> list[str]`
  The `n` players with the highest totals, descending. Ties broken by `player_id`
  ascending (lexicographic). Format each entry as `"<player_id>(<total>)"`.
  - Players who have never scored still appear, with a total of `0`.
  - If fewer than `n` players exist, return all of them.
  - Returns `[]` if there are no players.

- `top_in_team(n: int, team: str) -> str`
  Same ranking, but only over players in `team`, and returned as a **single string**
  joined by `", "` — e.g. `"amy(30), bob(30), cal(10)"`.
  Returns `""` if no player belongs to `team`.

### Example

```
add_player("cal", "red")   -> True
add_player("amy", "red")   -> True
add_player("bob", "blue")  -> True
add_player("amy", "blue")  -> False        # already exists, still in "red"
top(3)                     -> ['amy(0)', 'bob(0)', 'cal(0)']
record("cal", 10)          -> 10
record("amy", 30)          -> 30
record("bob", 30)          -> 30
record("zoe", 5)           -> None
top(2)                     -> ['amy(30)', 'bob(30)']
top(10)                    -> ['amy(30)', 'bob(30)', 'cal(10)']
top_in_team(5, "red")      -> "amy(30), cal(10)"
top_in_team(5, "green")    -> ""
```

Run: `./run d01`   ·   Peek at the answer: `./run --ref d01`, then read `reference.py`.
