import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestCatalog(unittest.TestCase):
    def setUp(self):
        self.c = M.Catalog()

    def test_add_duplicate(self):
        self.assertIs(self.c.add_file("a.txt", 10), True)
        self.assertIs(self.c.add_file("a.txt", 99), False)
        self.assertEqual(self.c.search_files("a"), ["a.txt(10)"])

    def test_search_order_and_tiebreak(self):
        self.c.add_file("report.pdf", 300)
        self.c.add_file("report.txt", 300)
        self.c.add_file("readme.md", 900)
        self.assertEqual(self.c.search_files("re"),
                         ["readme.md(900)", "report.pdf(300)", "report.txt(300)"])

    def test_search_no_match(self):
        self.c.add_file("a", 1)
        self.assertEqual(self.c.search_files("zzz"), [])

    def test_empty_prefix_matches_all(self):
        self.c.add_file("b", 1)
        self.c.add_file("a", 2)
        self.assertEqual(self.c.search_files(""), ["a(2)", "b(1)"])

    def test_search_caps_at_ten(self):
        for i in range(15):
            self.c.add_file("f%02d" % i, i)
        out = self.c.search_files("f")
        self.assertEqual(len(out), 10)
        self.assertEqual(out[0], "f14(14)")
        self.assertEqual(out[-1], "f05(5)")

    def test_prefix_is_not_substring(self):
        self.c.add_file("xreport", 5)
        self.c.add_file("report", 5)
        self.assertEqual(self.c.search_files("re"), ["report(5)"])

    def test_set_tag_returns_empty_and_ignores_missing_file(self):
        self.assertEqual(self.c.set_tag("ghost", "a", "b"), "")
        self.assertEqual(self.c.scan_tags("ghost", ""), "")

    def test_scan_tags_format_and_order(self):
        self.c.add_file("readme.md", 900)
        self.c.set_tag("readme.md", "owner", "amy")
        self.c.set_tag("readme.md", "org", "acme")
        self.c.set_tag("readme.md", "lang", "en")
        self.assertEqual(self.c.scan_tags("readme.md", "o"), "org(acme), owner(amy)")
        self.assertEqual(self.c.scan_tags("readme.md", ""),
                         "lang(en), org(acme), owner(amy)")
        self.assertEqual(self.c.scan_tags("readme.md", "z"), "")

    def test_set_tag_overwrites(self):
        self.c.add_file("a", 1)
        self.c.set_tag("a", "k", "v1")
        self.c.set_tag("a", "k", "v2")
        self.assertEqual(self.c.scan_tags("a", "k"), "k(v2)")


if __name__ == "__main__":
    unittest.main()
