import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestDrive(unittest.TestCase):
    def setUp(self):
        self.d = M.Drive()

    def test_add_user(self):
        self.assertIs(self.d.add_user("amy", 1000), True)
        self.assertIs(self.d.add_user("amy", 5), False)
        self.d.add_file("amy", "f", 1000)          # capacity was not overwritten with 5
        self.assertEqual(self.d.top_users(1), ["amy(1000)"])

    def test_add_file_returns_remaining(self):
        self.d.add_user("amy", 1000)
        self.assertEqual(self.d.add_file("amy", "a.txt", 600), 400)
        self.assertEqual(self.d.add_file("amy", "b.txt", 400), 0)

    def test_add_file_rejections_change_nothing(self):
        self.d.add_user("amy", 1000)
        self.d.add_file("amy", "a.txt", 600)
        self.assertIsNone(self.d.add_file("amy", "a.txt", 1))     # name taken
        self.assertIsNone(self.d.add_file("amy", "b.txt", 500))   # not enough room
        self.assertIsNone(self.d.add_file("ghost", "c.txt", 1))   # no such user
        self.assertEqual(self.d.top_users(1), ["amy(600)"])
        self.assertEqual(self.d.add_file("amy", "b.txt", 400), 0)

    def test_file_names_are_globally_unique(self):
        self.d.add_user("amy", 100)
        self.d.add_user("bob", 100)
        self.d.add_file("amy", "shared", 10)
        self.assertIsNone(self.d.add_file("bob", "shared", 10))

    def test_exact_fit_is_allowed(self):
        self.d.add_user("amy", 100)
        self.assertEqual(self.d.add_file("amy", "a", 100), 0)
        self.assertIsNone(self.d.add_file("amy", "b", 1))

    def test_delete_refunds_owner(self):
        self.d.add_user("amy", 1000)
        self.d.add_file("amy", "a.txt", 600)
        self.assertEqual(self.d.delete_file("a.txt"), 600)
        self.assertIsNone(self.d.delete_file("a.txt"))
        self.assertEqual(self.d.top_users(1), ["amy(0)"])
        self.assertEqual(self.d.add_file("amy", "big", 1000), 0)

    def test_get_owner(self):
        self.d.add_user("amy", 100)
        self.d.add_file("amy", "a", 1)
        self.assertEqual(self.d.get_owner("a"), "amy")
        self.assertIsNone(self.d.get_owner("nope"))

    def test_top_users(self):
        self.d.add_user("amy", 1000)
        self.d.add_user("bob", 1000)
        self.d.add_user("cal", 1000)
        self.d.add_file("amy", "1", 300)
        self.d.add_file("bob", "2", 300)
        self.assertEqual(self.d.top_users(5), ["amy(300)", "bob(300)", "cal(0)"])
        self.assertEqual(self.d.top_users(2), ["amy(300)", "bob(300)"])

    def test_merge_users(self):
        self.d.add_user("amy", 1000)
        self.d.add_user("bob", 500)
        self.d.add_file("amy", "a", 600)
        self.d.add_file("bob", "c", 300)
        self.d.delete_file("a")
        self.assertEqual(self.d.merge_users("amy", "bob"), 1200)
        self.assertEqual(self.d.get_owner("c"), "amy")
        self.assertEqual(self.d.top_users(5), ["amy(300)"])
        self.assertIsNone(self.d.add_file("bob", "z", 1))

    def test_merge_guards(self):
        self.d.add_user("amy", 100)
        self.assertIsNone(self.d.merge_users("amy", "amy"))
        self.assertIsNone(self.d.merge_users("amy", "ghost"))
        self.assertIsNone(self.d.merge_users("ghost", "amy"))

    def test_capacity_after_merge_is_the_sum(self):
        self.d.add_user("amy", 100)
        self.d.add_user("bob", 100)
        self.d.add_file("amy", "a", 100)
        self.assertIsNone(self.d.add_file("amy", "b", 50))
        self.d.merge_users("amy", "bob")
        self.assertEqual(self.d.add_file("amy", "b", 100), 0)


if __name__ == "__main__":
    unittest.main()
