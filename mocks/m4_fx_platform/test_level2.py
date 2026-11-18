import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel2(unittest.TestCase):
    def setUp(self):
        self.p = M.FXPlatform()
        self.p.create_client(1, "beta")
        self.p.create_client(2, "acme")
        self.p.deposit(3, "acme", "GBP", 1000)
        self.p.deposit(4, "beta", "GBP", 1000)
        self.p.deposit(5, "beta", "EUR", 1000)

    def test_zero_activity_is_alphabetical(self):
        self.assertEqual(self.p.top_spenders(6, "GBP", 5), ["acme(0)", "beta(0)"])

    def test_per_currency_totals(self):
        self.assertEqual(self.p.withdraw(7, "acme", "GBP", 300), 700)
        self.assertEqual(self.p.withdraw(8, "beta", "EUR", 900), 100)
        self.assertEqual(self.p.top_spenders(9, "GBP", 5), ["acme(300)", "beta(0)"])
        self.assertEqual(self.p.top_spenders(10, "EUR", 5), ["beta(900)", "acme(0)"])

    def test_unheld_currency_still_lists_everyone(self):
        self.assertEqual(self.p.top_spenders(6, "USD", 5), ["acme(0)", "beta(0)"])

    def test_n_smaller_than_client_count(self):
        self.p.withdraw(7, "acme", "GBP", 300)
        self.assertEqual(self.p.top_spenders(8, "GBP", 1), ["acme(300)"])

    def test_fewer_clients_than_n(self):
        self.assertEqual(len(self.p.top_spenders(6, "GBP", 99)), 2)

    def test_no_clients(self):
        self.assertEqual(M.FXPlatform().top_spenders(1, "GBP", 5), [])

    def test_deposits_and_failures_do_not_count(self):
        self.assertIsNone(self.p.withdraw(7, "acme", "GBP", 99999))
        self.assertEqual(self.p.top_spenders(8, "GBP", 5), ["acme(0)", "beta(0)"])

    def test_tie_is_alphabetical(self):
        self.p.withdraw(7, "acme", "GBP", 100)
        self.p.withdraw(8, "beta", "GBP", 100)
        self.assertEqual(self.p.top_spenders(9, "GBP", 5), ["acme(100)", "beta(100)"])


if __name__ == "__main__":
    unittest.main()
