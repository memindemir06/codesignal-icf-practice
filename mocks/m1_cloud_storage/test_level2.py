import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel2(unittest.TestCase):
    def setUp(self):
        self.s = M.CloudStorage()
        self.s.add_file("/dir/file.txt", 100)
        self.s.add_file("/dir/file.med", 200)
        self.s.add_file("/dir/deep/file.txt", 300)
        self.s.add_file("/other/file.txt", 300)

    def test_prefix_and_suffix(self):
        self.assertEqual(self.s.find_file("/dir", ".txt"),
                         ["/dir/deep/file.txt(300)", "/dir/file.txt(100)"])

    def test_tie_broken_by_name_ascending(self):
        self.assertEqual(self.s.find_file("/", ".txt"),
                         ["/dir/deep/file.txt(300)", "/other/file.txt(300)",
                          "/dir/file.txt(100)"])

    def test_empty_prefix_and_suffix_match_everything(self):
        self.assertEqual(self.s.find_file("", ""),
                         ["/dir/deep/file.txt(300)", "/other/file.txt(300)",
                          "/dir/file.med(200)", "/dir/file.txt(100)"])

    def test_no_match(self):
        self.assertEqual(self.s.find_file("/zzz", ""), [])
        self.assertEqual(self.s.find_file("", ".zip"), [])

    def test_prefix_and_suffix_must_both_hold(self):
        self.assertEqual(self.s.find_file("/other", ".med"), [])

    def test_empty_storage(self):
        self.assertEqual(M.CloudStorage().find_file("", ""), [])

    def test_capped_at_ten(self):
        s = M.CloudStorage()
        for i in range(15):
            s.add_file("/f%02d.txt" % i, i)
        out = s.find_file("/f", ".txt")
        self.assertEqual(len(out), 10)
        self.assertEqual(out[0], "/f14.txt(14)")
        self.assertEqual(out[-1], "/f05.txt(5)")

    def test_reflects_deletions(self):
        self.s.delete_file("/dir/deep/file.txt")
        self.assertEqual(self.s.find_file("/dir", ".txt"), ["/dir/file.txt(100)"])


if __name__ == "__main__":
    unittest.main()
