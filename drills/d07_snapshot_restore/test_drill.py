import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestCache(unittest.TestCase):
    def setUp(self):
        self.c = M.Cache()

    def test_basic_ttl(self):
        self.assertEqual(self.c.set_at("a", "1", 1, 10), "")
        self.assertEqual(self.c.get_at("a", 10), "1")
        self.assertEqual(self.c.get_at("a", 11), "")

    def test_backup_counts_only_alive(self):
        self.c.set_at("a", "1", 1, 5)
        self.c.set_at("b", "2", 2)
        self.assertEqual(self.c.backup(3), 2)
        self.assertEqual(self.c.backup(6), 1)      # "a" expired at 6

    def test_restore_rebases_lifespans(self):
        self.c.set_at("a", "1", 1, 10)             # alive [1, 11)
        self.c.backup(3)                           # a: 8 left
        self.c.set_at("b", "2", 4)                 # forever
        self.c.backup(5)                           # a: 6 left, b: forever
        self.assertEqual(self.c.delete_at("a", 8), "true")
        self.c.backup(9)
        self.assertEqual(self.c.restore(10, 7), "")
        self.assertEqual(self.c.get_at("a", 15), "1")
        self.assertEqual(self.c.get_at("a", 16), "")     # 10 + 6
        self.assertEqual(self.c.get_at("b", 10 ** 9), "2")

    def test_restore_picks_latest_backup_at_or_before(self):
        self.c.set_at("x", "old", 1)
        self.c.backup(2)
        self.c.set_at("x", "new", 3)
        self.c.backup(4)
        self.c.restore(5, 3)
        self.assertEqual(self.c.get_at("x", 6), "old")
        self.c.restore(7, 4)
        self.assertEqual(self.c.get_at("x", 8), "new")

    def test_restore_replaces_state_entirely(self):
        self.c.set_at("a", "1", 1)
        self.c.backup(2)
        self.c.set_at("z", "9", 3)
        self.c.restore(4, 2)
        self.assertEqual(self.c.get_at("z", 5), "")
        self.assertEqual(self.c.get_at("a", 5), "1")

    def test_expired_entries_are_not_resurrected(self):
        self.c.set_at("a", "1", 1, 2)      # dies at 3
        self.c.backup(5)                   # nothing alive
        self.c.set_at("b", "2", 6)
        self.c.restore(7, 5)
        self.assertEqual(self.c.get_at("a", 8), "")
        self.assertEqual(self.c.get_at("b", 8), "")

    def test_double_restore_of_the_same_backup(self):
        self.c.set_at("a", "1", 1, 10)
        self.c.backup(2)                   # a: 9 left
        self.c.restore(20, 2)
        self.assertEqual(self.c.get_at("a", 28), "1")
        self.assertEqual(self.c.get_at("a", 29), "")
        self.c.delete_at("a", 30)
        self.c.restore(40, 2)              # pristine snapshot, still 9 left
        self.assertEqual(self.c.get_at("a", 48), "1")
        self.assertEqual(self.c.get_at("a", 49), "")

    def test_mutating_after_restore_does_not_corrupt_the_backup(self):
        self.c.set_at("a", "1", 1)
        self.c.backup(2)
        self.c.restore(3, 2)
        self.c.set_at("a", "changed", 4)
        self.c.restore(5, 2)
        self.assertEqual(self.c.get_at("a", 6), "1")

    def test_overwrite_resets_ttl_then_backup(self):
        self.c.set_at("a", "1", 1, 3)
        self.c.set_at("a", "2", 2, 100)
        self.assertEqual(self.c.backup(3), 1)
        self.c.restore(200, 3)
        self.assertEqual(self.c.get_at("a", 200 + 98), "2")
        self.assertEqual(self.c.get_at("a", 200 + 99), "")


if __name__ == "__main__":
    unittest.main()
