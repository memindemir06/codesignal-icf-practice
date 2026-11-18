import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.db = M.InMemoryDB()

    def test_set_at_has_no_expiry(self):
        self.assertEqual(self.db.set_at("A", "B", "C", 1), "")
        self.assertEqual(self.db.get_at("A", "B", 10 ** 9), "C")

    def test_ttl_half_open(self):
        self.db.set_at_with_ttl("A", "BC", "E", 1, 9)
        self.assertEqual(self.db.get_at("A", "BC", 1), "E")
        self.assertEqual(self.db.get_at("A", "BC", 9), "E")
        self.assertEqual(self.db.get_at("A", "BC", 10), "")

    def test_overwrite_restarts_lifetime(self):
        self.db.set_at_with_ttl("A", "BC", "E", 1, 9)
        self.db.set_at_with_ttl("A", "BC", "E", 5, 10)
        self.db.set_at("A", "BD", "F", 6)
        self.assertEqual(self.db.scan_by_prefix_at("A", "B", 14), "BC(E), BD(F)")
        self.assertEqual(self.db.scan_by_prefix_at("A", "B", 15), "BD(F)")

    def test_ttl_replaced_by_no_ttl(self):
        self.db.set_at_with_ttl("A", "B", "1", 1, 3)
        self.db.set_at("A", "B", "2", 2)
        self.assertEqual(self.db.get_at("A", "B", 10 ** 9), "2")

    def test_delete_at(self):
        self.db.set_at_with_ttl("A", "B", "C", 1, 10)
        self.assertEqual(self.db.delete_at("A", "B", 5), "true")
        self.assertEqual(self.db.delete_at("A", "B", 6), "false")
        self.assertEqual(self.db.get_at("A", "B", 7), "")

    def test_delete_at_after_expiry_is_false(self):
        self.db.set_at_with_ttl("A", "B", "C", 1, 3)
        self.assertEqual(self.db.delete_at("A", "B", 4), "false")
        self.assertEqual(self.db.delete_at("Z", "B", 5), "false")

    def test_scan_at_filters_expired(self):
        self.db.set_at_with_ttl("A", "a", "1", 1, 5)
        self.db.set_at("A", "b", "2", 1)
        self.db.set_at_with_ttl("A", "c", "3", 1, 100)
        self.assertEqual(self.db.scan_at("A", 3), "a(1), b(2), c(3)")
        self.assertEqual(self.db.scan_at("A", 6), "b(2), c(3)")
        self.assertEqual(self.db.scan_at("A", 101), "b(2)")
        self.assertEqual(self.db.scan_at("Z", 1), "")

    def test_record_with_all_fields_expired_scans_empty(self):
        self.db.set_at_with_ttl("A", "a", "1", 1, 2)
        self.assertEqual(self.db.scan_at("A", 5), "")
        self.assertEqual(self.db.scan_by_prefix_at("A", "a", 5), "")

    def test_backward_compatibility_untimed_methods_unchanged(self):
        self.db.set("A", "B", "E")
        self.db.set("A", "C", "F")
        self.assertEqual(self.db.get("A", "B"), "E")
        self.assertEqual(self.db.scan("A"), "B(E), C(F)")
        self.assertEqual(self.db.scan_by_prefix("A", "B"), "B(E)")
        self.assertEqual(self.db.delete("A", "B"), "true")
        self.assertEqual(self.db.delete("A", "B"), "false")
        self.assertEqual(self.db.scan("A"), "C(F)")


if __name__ == "__main__":
    unittest.main()
