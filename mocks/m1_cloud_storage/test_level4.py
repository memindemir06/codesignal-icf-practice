import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.s = M.CloudStorage()

    def test_backup_counts_owned_files(self):
        self.s.add_user("u1", 100)
        self.s.add_file_by("u1", "/a", 40)
        self.s.add_file_by("u1", "/b", 40)
        self.s.add_file("/unowned", 1)
        self.assertEqual(self.s.backup_user("u1"), 2)
        self.assertIsNone(self.s.backup_user("ghost"))
        self.assertIs(self.s.restore_user("ghost"), False)

    def test_restore_round_trip(self):
        self.s.add_user("u1", 100)
        self.s.add_file_by("u1", "/a", 40)
        self.s.add_file_by("u1", "/b", 40)
        self.assertEqual(self.s.backup_user("u1"), 2)
        self.assertEqual(self.s.delete_file("/a"), 40)
        self.assertEqual(self.s.add_file_by("u1", "/c", 50), 10)
        self.assertIs(self.s.restore_user("u1"), True)
        self.assertEqual(self.s.get_file_size("/a"), 40)
        self.assertEqual(self.s.get_file_size("/b"), 40)
        self.assertIsNone(self.s.get_file_size("/c"))
        self.assertEqual(self.s.add_file_by("u1", "/d", 20), 0)

    def test_restore_without_backup_wipes_the_user(self):
        self.s.add_user("u1", 100)
        self.s.add_file_by("u1", "/a", 40)
        self.assertIs(self.s.restore_user("u1"), True)
        self.assertIsNone(self.s.get_file_size("/a"))
        self.assertEqual(self.s.add_file_by("u1", "/b", 100), 0)

    def test_restore_ignores_capacity_limit(self):
        self.s.add_user("u1", 100)
        self.s.add_file_by("u1", "/a", 100)
        self.s.backup_user("u1")
        self.s.delete_file("/a")
        self.s.add_file_by("u1", "/b", 100)
        self.s.backup_user("u1")            # backup is now {"/b": 100}
        self.s.delete_file("/b")
        self.s.add_file_by("u1", "/a", 100)
        self.assertIs(self.s.restore_user("u1"), True)
        self.assertEqual(self.s.get_file_size("/b"), 100)
        self.assertIsNone(self.s.get_file_size("/a"))

    def test_restore_can_overshoot_capacity_and_block_new_files(self):
        self.s.add_user("u1", 100)
        self.s.add_file_by("u1", "/a", 100)
        self.s.backup_user("u1")
        self.s.delete_file("/a")
        # someone else grabs half the world, then u1 restores over the top
        self.s.add_user("u2", 1000)
        self.s.add_file_by("u2", "/z", 10)
        self.assertIs(self.s.restore_user("u1"), True)
        self.assertEqual(self.s.get_file_size("/a"), 100)
        self.assertIsNone(self.s.add_file_by("u1", "/new", 1))

    def test_restore_skips_names_taken_by_others(self):
        self.s.add_user("u1", 100)
        self.s.add_user("u2", 100)
        self.s.add_file_by("u1", "/a", 10)
        self.s.add_file_by("u1", "/b", 10)
        self.s.backup_user("u1")
        self.s.delete_file("/a")
        self.s.add_file_by("u2", "/a", 5)
        self.assertIs(self.s.restore_user("u1"), True)
        self.assertEqual(self.s.get_file_size("/a"), 5)          # u2's file survives
        self.assertEqual(self.s.get_file_size("/b"), 10)
        self.assertEqual(self.s.add_file_by("u1", "/c", 90), 0)  # u1 only used 10

    def test_restore_skips_names_taken_by_unowned_files(self):
        self.s.add_user("u1", 100)
        self.s.add_file_by("u1", "/a", 10)
        self.s.backup_user("u1")
        self.s.delete_file("/a")
        self.s.add_file("/a", 7)
        self.assertIs(self.s.restore_user("u1"), True)
        self.assertEqual(self.s.get_file_size("/a"), 7)

    def test_new_backup_replaces_the_old_one(self):
        self.s.add_user("u1", 100)
        self.s.add_file_by("u1", "/a", 10)
        self.s.backup_user("u1")
        self.s.delete_file("/a")
        self.s.add_file_by("u1", "/b", 20)
        self.assertEqual(self.s.backup_user("u1"), 1)
        self.s.delete_file("/b")
        self.s.restore_user("u1")
        self.assertIsNone(self.s.get_file_size("/a"))
        self.assertEqual(self.s.get_file_size("/b"), 20)

    def test_merge_discards_the_dropped_users_backup(self):
        self.s.add_user("u1", 100)
        self.s.add_user("u2", 100)
        self.s.add_file_by("u1", "/a", 10)
        self.s.add_file_by("u2", "/b", 10)
        self.s.backup_user("u1")
        self.s.backup_user("u2")
        self.assertEqual(self.s.merge_user("u1", "u2"), 180)
        self.s.delete_file("/b")
        self.assertIs(self.s.restore_user("u1"), True)
        self.assertEqual(self.s.get_file_size("/a"), 10)
        self.assertIsNone(self.s.get_file_size("/b"))   # u1's backup never held /b

    def test_backup_after_merge_covers_transferred_files(self):
        self.s.add_user("u1", 100)
        self.s.add_user("u2", 100)
        self.s.add_file_by("u1", "/a", 10)
        self.s.add_file_by("u2", "/b", 10)
        self.s.merge_user("u1", "u2")
        self.assertEqual(self.s.backup_user("u1"), 2)
        self.s.delete_file("/a")
        self.s.delete_file("/b")
        self.s.restore_user("u1")
        self.assertEqual(self.s.get_file_size("/a"), 10)
        self.assertEqual(self.s.get_file_size("/b"), 10)

    def test_earlier_levels_still_work(self):
        self.s.add_file("/plain", 5)
        self.assertEqual(self.s.get_file_size("/plain"), 5)
        self.assertEqual(self.s.find_file("/pl", ""), ["/plain(5)"])


if __name__ == "__main__":
    unittest.main()
