import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.s = M.CloudStorage()

    def test_add_user(self):
        self.assertIs(self.s.add_user("u1", 200), True)
        self.assertIs(self.s.add_user("u1", 500), False)
        self.assertEqual(self.s.add_file_by("u1", "/x", 200), 0)   # capacity stayed 200

    def test_add_file_by_returns_remaining(self):
        self.s.add_user("u1", 200)
        self.assertEqual(self.s.add_file_by("u1", "/a.txt", 50), 150)
        self.assertEqual(self.s.add_file_by("u1", "/b.txt", 150), 0)

    def test_add_file_by_rejections(self):
        self.s.add_user("u1", 200)
        self.s.add_file_by("u1", "/a.txt", 50)
        self.assertIsNone(self.s.add_file_by("u1", "/a.txt", 1))
        self.assertIsNone(self.s.add_file_by("u1", "/b.txt", 500))
        self.assertIsNone(self.s.add_file_by("ghost", "/c.txt", 1))
        self.assertEqual(self.s.add_file_by("u1", "/b.txt", 150), 0)

    def test_owned_and_unowned_names_share_one_namespace(self):
        self.s.add_user("u1", 200)
        self.s.add_file("/shared", 10)
        self.assertIsNone(self.s.add_file_by("u1", "/shared", 10))
        self.s.add_file_by("u1", "/mine", 10)
        self.assertIs(self.s.add_file("/mine", 10), False)

    def test_level1_files_are_unowned_and_free(self):
        self.s.add_user("u1", 10)
        self.assertIs(self.s.add_file("/huge", 10 ** 9), True)
        self.assertEqual(self.s.add_file_by("u1", "/small", 10), 0)

    def test_delete_refunds_owner(self):
        self.s.add_user("u1", 200)
        self.s.add_file_by("u1", "/a.txt", 50)
        self.assertEqual(self.s.delete_file("/a.txt"), 50)
        self.assertEqual(self.s.add_file_by("u1", "/b.txt", 200), 0)

    def test_delete_of_unowned_file_refunds_nobody(self):
        self.s.add_user("u1", 100)
        self.s.add_file("/free", 50)
        self.assertEqual(self.s.delete_file("/free"), 50)
        self.assertEqual(self.s.add_file_by("u1", "/a", 100), 0)

    def test_copy_charges_the_source_owner(self):
        self.s.add_user("u1", 100)
        self.s.add_file_by("u1", "/a", 40)
        self.assertIs(self.s.copy_file("/a", "/b"), True)
        self.assertEqual(self.s.add_file_by("u1", "/c", 20), 0)
        self.assertIsNone(self.s.add_file_by("u1", "/d", 1))

    def test_copy_fails_when_owner_is_full(self):
        self.s.add_user("u1", 100)
        self.s.add_file_by("u1", "/a", 60)
        self.assertIs(self.s.copy_file("/a", "/b"), False)
        self.assertIsNone(self.s.get_file_size("/b"))
        self.assertEqual(self.s.add_file_by("u1", "/c", 40), 0)

    def test_copy_of_unowned_file_is_free(self):
        self.s.add_user("u1", 1)
        self.s.add_file("/big", 10 ** 6)
        self.assertIs(self.s.copy_file("/big", "/big2"), True)
        self.assertEqual(self.s.add_file_by("u1", "/tiny", 1), 0)

    def test_overwrite_charges_only_the_difference(self):
        self.s.add_user("u1", 100)
        self.s.add_file_by("u1", "/a", 30)
        self.s.add_file_by("u1", "/b", 40)          # used 70, 30 left
        self.assertIs(self.s.copy_file("/a", "/b"), True)   # 30 replaces 40 -> used 60
        self.assertEqual(self.s.get_file_size("/b"), 30)
        self.assertEqual(self.s.add_file_by("u1", "/c", 40), 0)

    def test_overwrite_still_fails_if_the_difference_is_unaffordable(self):
        self.s.add_user("u1", 100)
        self.s.add_file_by("u1", "/a", 60)
        self.s.add_file_by("u1", "/b", 40)          # used 100, 0 left
        self.assertIs(self.s.copy_file("/a", "/b"), False)  # would need 120
        self.assertEqual(self.s.get_file_size("/b"), 40)

    def test_overwrite_refunds_the_other_owner(self):
        self.s.add_user("u1", 100)
        self.s.add_user("u2", 100)
        self.s.add_file_by("u1", "/a", 30)
        self.s.add_file_by("u2", "/b", 90)
        self.assertIs(self.s.copy_file("/a", "/b"), True)
        self.assertEqual(self.s.get_file_size("/b"), 30)
        self.assertEqual(self.s.add_file_by("u2", "/c", 100), 0)   # u2 fully refunded
        self.assertEqual(self.s.add_file_by("u1", "/d", 40), 0)    # u1 charged twice: 60

    def test_merge_user(self):
        self.s.add_user("u1", 200)
        self.s.add_user("u2", 100)
        self.s.add_file_by("u1", "/a", 50)
        self.s.add_file_by("u2", "/d.txt", 80)
        self.assertEqual(self.s.merge_user("u1", "u2"), 170)
        self.assertIsNone(self.s.merge_user("u1", "u2"))
        self.assertEqual(self.s.get_file_size("/d.txt"), 80)
        self.assertEqual(self.s.delete_file("/d.txt"), 80)
        self.assertEqual(self.s.add_file_by("u1", "/e", 250), 0)

    def test_merge_guards(self):
        self.s.add_user("u1", 200)
        self.assertIsNone(self.s.merge_user("u1", "u1"))
        self.assertIsNone(self.s.merge_user("u1", "ghost"))
        self.assertIsNone(self.s.merge_user("ghost", "u1"))

    def test_find_file_covers_owned_and_unowned(self):
        self.s.add_user("u1", 1000)
        self.s.add_file("/free.txt", 10)
        self.s.add_file_by("u1", "/owned.txt", 20)
        self.assertEqual(self.s.find_file("/", ".txt"), ["/owned.txt(20)", "/free.txt(10)"])


if __name__ == "__main__":
    unittest.main()
