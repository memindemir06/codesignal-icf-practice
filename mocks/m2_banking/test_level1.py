import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)
DAY = 86400000


class TestLevel1(unittest.TestCase):
    def setUp(self):
        self.b = M.BankingSystem()

    def test_create_account(self):
        self.assertIs(self.b.create_account(1, "acc1"), True)
        self.assertIs(self.b.create_account(2, "acc1"), False)
        self.assertIs(self.b.create_account(3, "acc2"), True)

    def test_deposit(self):
        self.b.create_account(1, "acc1")
        self.assertIsNone(self.b.deposit(2, "nope", 2700))
        self.assertEqual(self.b.deposit(3, "acc1", 2700), 2700)
        self.assertEqual(self.b.deposit(4, "acc1", 300), 3000)

    def test_deposit_zero(self):
        self.b.create_account(1, "acc1")
        self.assertEqual(self.b.deposit(2, "acc1", 0), 0)

    def test_transfer_returns_source_balance(self):
        self.b.create_account(1, "acc1")
        self.b.create_account(2, "acc2")
        self.b.deposit(3, "acc1", 2700)
        self.assertEqual(self.b.transfer(4, "acc1", "acc2", 200), 2500)
        self.assertEqual(self.b.deposit(5, "acc2", 0), 200)

    def test_transfer_insufficient_funds(self):
        self.b.create_account(1, "acc1")
        self.b.create_account(2, "acc2")
        self.b.deposit(3, "acc1", 2700)
        self.assertIsNone(self.b.transfer(4, "acc1", "acc2", 2701))
        self.assertEqual(self.b.deposit(5, "acc1", 0), 2700)
        self.assertEqual(self.b.deposit(6, "acc2", 0), 0)

    def test_transfer_exact_balance(self):
        self.b.create_account(1, "acc1")
        self.b.create_account(2, "acc2")
        self.b.deposit(3, "acc1", 100)
        self.assertEqual(self.b.transfer(4, "acc1", "acc2", 100), 0)

    def test_transfer_to_self(self):
        self.b.create_account(1, "acc1")
        self.b.deposit(2, "acc1", 100)
        self.assertIsNone(self.b.transfer(3, "acc1", "acc1", 10))
        self.assertEqual(self.b.deposit(4, "acc1", 0), 100)

    def test_transfer_missing_accounts(self):
        self.b.create_account(1, "acc1")
        self.b.deposit(2, "acc1", 100)
        self.assertIsNone(self.b.transfer(3, "acc1", "nope", 10))
        self.assertIsNone(self.b.transfer(4, "nope", "acc1", 10))
        self.assertEqual(self.b.deposit(5, "acc1", 0), 100)


if __name__ == "__main__":
    unittest.main()
