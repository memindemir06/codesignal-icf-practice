import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.r = M.WorkRegister()
        self.r.add_worker("John", "Dev", 10)
        self.r.register("John", 0)
        self.r.register("John", 100)

    def test_spec_walkthrough(self):
        self.assertEqual(self.r.calc_salary("John", 0, 100), "1000")
        self.assertEqual(self.r.add_double_pay_period(20, 40), "true")
        self.assertEqual(self.r.calc_salary("John", 0, 100), "1200")
        self.assertEqual(self.r.add_double_pay_period(30, 50), "false")
        self.assertEqual(self.r.add_double_pay_period(40, 60), "true")
        self.assertEqual(self.r.add_double_pay_period(90, 90), "false")
        self.assertEqual(self.r.calc_salary("John", 0, 100), "1400")
        self.assertEqual(self.r.calc_salary("John", 0, 30), "400")

    def test_overlap_rejections(self):
        self.assertEqual(self.r.add_double_pay_period(100, 200), "true")
        self.assertEqual(self.r.add_double_pay_period(150, 160), "false")   # inside
        self.assertEqual(self.r.add_double_pay_period(50, 250), "false")    # around
        self.assertEqual(self.r.add_double_pay_period(50, 101), "false")    # left edge
        self.assertEqual(self.r.add_double_pay_period(199, 300), "false")   # right edge
        self.assertEqual(self.r.add_double_pay_period(50, 100), "true")     # touching
        self.assertEqual(self.r.add_double_pay_period(200, 300), "true")    # touching
        self.assertEqual(self.r.add_double_pay_period(10, 5), "false")      # inverted

    def test_double_pay_added_after_the_work(self):
        self.assertEqual(self.r.calc_salary("John", 0, 100), "1000")
        self.r.add_double_pay_period(0, 100)
        self.assertEqual(self.r.calc_salary("John", 0, 100), "2000")

    def test_double_pay_outside_the_salary_window_is_ignored(self):
        self.r.add_double_pay_period(200, 300)
        self.assertEqual(self.r.calc_salary("John", 0, 100), "1000")

    def test_double_pay_partially_overlapping_the_window(self):
        self.r.add_double_pay_period(80, 200)
        self.assertEqual(self.r.calc_salary("John", 0, 100), "1200")
        self.assertEqual(self.r.calc_salary("John", 0, 90), "1000")

    def test_double_pay_applies_to_every_worker_and_rate(self):
        self.r.add_worker("Ann", "Dev", 100)
        self.r.register("Ann", 200)
        self.r.register("Ann", 300)
        self.r.add_double_pay_period(250, 300)
        self.assertEqual(self.r.calc_salary("Ann", 0, 1000), str(100 * 100 + 50 * 100))
        self.assertEqual(self.r.calc_salary("John", 0, 1000), "1000")

    def test_double_pay_with_promotion_rates(self):
        r = M.WorkRegister()
        r.add_worker("A", "P1", 10)
        r.register("A", 0)
        r.register("A", 100)
        r.promote("A", "P2", 20, 200)
        r.register("A", 200)
        r.register("A", 300)
        r.add_double_pay_period(50, 250)
        # session1 [0,100) at 10: 100*10 + 50*10 = 1500
        # session2 [200,300) at 20: 100*20 + 50*20 = 3000
        self.assertEqual(r.calc_salary("A", 0, 1000), "4500")

    def test_multiple_double_pay_periods_in_one_session(self):
        self.r.add_double_pay_period(10, 20)
        self.r.add_double_pay_period(30, 40)
        self.r.add_double_pay_period(50, 60)
        self.assertEqual(self.r.calc_salary("John", 0, 100), str(1000 + 30 * 10))

    def test_unknown_worker_still_returns_empty(self):
        self.r.add_double_pay_period(0, 100)
        self.assertEqual(self.r.calc_salary("Ghost", 0, 100), "")


if __name__ == "__main__":
    unittest.main()
