import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.p = M.FXPlatform()

    def _acme(self):
        self.p.create_client(1, "acme")
        self.p.create_client(2, "acme-eu")
        self.p.deposit(3, "acme", "GBP", 1000)
        self.p.deposit(4, "acme-eu", "EUR", 700)
        self.p.deposit(5, "acme-eu", "GBP", 300)
        self.p.withdraw(6, "acme-eu", "GBP", 100)

    def test_balance_at_basics(self):
        self.p.create_client(1, "a")
        self.p.deposit(3, "a", "GBP", 100)
        self.p.deposit(7, "a", "GBP", 50)
        self.assertIsNone(self.p.balance_at(9, "a", "GBP", 0))
        self.assertEqual(self.p.balance_at(9, "a", "GBP", 1), 0)
        self.assertEqual(self.p.balance_at(9, "a", "GBP", 3), 100)
        self.assertEqual(self.p.balance_at(9, "a", "GBP", 6), 100)
        self.assertEqual(self.p.balance_at(9, "a", "GBP", 7), 150)
        self.assertEqual(self.p.balance_at(9, "a", "EUR", 7), 0)
        self.assertIsNone(self.p.balance_at(9, "ghost", "GBP", 7))

    def test_balance_at_tracks_conversions(self):
        self.p.create_client(1, "a")
        self.p.deposit(2, "a", "GBP", 1000)
        self.p.quote(3, "GBP", "EUR", 11750, 100)
        self.p.execute(4, "a", "quote1", 1000)
        self.assertEqual(self.p.balance_at(5, "a", "GBP", 3), 1000)
        self.assertEqual(self.p.balance_at(5, "a", "GBP", 4), 0)
        self.assertEqual(self.p.balance_at(5, "a", "EUR", 3), 0)
        self.assertEqual(self.p.balance_at(5, "a", "EUR", 4), 1175)

    def test_merge_guards(self):
        self._acme()
        self.assertIs(self.p.merge_clients(7, "acme", "acme"), False)
        self.assertIs(self.p.merge_clients(8, "acme", "ghost"), False)
        self.assertIs(self.p.merge_clients(9, "ghost", "acme"), False)
        self.assertIs(self.p.merge_clients(10, "acme", "acme-eu"), True)
        self.assertIs(self.p.merge_clients(11, "acme", "acme-eu"), False)

    def test_spec_walkthrough(self):
        self._acme()
        self.assertIs(self.p.merge_clients(9, "acme", "acme-eu"), True)
        self.assertEqual(self.p.get_balance(10, "acme", "GBP"), 1200)
        self.assertEqual(self.p.get_balance(11, "acme", "EUR"), 700)
        self.assertIsNone(self.p.get_balance(12, "acme-eu", "GBP"))
        self.assertEqual(self.p.top_spenders(13, "GBP", 5), ["acme(100)"])
        self.assertEqual(self.p.balance_at(14, "acme", "GBP", 3), 1000)
        self.assertEqual(self.p.balance_at(15, "acme", "GBP", 5), 1300)
        self.assertEqual(self.p.balance_at(16, "acme", "EUR", 3), 0)
        self.assertEqual(self.p.balance_at(17, "acme", "EUR", 4), 700)
        self.assertIsNone(self.p.balance_at(18, "acme", "GBP", 0))
        self.assertIsNone(self.p.balance_at(19, "acme-eu", "GBP", 5))

    def test_dropped_client_is_dead(self):
        self._acme()
        self.p.merge_clients(9, "acme", "acme-eu")
        self.assertIsNone(self.p.deposit(10, "acme-eu", "GBP", 1))
        self.assertIsNone(self.p.withdraw(11, "acme-eu", "GBP", 1))
        self.assertIsNone(self.p.get_balance(12, "acme-eu", "GBP"))
        self.p.quote(13, "GBP", "EUR", 10000, 100)
        self.assertIsNone(self.p.execute(14, "acme-eu", "quote1", 1))
        self.assertEqual(self.p.top_spenders(15, "GBP", 5), ["acme(100)"])

    def test_merge_sums_outgoing_per_currency(self):
        self.p.create_client(1, "a")
        self.p.create_client(2, "b")
        self.p.deposit(3, "a", "GBP", 1000)
        self.p.deposit(4, "b", "GBP", 1000)
        self.p.deposit(5, "b", "EUR", 1000)
        self.p.withdraw(6, "a", "GBP", 100)
        self.p.withdraw(7, "b", "GBP", 200)
        self.p.withdraw(8, "b", "EUR", 300)
        self.p.merge_clients(9, "a", "b")
        self.assertEqual(self.p.top_spenders(10, "GBP", 5), ["a(300)"])
        self.assertEqual(self.p.top_spenders(11, "EUR", 5), ["a(300)"])

    def test_merge_does_not_backdate_the_keeper(self):
        self.p.create_client(1, "b")
        self.p.deposit(2, "b", "GBP", 500)
        self.p.create_client(3, "a")
        self.p.deposit(4, "a", "GBP", 100)
        self.p.merge_clients(5, "a", "b")
        self.assertIsNone(self.p.balance_at(6, "a", "GBP", 2))
        self.assertEqual(self.p.balance_at(6, "a", "GBP", 3), 500)
        self.assertEqual(self.p.balance_at(6, "a", "GBP", 4), 600)

    def test_chained_merges(self):
        for i, name in enumerate(["a", "b", "c"], start=1):
            self.p.create_client(i, name)
        self.p.deposit(4, "a", "GBP", 100)
        self.p.deposit(5, "b", "GBP", 200)
        self.p.deposit(6, "c", "USD", 300)
        self.p.withdraw(7, "c", "USD", 50)
        self.p.merge_clients(8, "b", "c")
        self.p.merge_clients(9, "a", "b")
        self.assertEqual(self.p.get_balance(10, "a", "GBP"), 300)
        self.assertEqual(self.p.get_balance(11, "a", "USD"), 250)
        self.assertEqual(self.p.top_spenders(12, "USD", 5), ["a(50)"])
        self.assertEqual(self.p.balance_at(13, "a", "GBP", 5), 300)
        self.assertEqual(self.p.balance_at(14, "a", "USD", 6), 300)
        self.assertEqual(self.p.balance_at(15, "a", "USD", 7), 250)

    def test_activity_after_merge(self):
        self._acme()
        self.p.merge_clients(9, "acme", "acme-eu")
        self.assertEqual(self.p.withdraw(10, "acme", "GBP", 200), 1000)
        self.assertEqual(self.p.balance_at(11, "acme", "GBP", 9), 1200)
        self.assertEqual(self.p.balance_at(12, "acme", "GBP", 10), 1000)
        self.assertEqual(self.p.top_spenders(13, "GBP", 5), ["acme(300)"])

    def test_merge_of_a_client_with_no_activity(self):
        self.p.create_client(1, "a")
        self.p.create_client(2, "empty")
        self.p.deposit(3, "a", "GBP", 100)
        self.assertIs(self.p.merge_clients(4, "a", "empty"), True)
        self.assertEqual(self.p.get_balance(5, "a", "GBP"), 100)
        self.assertEqual(self.p.balance_at(6, "a", "GBP", 3), 100)
        self.assertEqual(self.p.top_spenders(7, "GBP", 5), ["a(0)"])


if __name__ == "__main__":
    unittest.main()
