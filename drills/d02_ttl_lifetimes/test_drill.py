import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestStore(unittest.TestCase):
    def setUp(self):
        self.s = M.Store()

    def test_set_returns_empty_string(self):
        self.assertEqual(self.s.set_at("a", "1", 1), "")
        self.assertEqual(self.s.set_at_with_ttl("b", "2", 1, 5), "")

    def test_no_ttl_lives_forever(self):
        self.s.set_at("a", "1", 1)
        self.assertEqual(self.s.get_at("a", 10 ** 9), "1")

    def test_half_open_interval(self):
        self.s.set_at_with_ttl("a", "1", 1, 9)
        self.assertEqual(self.s.get_at("a", 1), "1")
        self.assertEqual(self.s.get_at("a", 9), "1")
        self.assertEqual(self.s.get_at("a", 10), "")   # dead AT expiry

    def test_overwrite_resets_lifetime(self):
        self.s.set_at_with_ttl("a", "1", 1, 9)
        self.s.set_at_with_ttl("a", "2", 5, 10)
        self.assertEqual(self.s.get_at("a", 14), "2")
        self.assertEqual(self.s.get_at("a", 15), "")

    def test_overwrite_ttl_with_no_ttl(self):
        self.s.set_at_with_ttl("a", "1", 1, 3)
        self.s.set_at("a", "2", 2)
        self.assertEqual(self.s.get_at("a", 10 ** 6), "2")

    def test_missing_key(self):
        self.assertEqual(self.s.get_at("nope", 1), "")

    def test_delete_returns_strings(self):
        self.s.set_at("a", "1", 1)
        self.assertEqual(self.s.delete_at("a", 2), "true")
        self.assertEqual(self.s.delete_at("a", 3), "false")
        self.assertEqual(self.s.delete_at("never", 4), "false")

    def test_delete_expired_is_false(self):
        self.s.set_at_with_ttl("a", "1", 1, 5)
        self.assertEqual(self.s.delete_at("a", 6), "false")
        self.assertEqual(self.s.get_at("a", 7), "")

    def test_count_and_keys(self):
        self.s.set_at_with_ttl("b", "1", 1, 5)
        self.s.set_at_with_ttl("a", "2", 1, 50)
        self.s.set_at("c", "3", 2)
        self.assertEqual(self.s.count_at(3), 3)
        self.assertEqual(self.s.keys_at(3), ["a", "b", "c"])
        self.assertEqual(self.s.count_at(6), 2)
        self.assertEqual(self.s.keys_at(6), ["a", "c"])
        self.assertEqual(self.s.keys_at(51), ["c"])

    def test_expiry_is_lazy_not_destructive(self):
        # asking at a late time must not wipe entries that a later query still needs
        self.s.set_at_with_ttl("a", "1", 1, 100)
        self.assertEqual(self.s.get_at("a", 50), "1")
        self.assertEqual(self.s.count_at(60), 1)
        self.assertEqual(self.s.get_at("a", 99), "1")


if __name__ == "__main__":
    unittest.main()
