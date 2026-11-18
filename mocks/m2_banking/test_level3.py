import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)
DAY = 86400000


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.b = M.BankingSystem()
        self.b.create_account(1, "acc1")
        self.b.create_account(2, "acc2")
        self.b.deposit(3, "acc1", 2000)

    def test_pay_ids_and_failures(self):
        self.assertEqual(self.b.pay(4, "acc1", 1000), "payment1")
        self.assertEqual(self.b.pay(100, "acc1", 1000), "payment2")
        self.assertIsNone(self.b.pay(101, "acc1", 1))
        self.assertIsNone(self.b.pay(102, "nope", 1))
        self.b.deposit(103, "acc1", 5)
        self.assertEqual(self.b.pay(104, "acc1", 5), "payment3")

    def test_pay_ids_are_global(self):
        self.b.deposit(4, "acc2", 1000)
        self.assertEqual(self.b.pay(5, "acc1", 10), "payment1")
        self.assertEqual(self.b.pay(6, "acc2", 10), "payment2")
        self.assertEqual(self.b.pay(7, "acc1", 10), "payment3")

    def test_payment_status_guards(self):
        self.b.pay(4, "acc1", 1000)
        self.assertIsNone(self.b.get_payment_status(5, "nope", "payment1"))
        self.assertIsNone(self.b.get_payment_status(6, "acc2", "payment1"))
        self.assertIsNone(self.b.get_payment_status(7, "acc1", "payment99"))
        self.assertEqual(self.b.get_payment_status(8, "acc1", "payment1"), "IN_PROGRESS")

    def test_top_spenders_counts_payments(self):
        self.b.pay(4, "acc1", 1000)
        self.b.pay(5, "acc1", 1000)
        self.assertEqual(self.b.top_spenders(6, 2), ["acc1(2000)", "acc2(0)"])

    def test_cashback_timeline(self):
        self.b.pay(4, "acc1", 1000)
        self.b.pay(100, "acc1", 1000)
        self.assertEqual(self.b.deposit(3 + DAY, "acc1", 100), 100)
        self.assertEqual(self.b.get_payment_status(4 + DAY, "acc1", "payment1"),
                         "CASHBACK_RECEIVED")
        self.assertEqual(self.b.deposit(5 + DAY, "acc1", 100), 220)
        self.assertEqual(self.b.deposit(99 + DAY, "acc1", 100), 320)
        self.assertEqual(self.b.get_payment_status(99 + DAY, "acc1", "payment2"),
                         "IN_PROGRESS")
        self.assertEqual(self.b.deposit(100 + DAY, "acc1", 100), 440)

    def test_cashback_rounds_down(self):
        self.b.pay(4, "acc1", 49)      # 0.98 -> 0
        self.b.pay(5, "acc1", 50)      # 1.0  -> 1
        self.b.pay(6, "acc1", 149)     # 2.98 -> 2
        self.assertEqual(self.b.deposit(7, "acc1", 0), 2000 - 49 - 50 - 149)
        self.assertEqual(self.b.deposit(6 + DAY, "acc1", 0), 1752 + 0 + 1 + 2)

    def test_cashback_does_not_count_as_outgoing(self):
        self.b.pay(4, "acc1", 1000)
        self.assertEqual(self.b.top_spenders(4 + DAY, 2), ["acc1(1000)", "acc2(0)"])

    def test_cashback_can_fund_a_later_payment(self):
        self.assertEqual(self.b.pay(4, "acc1", 2000), "payment1")
        self.assertIsNone(self.b.pay(5, "acc1", 40))
        self.assertEqual(self.b.pay(4 + DAY, "acc1", 40), "payment2")
        self.assertEqual(self.b.deposit(5 + DAY, "acc1", 0), 0)

    def test_transfer_after_cashback_lands(self):
        self.b.pay(4, "acc1", 2000)
        self.assertIsNone(self.b.transfer(5, "acc1", "acc2", 40))
        self.assertEqual(self.b.transfer(4 + DAY, "acc1", "acc2", 40), 0)
        self.assertEqual(self.b.top_spenders(5 + DAY, 2), ["acc1(2040)", "acc2(0)"])

    def test_many_pending_cashbacks_settle_in_order(self):
        for i in range(5):
            self.b.pay(10 + i, "acc1", 100)
        self.assertEqual(self.b.deposit(20, "acc1", 0), 1500)
        self.assertEqual(self.b.deposit(12 + DAY, "acc1", 0), 1500 + 3 * 2)
        self.assertEqual(self.b.deposit(20 + DAY, "acc1", 0), 1500 + 5 * 2)


if __name__ == "__main__":
    unittest.main()
