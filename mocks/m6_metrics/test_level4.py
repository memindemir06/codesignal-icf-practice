import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.s = M.MetricsService()

    def test_spec_walkthrough(self):
        self.s.record(10, "cpu", 40)
        self.s.record(20, "cpu", 60)
        self.s.set_retention(21, "cpu", 15)
        self.assertEqual(self.s.snapshot(25), 1)
        self.s.record(26, "mem", 1)
        self.assertIs(self.s.remove(27, "cpu"), True)
        self.assertEqual(self.s.snapshot(28), 1)
        self.assertEqual(self.s.rollback(100, 26), "")
        self.assertEqual(self.s.latest(101, "cpu"), 60)
        self.assertIsNone(self.s.latest(102, "mem"))
        self.assertEqual(self.s.top_metrics(103, 5), ["cpu(1)"])
        self.assertIsNone(self.s.latest(115, "cpu"))

    def test_snapshot_counts_metrics_with_visible_samples(self):
        self.s.record(1, "a", 1)
        self.s.record(2, "b", 1)
        self.s.set_retention(3, "b", 1)
        self.assertEqual(self.s.snapshot(4), 1)

    def test_snapshot_of_empty_service(self):
        self.assertEqual(self.s.snapshot(1), 0)
        self.s.record(2, "a", 1)
        self.assertEqual(self.s.rollback(3, 1), "")
        self.assertEqual(self.s.top_metrics(4, 5), [])

    def test_rollback_picks_latest_at_or_before(self):
        self.s.record(1, "m", 10)
        self.s.snapshot(2)
        self.s.record(3, "m", 20)
        self.s.snapshot(4)
        self.s.rollback(5, 3)
        self.assertEqual(self.s.latest(6, "m"), 10)
        self.s.rollback(7, 4)
        self.assertEqual(self.s.latest(8, "m"), 20)

    def test_rollback_preserves_sample_ages(self):
        self.s.record(10, "m", 1)
        self.s.record(20, "m", 2)
        self.s.snapshot(30)             # ages 20 and 10
        self.s.rollback(1000, 30)
        self.assertEqual(self.s.summary(1000, "m", 20), "min(1) max(2) avg(1)")
        self.assertEqual(self.s.summary(1001, "m", 11), "min(2) max(2) avg(2)")
        self.assertEqual(self.s.summary(1002, "m", 10), "")

    def test_rollback_restores_retention(self):
        self.s.record(10, "m", 1)
        self.s.set_retention(11, "m", 5)
        self.s.snapshot(12)
        self.s.set_retention(13, "m", 10 ** 9)
        self.assertEqual(self.s.latest(99, "m"), 1)    # visible under the huge retention
        self.s.rollback(100, 12)                       # sample was 2 old -> replayed at 98
        self.assertEqual(self.s.latest(101, "m"), 1)
        self.assertIsNone(self.s.latest(104, "m"))     # the ttl of 5 is back

    def test_rollback_discards_metrics_created_later(self):
        self.s.record(1, "old", 1)
        self.s.snapshot(2)
        self.s.record(3, "new", 1)
        self.s.rollback(4, 2)
        self.assertIsNone(self.s.latest(5, "new"))
        self.assertEqual(self.s.top_metrics(6, 5), ["old(1)"])

    def test_snapshot_drops_invisible_samples(self):
        self.s.record(10, "m", 1)
        self.s.record(20, "m", 2)
        self.s.set_retention(21, "m", 5)
        self.assertEqual(self.s.snapshot(22), 1)
        self.s.set_retention(23, "m", 10 ** 9)
        self.assertEqual(self.s.top_metrics(24, 5), ["m(2)"])
        self.s.rollback(25, 22)
        self.assertEqual(self.s.top_metrics(26, 5), ["m(1)"])

    def test_double_rollback_of_the_same_snapshot(self):
        self.s.record(10, "m", 1)
        self.s.snapshot(11)
        self.s.rollback(100, 11)
        self.s.record(101, "m", 2)
        self.s.record(102, "extra", 9)
        self.s.rollback(200, 11)
        self.assertEqual(self.s.latest(201, "m"), 1)
        self.assertIsNone(self.s.latest(202, "extra"))
        self.assertEqual(self.s.top_metrics(203, 5), ["m(1)"])

    def test_recording_continues_after_rollback(self):
        self.s.record(10, "m", 1)
        self.s.snapshot(11)
        self.s.rollback(100, 11)
        self.assertEqual(self.s.record(101, "m", 5), 2)
        self.assertEqual(self.s.latest(102, "m"), 5)


if __name__ == "__main__":
    unittest.main()
