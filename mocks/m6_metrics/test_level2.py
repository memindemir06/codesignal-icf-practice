import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel2(unittest.TestCase):
    def setUp(self):
        self.s = M.MetricsService()
        self.s.record(10, "cpu", 40)
        self.s.record(20, "cpu", 60)
        self.s.record(30, "cpu", 50)
        self.s.record(31, "mem", 7)

    def test_summary_over_whole_history(self):
        self.assertEqual(self.s.summary(32, "cpu", 100), "min(40) max(60) avg(50)")

    def test_summary_window_is_closed_on_both_ends(self):
        self.assertEqual(self.s.summary(33, "cpu", 15), "min(50) max(60) avg(55)")
        self.assertEqual(self.s.summary(34, "cpu", 4), "min(50) max(50) avg(50)")

    def test_summary_empty_cases(self):
        self.assertEqual(self.s.summary(35, "cpu", 1), "")
        self.assertEqual(self.s.summary(36, "disk", 100), "")

    def test_summary_boundary_sample_is_included(self):
        s = M.MetricsService()
        s.record(10, "m", 1)
        self.assertEqual(s.summary(20, "m", 10), "min(1) max(1) avg(1)")
        self.assertEqual(s.summary(21, "m", 10), "")

    def test_average_floors_towards_negative_infinity(self):
        s = M.MetricsService()
        s.record(1, "m", -3)
        s.record(2, "m", -4)
        self.assertEqual(s.summary(3, "m", 100), "min(-4) max(-3) avg(-4)")
        s2 = M.MetricsService()
        s2.record(1, "m", 3)
        s2.record(2, "m", 4)
        self.assertEqual(s2.summary(3, "m", 100), "min(3) max(4) avg(3)")

    def test_top_metrics(self):
        self.assertEqual(self.s.top_metrics(40, 5), ["cpu(3)", "mem(1)"])
        self.assertEqual(self.s.top_metrics(41, 1), ["cpu(3)"])

    def test_top_metrics_tie_is_alphabetical(self):
        s = M.MetricsService()
        for i, name in enumerate(["zeta", "alpha", "mid"], start=1):
            s.record(i, name, 1)
        self.assertEqual(s.top_metrics(10, 5), ["alpha(1)", "mid(1)", "zeta(1)"])

    def test_top_metrics_empty(self):
        self.assertEqual(M.MetricsService().top_metrics(1, 5), [])

    def test_removed_metric_leaves_the_ranking(self):
        self.s.remove(40, "cpu")
        self.assertEqual(self.s.top_metrics(41, 5), ["mem(1)"])


if __name__ == "__main__":
    unittest.main()
