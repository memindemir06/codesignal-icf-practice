import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestAttendance(unittest.TestCase):
    def setUp(self):
        self.a = M.Attendance()

    def test_add_and_duplicate(self):
        self.assertEqual(self.a.add_worker("amy", 10), "true")
        self.assertEqual(self.a.add_worker("amy", 99), "false")
        self.a.punch("amy", 1)
        self.a.punch("amy", 3)
        self.assertEqual(self.a.pay("amy", 0, 100), 20)   # rate stayed 10

    def test_unknown_worker(self):
        self.assertEqual(self.a.punch("bob", 5), "invalid_request")
        self.assertEqual(self.a.total("bob"), "")
        self.assertIsNone(self.a.pay("bob", 0, 10))

    def test_total_is_a_string_of_finished_sessions(self):
        self.a.add_worker("amy", 10)
        self.a.punch("amy", 10)
        self.assertEqual(self.a.total("amy"), "0")
        self.a.punch("amy", 25)
        self.assertEqual(self.a.total("amy"), "15")
        self.a.punch("amy", 40)
        self.assertEqual(self.a.total("amy"), "15")       # open session excluded
        self.a.punch("amy", 67)
        self.assertEqual(self.a.total("amy"), "42")

    def test_pay_full_window(self):
        self.a.add_worker("amy", 10)
        self.a.punch("amy", 10)
        self.a.punch("amy", 25)
        self.assertEqual(self.a.pay("amy", 0, 100), 150)

    def test_pay_partial_overlap(self):
        self.a.add_worker("amy", 10)
        self.a.punch("amy", 10)
        self.a.punch("amy", 25)
        self.assertEqual(self.a.pay("amy", 15, 20), 50)
        self.assertEqual(self.a.pay("amy", 20, 100), 50)
        self.assertEqual(self.a.pay("amy", 0, 15), 50)

    def test_pay_no_overlap_and_touching_boundary(self):
        self.a.add_worker("amy", 10)
        self.a.punch("amy", 10)
        self.a.punch("amy", 25)
        self.assertEqual(self.a.pay("amy", 26, 100), 0)
        self.assertEqual(self.a.pay("amy", 0, 9), 0)
        self.assertEqual(self.a.pay("amy", 25, 100), 0)   # zero-width overlap
        self.assertEqual(self.a.pay("amy", 0, 10), 0)

    def test_pay_ignores_open_session(self):
        self.a.add_worker("amy", 10)
        self.a.punch("amy", 10)
        self.a.punch("amy", 25)
        self.a.punch("amy", 40)
        self.assertEqual(self.a.pay("amy", 30, 100), 0)

    def test_pay_across_multiple_sessions(self):
        self.a.add_worker("amy", 2)
        for t in (10, 20, 30, 40, 50, 60):
            self.a.punch("amy", t)
        # sessions (10,20) (30,40) (50,60) -> 30 units
        self.assertEqual(self.a.pay("amy", 0, 100), 60)
        self.assertEqual(self.a.pay("amy", 15, 55), (5 + 10 + 5) * 2)

    def test_top_ranking(self):
        for w in ("cal", "amy", "bob"):
            self.a.add_worker(w, 1)
        self.a.punch("amy", 1)
        self.a.punch("amy", 11)
        self.a.punch("bob", 20)
        self.a.punch("bob", 30)
        self.assertEqual(self.a.top(3), ["amy(10)", "bob(10)", "cal(0)"])
        self.assertEqual(self.a.top(1), ["amy(10)"])
        self.assertEqual(self.a.top(99), ["amy(10)", "bob(10)", "cal(0)"])

    def test_interleaved_workers(self):
        self.a.add_worker("amy", 1)
        self.a.add_worker("bob", 1)
        self.a.punch("amy", 1)
        self.a.punch("bob", 2)
        self.a.punch("amy", 5)
        self.a.punch("bob", 9)
        self.assertEqual(self.a.total("amy"), "4")
        self.assertEqual(self.a.total("bob"), "7")


if __name__ == "__main__":
    unittest.main()
