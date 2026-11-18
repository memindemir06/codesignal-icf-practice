import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel2(unittest.TestCase):
    def setUp(self):
        self.r = M.WorkRegister()
        for w in ("John", "Jason", "Ashley"):
            self.r.add_worker(w, "Junior Developer", 120)
        self.r.add_worker("Ellie", "Senior Developer", 400)
        self.r.register("John", 100)
        self.r.register("John", 150)
        self.r.register("Jason", 200)
        self.r.register("Jason", 250)
        self.r.register("Ashley", 300)
        self.r.register("Ashley", 310)

    def test_ranking_and_tiebreak(self):
        self.assertEqual(self.r.top_n_workers(3, "Junior Developer"),
                         "Jason(50), John(50), Ashley(10)")

    def test_n_limits_the_list(self):
        self.assertEqual(self.r.top_n_workers(1, "Junior Developer"), "Jason(50)")

    def test_workers_with_no_sessions_appear(self):
        self.assertEqual(self.r.top_n_workers(5, "Senior Developer"), "Ellie(0)")

    def test_unknown_position(self):
        self.assertEqual(self.r.top_n_workers(5, "Designer"), "")

    def test_fewer_than_n(self):
        self.assertEqual(self.r.top_n_workers(99, "Junior Developer"),
                         "Jason(50), John(50), Ashley(10)")

    def test_open_sessions_excluded_from_ranking(self):
        self.r.register("Ellie", 400)
        self.assertEqual(self.r.top_n_workers(5, "Senior Developer"), "Ellie(0)")
        self.r.register("Ellie", 500)
        self.assertEqual(self.r.top_n_workers(5, "Senior Developer"), "Ellie(100)")

    def test_no_workers_at_all(self):
        self.assertEqual(M.WorkRegister().top_n_workers(5, "Dev"), "")


if __name__ == "__main__":
    unittest.main()
