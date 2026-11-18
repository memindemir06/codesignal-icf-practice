import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.p = M.FXPlatform()
        self.p.create_client(1, "acme")
        self.p.deposit(2, "acme", "GBP", 10000)

    def test_quote_ids_are_sequential(self):
        self.assertEqual(self.p.quote(3, "GBP", "EUR", 11750, 100), "quote1")
        self.assertEqual(self.p.quote(4, "EUR", "USD", 10500, 100), "quote2")

    def test_spec_walkthrough(self):
        self.p.quote(3, "GBP", "EUR", 11750, 100)
        self.p.quote(4, "EUR", "USD", 10500, 100)
        self.assertEqual(self.p.execute(5, "acme", "quote1", 1000), 1175)
        self.assertEqual(self.p.execute(6, "acme", "quote1", 3), 1178)
        self.assertIsNone(self.p.execute(7, "acme", "quote9", 10))
        self.assertIsNone(self.p.execute(8, "ghost", "quote1", 10))
        self.assertIsNone(self.p.execute(9, "acme", "quote2", 5000))
        self.assertEqual(self.p.execute(10, "acme", "quote2", 1000), 1050)
        self.assertEqual(self.p.get_balance(11, "acme", "GBP"), 8997)
        self.assertEqual(self.p.get_balance(11, "acme", "EUR"), 178)
        self.assertEqual(self.p.top_spenders(12, "GBP", 5), ["acme(1003)"])
        self.assertEqual(self.p.top_spenders(13, "EUR", 5), ["acme(1000)"])

    def test_quote_lifetime_is_half_open(self):
        self.p.quote(3, "GBP", "EUR", 10000, 100)
        self.assertEqual(self.p.execute(102, "acme", "quote1", 10), 10)
        self.assertIsNone(self.p.execute(103, "acme", "quote1", 10))
        self.assertEqual(self.p.get_balance(104, "acme", "GBP"), 9990)

    def test_rate_rounds_down(self):
        self.p.quote(3, "GBP", "EUR", 11750, 1000)
        self.assertEqual(self.p.execute(4, "acme", "quote1", 3), 3)     # 3.525 -> 3
        self.assertEqual(self.p.execute(5, "acme", "quote1", 1), 4)     # 1.175 -> 1
        self.p.quote(6, "GBP", "USD", 9, 1000)
        self.assertEqual(self.p.execute(7, "acme", "quote2", 1000), 0)  # 0.9 -> 0

    def test_failed_execute_changes_nothing(self):
        self.p.quote(3, "GBP", "EUR", 11750, 100)
        self.assertIsNone(self.p.execute(4, "acme", "quote1", 10001))
        self.assertEqual(self.p.get_balance(5, "acme", "GBP"), 10000)
        self.assertEqual(self.p.get_balance(6, "acme", "EUR"), 0)
        self.assertEqual(self.p.top_spenders(7, "GBP", 5), ["acme(0)"])

    def test_a_quote_is_reusable_by_many_clients(self):
        self.p.create_client(3, "beta")
        self.p.deposit(4, "beta", "GBP", 500)
        self.p.quote(5, "GBP", "EUR", 20000, 100)
        self.assertEqual(self.p.execute(6, "acme", "quote1", 100), 200)
        self.assertEqual(self.p.execute(7, "beta", "quote1", 100), 200)
        self.assertEqual(self.p.top_spenders(8, "GBP", 5), ["acme(100)", "beta(100)"])

    def test_conversion_target_is_not_outgoing(self):
        self.p.quote(3, "GBP", "EUR", 10000, 100)
        self.p.execute(4, "acme", "quote1", 100)
        self.assertEqual(self.p.top_spenders(5, "EUR", 5), ["acme(0)"])

    def test_round_trip_conversion(self):
        self.p.quote(3, "GBP", "EUR", 20000, 1000)
        self.p.quote(4, "EUR", "GBP", 5000, 1000)
        self.assertEqual(self.p.execute(5, "acme", "quote1", 1000), 2000)
        self.assertEqual(self.p.execute(6, "acme", "quote2", 2000), 10000)
        self.assertEqual(self.p.get_balance(7, "acme", "EUR"), 0)
        self.assertEqual(self.p.top_spenders(8, "GBP", 5), ["acme(1000)"])
        self.assertEqual(self.p.top_spenders(9, "EUR", 5), ["acme(2000)"])


if __name__ == "__main__":
    unittest.main()
