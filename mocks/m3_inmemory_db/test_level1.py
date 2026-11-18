import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel1(unittest.TestCase):
    def setUp(self):
        self.db = M.InMemoryDB()

    def test_set_returns_empty_string(self):
        self.assertEqual(self.db.set("A", "B", "E"), "")

    def test_get(self):
        self.db.set("A", "B", "E")
        self.assertEqual(self.db.get("A", "B"), "E")
        self.assertEqual(self.db.get("A", "D"), "")
        self.assertEqual(self.db.get("Z", "B"), "")

    def test_set_overwrites(self):
        self.db.set("A", "B", "E")
        self.db.set("A", "B", "F")
        self.assertEqual(self.db.get("A", "B"), "F")

    def test_multiple_fields_and_records(self):
        self.db.set("A", "B", "E")
        self.db.set("A", "C", "F")
        self.db.set("Z", "B", "G")
        self.assertEqual(self.db.get("A", "B"), "E")
        self.assertEqual(self.db.get("A", "C"), "F")
        self.assertEqual(self.db.get("Z", "B"), "G")

    def test_delete_returns_strings(self):
        self.db.set("A", "B", "E")
        self.assertEqual(self.db.delete("A", "B"), "true")
        self.assertEqual(self.db.delete("A", "B"), "false")
        self.assertEqual(self.db.delete("Z", "B"), "false")
        self.assertEqual(self.db.get("A", "B"), "")

    def test_empty_string_value_is_a_real_value(self):
        self.db.set("A", "B", "")
        self.assertEqual(self.db.delete("A", "B"), "true")


if __name__ == "__main__":
    unittest.main()
