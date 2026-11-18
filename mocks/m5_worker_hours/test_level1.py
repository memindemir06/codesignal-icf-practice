import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel1(unittest.TestCase):
    def setUp(self):
        self.r = M.WorkRegister()

    def test_add_worker_returns_strings(self):
        self.assertEqual(self.r.add_worker("Ashley", "Middle Developer", 150), "true")
        self.assertEqual(self.r.add_worker("Ashley", "Junior Developer", 100), "false")

    def test_duplicate_add_does_not_reset_the_worker(self):
        self.r.add_worker("Ashley", "Middle Developer", 150)
        self.r.register("Ashley", 10)
        self.r.register("Ashley", 20)
        self.assertEqual(self.r.add_worker("Ashley", "Junior Developer", 100), "false")
        self.assertEqual(self.r.get("Ashley"), "10")

    def test_register_toggles(self):
        self.r.add_worker("Ashley", "Dev", 150)
        self.assertEqual(self.r.register("Ashley", 10), "registered")
        self.assertEqual(self.r.register("Ashley", 25), "registered")
        self.assertEqual(self.r.get("Ashley"), "15")

    def test_open_session_is_not_counted(self):
        self.r.add_worker("Ashley", "Dev", 150)
        self.r.register("Ashley", 10)
        self.assertEqual(self.r.get("Ashley"), "0")
        self.r.register("Ashley", 25)
        self.r.register("Ashley", 40)
        self.assertEqual(self.r.get("Ashley"), "15")
        self.r.register("Ashley", 67)
        self.assertEqual(self.r.get("Ashley"), "42")

    def test_unknown_worker(self):
        self.assertEqual(self.r.get("Walter"), "")
        self.assertEqual(self.r.register("Walter", 120), "invalid_request")

    def test_returns_are_strings_not_ints(self):
        self.r.add_worker("A", "Dev", 1)
        self.r.register("A", 1)
        self.r.register("A", 4)
        self.assertIsInstance(self.r.get("A"), str)
        self.assertEqual(self.r.get("A"), "3")

    def test_interleaved_workers(self):
        self.r.add_worker("A", "Dev", 1)
        self.r.add_worker("B", "Dev", 1)
        self.r.register("A", 1)
        self.r.register("B", 2)
        self.r.register("A", 5)
        self.r.register("B", 9)
        self.assertEqual(self.r.get("A"), "4")
        self.assertEqual(self.r.get("B"), "7")

    def test_zero_length_session(self):
        self.r.add_worker("A", "Dev", 1)
        self.r.register("A", 10)
        self.r.register("A", 10)
        self.assertEqual(self.r.get("A"), "0")


if __name__ == "__main__":
    unittest.main()
