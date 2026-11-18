import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)
DAY = 86400000


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.b = M.BankingSystem()

    # ---------- get_balance ----------
    def test_balance_history_basics(self):
        self.b.create_account(1, "a")
        self.b.deposit(3, "a", 100)
        self.b.deposit(7, "a", 50)
        self.assertIsNone(self.b.get_balance(9, "a", 0))
        self.assertEqual(self.b.get_balance(9, "a", 1), 0)
        self.assertEqual(self.b.get_balance(9, "a", 2), 0)
        self.assertEqual(self.b.get_balance(9, "a", 3), 100)
        self.assertEqual(self.b.get_balance(9, "a", 6), 100)
        self.assertEqual(self.b.get_balance(9, "a", 7), 150)
        self.assertEqual(self.b.get_balance(9, "a", 9), 150)
        self.assertIsNone(self.b.get_balance(9, "ghost", 5))

    def test_failed_operations_leave_history_untouched(self):
        self.b.create_account(1, "a")
        self.b.deposit(2, "a", 10)
        self.assertIsNone(self.b.pay(3, "a", 999))
        self.assertEqual(self.b.get_balance(4, "a", 3), 10)

    def test_history_includes_cashback_at_its_due_time(self):
        self.b.create_account(1, "a")
        self.b.deposit(2, "a", 1000)
        self.assertEqual(self.b.pay(3, "a", 300), "payment1")
        self.assertEqual(self.b.get_balance(4, "a", 3), 700)
        self.assertEqual(self.b.get_balance(5 + DAY, "a", 2 + DAY), 700)
        self.assertEqual(self.b.get_balance(6 + DAY, "a", 3 + DAY), 706)

    # ---------- merge_accounts ----------
    def test_merge_guards(self):
        self.b.create_account(1, "acc1")
        self.b.create_account(2, "acc2")
        self.assertIs(self.b.merge_accounts(3, "acc1", "nope"), False)
        self.assertIs(self.b.merge_accounts(4, "nope", "acc1"), False)
        self.assertIs(self.b.merge_accounts(5, "acc1", "acc1"), False)
        self.assertIs(self.b.merge_accounts(6, "acc1", "acc2"), True)
        self.assertIs(self.b.merge_accounts(7, "acc1", "acc2"), False)

    def test_spec_walkthrough(self):
        self.b.create_account(1, "acc1")
        self.b.create_account(2, "acc2")
        self.assertEqual(self.b.deposit(3, "acc1", 2000), 2000)
        self.assertEqual(self.b.deposit(4, "acc2", 3000), 3000)
        self.assertEqual(self.b.pay(5, "acc1", 500), "payment1")
        self.assertEqual(self.b.transfer(6, "acc1", "acc2", 500), 1000)
        self.assertIs(self.b.merge_accounts(9, "acc1", "acc2"), True)
        self.assertEqual(self.b.get_balance(10, "acc1", 10), 4500)
        self.assertIsNone(self.b.get_balance(11, "acc2", 10))
        self.assertIsNone(self.b.get_balance(12, "acc2", 4))
        self.assertEqual(self.b.get_payment_status(13, "acc1", "payment1"), "IN_PROGRESS")
        self.assertEqual(self.b.get_balance(14, "acc1", 3), 2000)
        self.assertEqual(self.b.get_balance(15, "acc1", 4), 5000)
        self.assertEqual(self.b.top_spenders(16, 5), ["acc1(1000)"])
        self.assertEqual(self.b.deposit(5 + DAY, "acc1", 100), 4610)

    def test_merged_account_is_dead(self):
        self.b.create_account(1, "a")
        self.b.create_account(2, "b")
        self.b.deposit(3, "a", 100)
        self.b.deposit(4, "b", 100)
        self.b.merge_accounts(5, "a", "b")
        self.assertIsNone(self.b.deposit(6, "b", 10))
        self.assertIsNone(self.b.transfer(7, "b", "a", 10))
        self.assertIsNone(self.b.transfer(8, "a", "b", 10))
        self.assertIsNone(self.b.pay(9, "b", 10))
        self.assertEqual(self.b.top_spenders(10, 5), ["a(0)"])

    def test_merge_sums_outgoing(self):
        self.b.create_account(1, "a")
        self.b.create_account(2, "b")
        self.b.create_account(3, "sink")
        self.b.deposit(4, "a", 1000)
        self.b.deposit(5, "b", 1000)
        self.b.transfer(6, "a", "sink", 100)
        self.b.pay(7, "b", 250)
        self.b.merge_accounts(8, "a", "b")
        self.assertEqual(self.b.top_spenders(9, 5), ["a(350)", "sink(0)"])

    def test_merge_retargets_pending_cashback(self):
        self.b.create_account(1, "a")
        self.b.create_account(2, "b")
        self.b.deposit(3, "a", 1000)
        self.b.deposit(4, "b", 1000)
        self.assertEqual(self.b.pay(5, "b", 500), "payment1")
        self.assertIs(self.b.merge_accounts(6, "a", "b"), True)
        self.assertEqual(self.b.get_balance(7, "a", 7), 1500)
        self.assertEqual(self.b.deposit(5 + DAY, "a", 0), 1510)

    def test_merge_moves_payment_ids(self):
        self.b.create_account(1, "a")
        self.b.create_account(2, "b")
        self.b.deposit(3, "b", 1000)
        self.b.pay(4, "b", 500)
        self.b.merge_accounts(5, "a", "b")
        self.assertEqual(self.b.get_payment_status(6, "a", "payment1"), "IN_PROGRESS")
        self.assertIsNone(self.b.get_payment_status(7, "b", "payment1"))
        self.assertEqual(self.b.get_payment_status(4 + DAY, "a", "payment1"),
                         "CASHBACK_RECEIVED")

    def test_merge_does_not_backdate_the_keeper(self):
        self.b.create_account(1, "b")
        self.b.deposit(2, "b", 500)
        self.b.create_account(3, "a")
        self.b.deposit(4, "a", 100)
        self.b.merge_accounts(5, "a", "b")
        self.assertIsNone(self.b.get_balance(6, "a", 2))
        self.assertEqual(self.b.get_balance(6, "a", 3), 500)
        self.assertEqual(self.b.get_balance(6, "a", 4), 600)

    def test_chained_merges(self):
        for i, name in enumerate(["a", "b", "c"], start=1):
            self.b.create_account(i, name)
        self.b.deposit(4, "a", 100)
        self.b.deposit(5, "b", 200)
        self.b.deposit(6, "c", 300)
        self.assertEqual(self.b.pay(7, "c", 100), "payment1")
        self.assertIs(self.b.merge_accounts(8, "b", "c"), True)
        self.assertIs(self.b.merge_accounts(9, "a", "b"), True)
        self.assertEqual(self.b.top_spenders(10, 5), ["a(100)"])
        self.assertEqual(self.b.get_balance(11, "a", 11), 500)
        self.assertEqual(self.b.get_balance(11, "a", 6), 600)
        self.assertEqual(self.b.get_payment_status(12, "a", "payment1"), "IN_PROGRESS")
        self.assertEqual(self.b.deposit(7 + DAY, "a", 0), 502)

    def test_activity_after_merge(self):
        self.b.create_account(1, "a")
        self.b.create_account(2, "b")
        self.b.create_account(3, "z")
        self.b.deposit(4, "a", 100)
        self.b.deposit(5, "b", 100)
        self.b.merge_accounts(6, "a", "b")
        self.assertEqual(self.b.transfer(7, "a", "z", 50), 150)
        self.assertEqual(self.b.get_balance(8, "a", 6), 200)
        self.assertEqual(self.b.get_balance(8, "a", 7), 150)
        self.assertEqual(self.b.top_spenders(9, 5), ["a(50)", "z(0)"])


if __name__ == "__main__":
    unittest.main()
