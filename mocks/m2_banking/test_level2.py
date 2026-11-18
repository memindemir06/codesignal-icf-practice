import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)
DAY = 86400000


class TestLevel2(unittest.TestCase):
    def setUp(self):
        self.b = M.BankingSystem()

    def test_no_activity_is_alphabetical(self):
        self.b.create_account(1, "acc3")
        self.b.create_account(2, "acc2")
        self.b.create_account(3, "acc1")
        self.assertEqual(self.b.top_spenders(4, 3), ["acc1(0)", "acc2(0)", "acc3(0)"])

    def test_ranking(self):
        self.b.create_account(1, "acc3")
        self.b.create_account(2, "acc2")
        self.b.create_account(3, "acc1")
        self.b.deposit(4, "acc3", 2000)
        self.b.deposit(5, "acc2", 3000)
        self.b.deposit(6, "acc3", 4000)
        self.assertEqual(self.b.transfer(8, "acc3", "acc2", 500), 5500)
        self.assertEqual(self.b.transfer(9, "acc3", "acc1", 1000), 4500)
        self.assertEqual(self.b.transfer(10, "acc1", "acc2", 700), 300)
        self.assertEqual(self.b.top_spenders(11, 3), ["acc3(1500)", "acc1(700)", "acc2(0)"])
        self.assertEqual(self.b.top_spenders(12, 1), ["acc3(1500)"])

    def test_fewer_accounts_than_n(self):
        self.b.create_account(1, "acc1")
        self.assertEqual(self.b.top_spenders(2, 99), ["acc1(0)"])

    def test_no_accounts(self):
        self.assertEqual(self.b.top_spenders(1, 5), [])

    def test_incoming_does_not_count(self):
        self.b.create_account(1, "a")
        self.b.create_account(2, "b")
        self.b.deposit(3, "a", 1000)
        self.b.transfer(4, "a", "b", 400)
        self.assertEqual(self.b.top_spenders(5, 2), ["a(400)", "b(0)"])

    def test_failed_transfers_do_not_count(self):
        self.b.create_account(1, "a")
        self.b.create_account(2, "b")
        self.b.deposit(3, "a", 10)
        self.assertIsNone(self.b.transfer(4, "a", "b", 999))
        self.assertEqual(self.b.top_spenders(5, 2), ["a(0)", "b(0)"])

    def test_tie_is_alphabetical(self):
        for i, name in enumerate(["z", "m", "a"], start=1):
            self.b.create_account(i, name)
        self.b.create_account(4, "sink")
        for i, name in enumerate(["z", "m", "a"], start=5):
            self.b.deposit(i, name, 100)
        for i, name in enumerate(["z", "m", "a"], start=8):
            self.b.transfer(i, name, "sink", 50)
        self.assertEqual(self.b.top_spenders(20, 4), ["a(50)", "m(50)", "z(50)", "sink(0)"])


if __name__ == "__main__":
    unittest.main()
