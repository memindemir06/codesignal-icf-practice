import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel1(unittest.TestCase):
    def setUp(self):
        self.p = M.FXPlatform()

    def test_create_client(self):
        self.assertIs(self.p.create_client(1, "acme"), True)
        self.assertIs(self.p.create_client(2, "acme"), False)

    def test_deposit(self):
        self.p.create_client(1, "acme")
        self.assertIsNone(self.p.deposit(2, "ghost", "GBP", 100))
        self.assertEqual(self.p.deposit(3, "acme", "GBP", 100000), 100000)
        self.assertEqual(self.p.deposit(4, "acme", "GBP", 500), 100500)
        self.assertEqual(self.p.deposit(5, "acme", "EUR", 5000), 5000)

    def test_currencies_are_independent(self):
        self.p.create_client(1, "acme")
        self.p.deposit(2, "acme", "GBP", 100)
        self.assertEqual(self.p.get_balance(3, "acme", "EUR"), 0)
        self.assertEqual(self.p.get_balance(4, "acme", "GBP"), 100)

    def test_clients_are_independent(self):
        self.p.create_client(1, "a")
        self.p.create_client(2, "b")
        self.p.deposit(3, "a", "GBP", 100)
        self.assertEqual(self.p.get_balance(4, "b", "GBP"), 0)

    def test_get_balance_unknown_client(self):
        self.assertIsNone(self.p.get_balance(1, "ghost", "GBP"))

    def test_withdraw(self):
        self.p.create_client(1, "acme")
        self.p.deposit(2, "acme", "GBP", 100000)
        self.assertIsNone(self.p.withdraw(3, "acme", "GBP", 100001))
        self.assertIsNone(self.p.withdraw(4, "acme", "USD", 1))
        self.assertIsNone(self.p.withdraw(5, "ghost", "GBP", 1))
        self.assertEqual(self.p.withdraw(6, "acme", "GBP", 40000), 60000)
        self.assertEqual(self.p.get_balance(7, "acme", "GBP"), 60000)

    def test_withdraw_exact_balance(self):
        self.p.create_client(1, "acme")
        self.p.deposit(2, "acme", "GBP", 100)
        self.assertEqual(self.p.withdraw(3, "acme", "GBP", 100), 0)
        self.assertIsNone(self.p.withdraw(4, "acme", "GBP", 1))

    def test_zero_amounts(self):
        self.p.create_client(1, "acme")
        self.assertEqual(self.p.deposit(2, "acme", "GBP", 0), 0)
        self.assertEqual(self.p.withdraw(3, "acme", "GBP", 0), 0)


if __name__ == "__main__":
    unittest.main()
