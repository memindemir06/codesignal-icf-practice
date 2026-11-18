import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel2(unittest.TestCase):
    def setUp(self):
        self.db = M.InMemoryDB()
        self.db.set("A", "BC", "E")
        self.db.set("A", "BD", "F")
        self.db.set("A", "C", "G")

    def test_scan_is_sorted(self):
        self.assertEqual(self.db.scan("A"), "BC(E), BD(F), C(G)")

    def test_scan_by_prefix(self):
        self.assertEqual(self.db.scan_by_prefix("A", "B"), "BC(E), BD(F)")
        self.assertEqual(self.db.scan_by_prefix("A", "BC"), "BC(E)")
        self.assertEqual(self.db.scan_by_prefix("A", "Z"), "")

    def test_empty_prefix_matches_all(self):
        self.assertEqual(self.db.scan_by_prefix("A", ""), "BC(E), BD(F), C(G)")

    def test_missing_record(self):
        self.assertEqual(self.db.scan("Z"), "")
        self.assertEqual(self.db.scan_by_prefix("Z", "B"), "")

    def test_record_emptied_by_deletes(self):
        for f in ("BC", "BD", "C"):
            self.db.delete("A", f)
        self.assertEqual(self.db.scan("A"), "")

    def test_insertion_order_does_not_leak(self):
        db = M.InMemoryDB()
        for f in ("z", "a", "m"):
            db.set("K", f, f.upper())
        self.assertEqual(db.scan("K"), "a(A), m(M), z(Z)")


if __name__ == "__main__":
    unittest.main()
