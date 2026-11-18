import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLeaderboard(unittest.TestCase):
    def setUp(self):
        self.lb = M.Leaderboard()

    def test_add_and_duplicate(self):
        self.assertIs(self.lb.add_player("cal", "red"), True)
        self.assertIs(self.lb.add_player("cal", "blue"), False)
        self.lb.record("cal", 5)
        self.assertEqual(self.lb.top_in_team(5, "red"), "cal(5)")
        self.assertEqual(self.lb.top_in_team(5, "blue"), "")

    def test_record_missing_player(self):
        self.assertIsNone(self.lb.record("nobody", 5))

    def test_record_returns_running_total(self):
        self.lb.add_player("amy", "red")
        self.assertEqual(self.lb.record("amy", 10), 10)
        self.assertEqual(self.lb.record("amy", 5), 15)
        self.assertEqual(self.lb.record("amy", -20), -5)

    def test_zero_score_players_still_ranked_alphabetically(self):
        for p in ("cal", "amy", "bob"):
            self.lb.add_player(p, "red")
        self.assertEqual(self.lb.top(3), ["amy(0)", "bob(0)", "cal(0)"])

    def test_tie_break_is_alphabetical_ascending(self):
        for p in ("cal", "amy", "bob"):
            self.lb.add_player(p, "red")
        self.lb.record("cal", 10)
        self.lb.record("amy", 30)
        self.lb.record("bob", 30)
        self.assertEqual(self.lb.top(2), ["amy(30)", "bob(30)"])
        self.assertEqual(self.lb.top(10), ["amy(30)", "bob(30)", "cal(10)"])

    def test_fewer_than_n(self):
        self.lb.add_player("amy", "red")
        self.assertEqual(self.lb.top(99), ["amy(0)"])

    def test_n_zero_and_empty(self):
        self.assertEqual(self.lb.top(3), [])
        self.lb.add_player("amy", "red")
        self.assertEqual(self.lb.top(0), [])
        self.assertEqual(self.lb.top_in_team(0, "red"), "")

    def test_team_filter_pool(self):
        self.lb.add_player("amy", "red")
        self.lb.add_player("bob", "blue")
        self.lb.add_player("cal", "red")
        self.lb.record("bob", 100)
        self.lb.record("amy", 30)
        self.lb.record("cal", 10)
        self.assertEqual(self.lb.top_in_team(5, "red"), "amy(30), cal(10)")
        self.assertEqual(self.lb.top_in_team(5, "green"), "")
        self.assertEqual(self.lb.top(5), ["bob(100)", "amy(30)", "cal(10)"])

    def test_negative_totals_sort_correctly(self):
        for p in ("a", "b", "c"):
            self.lb.add_player(p, "red")
        self.lb.record("a", -5)
        self.lb.record("b", -5)
        self.lb.record("c", -1)
        self.assertEqual(self.lb.top(3), ["c(-1)", "a(-5)", "b(-5)"])


if __name__ == "__main__":
    unittest.main()
