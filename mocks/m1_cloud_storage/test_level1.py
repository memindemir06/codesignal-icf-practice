import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel1(unittest.TestCase):
    def setUp(self):
        self.s = M.CloudStorage()

    def test_add_file(self):
        self.assertIs(self.s.add_file("/dir/file.txt", 100), True)
        self.assertIs(self.s.add_file("/dir/file.txt", 200), False)
        self.assertEqual(self.s.get_file_size("/dir/file.txt"), 100)

    def test_get_missing(self):
        self.assertIsNone(self.s.get_file_size("/nope"))

    def test_zero_size_file(self):
        self.assertIs(self.s.add_file("/empty", 0), True)
        self.assertEqual(self.s.get_file_size("/empty"), 0)

    def test_delete_returns_size(self):
        self.s.add_file("/a", 42)
        self.assertEqual(self.s.delete_file("/a"), 42)
        self.assertIsNone(self.s.delete_file("/a"))
        self.assertIsNone(self.s.get_file_size("/a"))

    def test_copy_missing_source(self):
        self.assertIs(self.s.copy_file("/nope", "/x"), False)
        self.assertIsNone(self.s.get_file_size("/x"))

    def test_copy_creates_independent_file(self):
        self.s.add_file("/a", 100)
        self.assertIs(self.s.copy_file("/a", "/b"), True)
        self.assertEqual(self.s.get_file_size("/b"), 100)
        self.s.delete_file("/a")
        self.assertEqual(self.s.get_file_size("/b"), 100)

    def test_copy_overwrites_destination(self):
        self.s.add_file("/a", 100)
        self.s.add_file("/b", 999)
        self.assertIs(self.s.copy_file("/a", "/b"), True)
        self.assertEqual(self.s.get_file_size("/b"), 100)

    def test_copy_onto_itself(self):
        self.s.add_file("/a", 100)
        self.assertIs(self.s.copy_file("/a", "/a"), True)
        self.assertEqual(self.s.get_file_size("/a"), 100)

    def test_name_after_delete_is_reusable(self):
        self.s.add_file("/a", 1)
        self.s.delete_file("/a")
        self.assertIs(self.s.add_file("/a", 2), True)
        self.assertEqual(self.s.get_file_size("/a"), 2)


if __name__ == "__main__":
    unittest.main()
