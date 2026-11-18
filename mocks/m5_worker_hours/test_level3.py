import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.r = M.WorkRegister()

    def test_spec_walkthrough(self):
        self.r.add_worker("John", "Middle Developer", 200)
        self.r.register("John", 100)
        self.r.register("John", 125)
        self.assertEqual(self.r.promote("John", "Senior Developer", 500, 200), "success")
        self.assertEqual(self.r.promote("John", "Staff Developer", 900, 300),
                         "invalid_request")
        self.assertEqual(self.r.register("John", 300), "registered")
        self.r.register("John", 350)
        self.assertEqual(self.r.get("John"), "75")
        self.assertEqual(self.r.top_n_workers(5, "Middle Developer"), "")
        self.assertEqual(self.r.top_n_workers(5, "Senior Developer"), "John(75)")
        self.assertEqual(self.r.calc_salary("John", 0, 1000), "30000")
        self.assertEqual(self.r.calc_salary("John", 110, 320), "13000")
        self.assertEqual(self.r.calc_salary("John", 0, 100), "0")
        self.assertEqual(self.r.calc_salary("Walter", 0, 10), "")

    def test_promote_unknown_worker(self):
        self.assertEqual(self.r.promote("Ghost", "Dev", 1, 1), "invalid_request")

    def test_promotion_waits_for_the_next_entry(self):
        self.r.add_worker("A", "Junior", 100)
        self.r.register("A", 10)
        self.assertEqual(self.r.promote("A", "Senior", 300, 20), "success")
        self.r.register("A", 30)      # this is an EXIT -- still Junior
        self.assertEqual(self.r.top_n_workers(5, "Junior"), "A(20)")
        self.assertEqual(self.r.calc_salary("A", 0, 100), "2000")
        self.r.register("A", 40)      # entry -- promotion applies now
        self.r.register("A", 50)
        self.assertEqual(self.r.top_n_workers(5, "Senior"), "A(30)")
        self.assertEqual(self.r.calc_salary("A", 0, 100), str(20 * 100 + 10 * 300))

    def test_a_second_promotion_is_allowed_once_the_first_landed(self):
        self.r.add_worker("A", "P1", 100)
        self.assertEqual(self.r.promote("A", "P2", 200, 10), "success")
        self.r.register("A", 20)
        self.r.register("A", 30)
        self.assertEqual(self.r.promote("A", "P3", 300, 40), "success")
        self.r.register("A", 50)
        self.r.register("A", 60)
        self.assertEqual(self.r.calc_salary("A", 0, 1000), str(10 * 200 + 10 * 300))
        self.assertEqual(self.r.top_n_workers(5, "P3"), "A(20)")

    def test_salary_window_clipping(self):
        self.r.add_worker("A", "Dev", 10)
        self.r.register("A", 100)
        self.r.register("A", 200)
        self.assertEqual(self.r.calc_salary("A", 0, 1000), "1000")
        self.assertEqual(self.r.calc_salary("A", 150, 1000), "500")
        self.assertEqual(self.r.calc_salary("A", 0, 150), "500")
        self.assertEqual(self.r.calc_salary("A", 120, 180), "600")
        self.assertEqual(self.r.calc_salary("A", 0, 100), "0")
        self.assertEqual(self.r.calc_salary("A", 200, 300), "0")

    def test_open_session_is_not_paid(self):
        self.r.add_worker("A", "Dev", 10)
        self.r.register("A", 100)
        self.assertEqual(self.r.calc_salary("A", 0, 1000), "0")

    def test_get_spans_all_positions(self):
        self.r.add_worker("A", "P1", 100)
        self.r.register("A", 10)
        self.r.register("A", 20)
        self.r.promote("A", "P2", 200, 30)
        self.r.register("A", 30)
        self.r.register("A", 45)
        self.assertEqual(self.r.get("A"), "25")


if __name__ == "__main__":
    unittest.main()
