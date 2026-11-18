import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.r = M.Registry()

    def _ab(self):
        self.r.create(1, "a")
        self.r.create(2, "b")
        self.r.deposit(3, "a", 1000)
        self.r.deposit(4, "b", 500)
        self.r.transfer(5, "a", "b", 200)
        self.r.transfer(6, "b", "a", 100)

    def test_level1_guards(self):
        self.assertIs(self.r.create(1, "a"), True)
        self.assertIs(self.r.create(2, "a"), False)
        self.r.create(3, "b")
        self.r.deposit(4, "a", 10)
        self.assertIsNone(self.r.transfer(5, "a", "a", 1))
        self.assertIsNone(self.r.transfer(6, "a", "ghost", 1))
        self.assertIsNone(self.r.transfer(7, "ghost", "a", 1))
        self.assertIsNone(self.r.transfer(8, "a", "b", 11))
        self.assertEqual(self.r.balance_at(9, "a", 9), 10)
        self.assertEqual(self.r.transfer(10, "a", "b", 10), 0)

    def test_top_spenders_before_merge(self):
        self._ab()
        self.assertEqual(self.r.top_spenders(7, 5), ["a(200)", "b(100)"])

    def test_merge_guards(self):
        self._ab()
        self.assertIs(self.r.merge(7, "a", "a"), False)
        self.assertIs(self.r.merge(8, "a", "ghost"), False)
        self.assertIs(self.r.merge(9, "ghost", "a"), False)
        self.assertIs(self.r.merge(10, "a", "b"), True)

    def test_merge_adds_balance(self):
        self._ab()                       # a=900, b=600
        self.r.merge(8, "a", "b")
        self.assertEqual(self.r.balance_at(9, "a", 9), 1500)

    def test_merge_adds_outgoing_metric(self):
        self._ab()
        self.r.merge(8, "a", "b")
        self.assertEqual(self.r.top_spenders(9, 5), ["a(300)"])

    def test_merge_inherits_history(self):
        self._ab()
        self.r.merge(8, "a", "b")
        self.assertEqual(self.r.balance_at(12, "a", 6), 1500)
        self.assertEqual(self.r.balance_at(12, "a", 5), 1500)   # 800 + 700
        self.assertEqual(self.r.balance_at(12, "a", 4), 1500)   # 1000 + 500
        self.assertEqual(self.r.balance_at(12, "a", 3), 1000)   # 1000 + 0 (b at 2 was 0)
        self.assertEqual(self.r.balance_at(12, "a", 2), 0)
        self.assertEqual(self.r.balance_at(12, "a", 1), 0)

    def test_merge_does_not_backdate_keeper(self):
        self.r.create(1, "b")
        self.r.deposit(2, "b", 500)
        self.r.create(3, "a")
        self.r.deposit(4, "a", 100)
        self.r.merge(5, "a", "b")
        self.assertIsNone(self.r.balance_at(6, "a", 2))
        self.assertEqual(self.r.balance_at(6, "a", 3), 500)   # a exists (0) + b's 500
        self.assertEqual(self.r.balance_at(6, "a", 4), 600)

    def test_dropped_account_is_gone(self):
        self._ab()
        self.r.merge(8, "a", "b")
        self.assertIsNone(self.r.balance_at(9, "b", 4))
        self.assertIsNone(self.r.balance_at(9, "b", 9))
        self.assertIsNone(self.r.deposit(10, "b", 1))
        self.assertIsNone(self.r.transfer(11, "b", "a", 1))
        self.assertEqual(self.r.top_spenders(12, 5), ["a(300)"])

    def test_chained_merges(self):
        for i, name in enumerate(("a", "b", "c"), start=1):
            self.r.create(i, name)
        self.r.deposit(4, "a", 100)
        self.r.deposit(5, "b", 200)
        self.r.deposit(6, "c", 300)
        self.r.transfer(7, "c", "a", 50)     # c out 50 -> c=250, a=150
        self.r.merge(8, "b", "c")            # b = 200 + 250 = 450, out 50
        self.r.merge(9, "a", "b")            # a = 150 + 450 = 600, out 50
        self.assertEqual(self.r.top_spenders(10, 5), ["a(50)"])
        self.assertEqual(self.r.balance_at(11, "a", 11), 600)
        self.assertEqual(self.r.balance_at(11, "a", 6), 600)   # 100 + 200 + 300
        self.assertIsNone(self.r.balance_at(11, "b", 6))
        self.assertIsNone(self.r.balance_at(11, "c", 6))

    def test_activity_after_merge(self):
        self._ab()
        self.r.merge(8, "a", "b")
        self.r.create(9, "z")
        self.assertEqual(self.r.transfer(10, "a", "z", 500), 1000)
        self.assertEqual(self.r.top_spenders(11, 5), ["a(800)", "z(0)"])
        self.assertEqual(self.r.balance_at(12, "a", 9), 1500)
        self.assertEqual(self.r.balance_at(12, "a", 10), 1000)


if __name__ == "__main__":
    unittest.main()
