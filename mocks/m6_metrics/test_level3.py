import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.s = M.MetricsService()

    def test_spec_walkthrough(self):
        self.assertEqual(self.s.record(10, "cpu", 40), 1)
        self.assertEqual(self.s.record(20, "cpu", 60), 2)
        self.assertIs(self.s.set_retention(21, "cpu", 15), True)
        self.assertIs(self.s.set_retention(22, "disk", 15), False)
        self.assertEqual(self.s.record(25, "cpu", 50), 2)
        self.assertEqual(self.s.latest(26, "cpu"), 50)
        self.assertEqual(self.s.summary(26, "cpu", 100), "min(50) max(60) avg(55)")
        self.assertEqual(self.s.summary(35, "cpu", 100), "min(50) max(50) avg(50)")
        self.assertEqual(self.s.top_metrics(41, 5), ["cpu(0)"])
        self.assertIsNone(self.s.latest(41, "cpu"))
        self.assertIs(self.s.set_retention(42, "cpu", 1000), True)
        self.assertEqual(self.s.latest(43, "cpu"), 50)

    def test_retention_boundary_is_strict(self):
        self.s.record(10, "m", 1)
        self.s.set_retention(11, "m", 5)
        self.assertEqual(self.s.latest(14, "m"), 1)
        self.assertIsNone(self.s.latest(15, "m"))

    def test_no_retention_means_forever(self):
        self.s.record(1, "m", 7)
        self.assertEqual(self.s.latest(10 ** 9, "m"), 7)

    def test_retention_replaces_not_accumulates(self):
        self.s.record(10, "m", 1)
        self.s.set_retention(11, "m", 1000)
        self.s.set_retention(12, "m", 5)
        self.assertIsNone(self.s.latest(20, "m"))

    def test_aged_out_metric_still_exists(self):
        self.s.record(10, "m", 1)
        self.s.set_retention(11, "m", 2)
        self.assertEqual(self.s.top_metrics(50, 5), ["m(0)"])
        self.assertIs(self.s.set_retention(51, "m", 3), True)
        self.assertIs(self.s.remove(52, "m"), True)
        self.assertIs(self.s.remove(53, "m"), False)

    def test_summary_respects_both_window_and_retention(self):
        self.s.record(10, "m", 10)
        self.s.record(20, "m", 20)
        self.s.record(30, "m", 30)
        self.s.set_retention(31, "m", 15)
        self.assertEqual(self.s.summary(32, "m", 100), "min(20) max(30) avg(25)")
        self.assertEqual(self.s.summary(33, "m", 5), "min(30) max(30) avg(30)")

    def test_top_metrics_ranks_by_visible_count(self):
        self.s.record(1, "old", 1)
        self.s.record(2, "old", 1)
        self.s.record(3, "old", 1)
        self.s.record(4, "new", 1)
        self.s.set_retention(5, "old", 2)
        self.assertEqual(self.s.top_metrics(6, 5), ["new(1)", "old(0)"])

    def test_record_returns_visible_count(self):
        self.s.record(10, "m", 1)
        self.s.record(11, "m", 1)
        self.s.set_retention(12, "m", 3)
        self.assertEqual(self.s.record(13, "m", 1), 2)
        self.assertEqual(self.s.record(100, "m", 1), 1)

    def test_backward_compatibility_without_retention(self):
        self.s.record(10, "cpu", 40)
        self.s.record(20, "cpu", 60)
        self.assertEqual(self.s.latest(30, "cpu"), 60)
        self.assertEqual(self.s.summary(30, "cpu", 100), "min(40) max(60) avg(50)")
        self.assertEqual(self.s.top_metrics(30, 5), ["cpu(2)"])


if __name__ == "__main__":
    unittest.main()
