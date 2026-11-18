import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel1(unittest.TestCase):
    def setUp(self):
        self.s = M.MetricsService()

    def test_record_returns_running_count(self):
        self.assertEqual(self.s.record(1, "cpu", 40), 1)
        self.assertEqual(self.s.record(2, "cpu", 55), 2)
        self.assertEqual(self.s.record(3, "mem", 10), 1)

    def test_latest(self):
        self.s.record(1, "cpu", 40)
        self.s.record(2, "cpu", 55)
        self.assertEqual(self.s.latest(3, "cpu"), 55)
        self.assertIsNone(self.s.latest(4, "disk"))

    def test_negative_and_zero_values(self):
        self.s.record(1, "delta", -5)
        self.assertEqual(self.s.latest(2, "delta"), -5)
        self.s.record(3, "delta", 0)
        self.assertEqual(self.s.latest(4, "delta"), 0)

    def test_remove(self):
        self.s.record(1, "cpu", 40)
        self.assertIs(self.s.remove(2, "cpu"), True)
        self.assertIs(self.s.remove(3, "cpu"), False)
        self.assertIsNone(self.s.latest(4, "cpu"))

    def test_recording_after_remove_starts_fresh(self):
        self.s.record(1, "cpu", 40)
        self.s.record(2, "cpu", 41)
        self.s.remove(3, "cpu")
        self.assertEqual(self.s.record(4, "cpu", 1), 1)
        self.assertEqual(self.s.latest(5, "cpu"), 1)

    def test_metrics_are_independent(self):
        self.s.record(1, "a", 1)
        self.s.record(2, "b", 2)
        self.s.remove(3, "a")
        self.assertEqual(self.s.latest(4, "b"), 2)


if __name__ == "__main__":
    unittest.main()
