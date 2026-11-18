import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.db = M.InMemoryDB()

    def test_backup_returns_a_string_count(self):
        self.db.set_at("A", "B", "C", 1)
        self.db.set_at("Z", "B", "C", 2)
        self.assertEqual(self.db.backup(3), "2")

    def test_backup_ignores_expired_and_empty_records(self):
        self.db.set_at_with_ttl("A", "B", "C", 1, 2)     # dead at 3
        self.db.set_at("Z", "B", "C", 2)
        self.assertEqual(self.db.backup(5), "1")

    def test_spec_walkthrough(self):
        self.db.set_at_with_ttl("A", "B", "C", 1, 10)
        self.assertEqual(self.db.backup(3), "1")
        self.db.set_at("A", "D", "E", 4)
        self.assertEqual(self.db.backup(5), "1")
        self.assertEqual(self.db.delete_at("A", "B", 8), "true")
        self.assertEqual(self.db.backup(9), "1")
        self.assertEqual(self.db.restore(10, 7), "")
        self.assertEqual(self.db.scan_at("A", 15), "B(C), D(E)")
        self.assertEqual(self.db.scan_at("A", 16), "D(E)")
        self.db.set_at("B", "C", "D", 17)
        self.assertEqual(self.db.backup(18), "2")

    def test_restore_picks_latest_at_or_before(self):
        self.db.set_at("A", "B", "old", 1)
        self.db.backup(2)
        self.db.set_at("A", "B", "new", 3)
        self.db.backup(4)
        self.db.restore(5, 3)
        self.assertEqual(self.db.get_at("A", "B", 6), "old")
        self.db.restore(7, 4)
        self.assertEqual(self.db.get_at("A", "B", 8), "new")

    def test_restore_replaces_everything(self):
        self.db.set_at("A", "B", "1", 1)
        self.db.backup(2)
        self.db.set_at("Z", "Y", "9", 3)
        self.db.restore(4, 2)
        self.assertEqual(self.db.get_at("Z", "Y", 5), "")
        self.assertEqual(self.db.scan_at("A", 5), "B(1)")

    def test_no_expiry_survives_restore(self):
        self.db.set_at("A", "B", "1", 1)
        self.db.backup(2)
        self.db.restore(3, 2)
        self.assertEqual(self.db.get_at("A", "B", 10 ** 9), "1")

    def test_double_restore_of_the_same_backup(self):
        self.db.set_at_with_ttl("A", "B", "C", 1, 10)
        self.db.backup(2)                    # 9 ticks left
        self.db.restore(20, 2)
        self.assertEqual(self.db.get_at("A", "B", 28), "C")
        self.assertEqual(self.db.get_at("A", "B", 29), "")
        self.db.delete_at("A", "B", 30)
        self.db.restore(40, 2)
        self.assertEqual(self.db.get_at("A", "B", 48), "C")
        self.assertEqual(self.db.get_at("A", "B", 49), "")

    def test_mutating_after_restore_does_not_corrupt_the_snapshot(self):
        self.db.set_at("A", "B", "1", 1)
        self.db.backup(2)
        self.db.restore(3, 2)
        self.db.set_at("A", "B", "changed", 4)
        self.db.set_at("A", "C", "extra", 5)
        self.db.restore(6, 2)
        self.assertEqual(self.db.scan_at("A", 7), "B(1)")

    def test_partial_record_backup(self):
        self.db.set_at_with_ttl("A", "a", "1", 1, 3)     # dead at 4
        self.db.set_at("A", "b", "2", 1)
        self.assertEqual(self.db.backup(5), "1")
        self.db.restore(6, 5)
        self.assertEqual(self.db.scan_at("A", 7), "b(2)")


if __name__ == "__main__":
    unittest.main()
