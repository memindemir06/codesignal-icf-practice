import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)
WAIT = 3600


class TestRewards(unittest.TestCase):
    def setUp(self):
        self.r = M.Rewards()

    def test_open_and_duplicate(self):
        self.assertIs(self.r.open_account(1, "a"), True)
        self.assertIs(self.r.open_account(2, "a"), False)

    def test_deposit_returns_balance_after(self):
        self.r.open_account(1, "a")
        self.assertEqual(self.r.deposit(2, "a", 100), 100)
        self.assertEqual(self.r.deposit(3, "a", 50), 150)
        self.assertIsNone(self.r.deposit(4, "ghost", 50))

    def test_spend_ids_are_global_and_sequential(self):
        self.r.open_account(1, "a")
        self.r.open_account(2, "b")
        self.r.deposit(3, "a", 1000)
        self.r.deposit(4, "b", 1000)
        self.assertEqual(self.r.spend(5, "a", 10), "reward1")
        self.assertEqual(self.r.spend(6, "b", 10), "reward2")
        self.assertEqual(self.r.spend(7, "a", 10), "reward3")

    def test_failed_spend_consumes_no_id_and_changes_nothing(self):
        self.r.open_account(1, "a")
        self.r.deposit(2, "a", 100)
        self.assertIsNone(self.r.spend(3, "a", 101))
        self.assertIsNone(self.r.spend(4, "ghost", 1))
        self.assertEqual(self.r.balance(5, "a"), 100)
        self.assertEqual(self.r.spend(6, "a", 100), "reward1")

    def test_cashback_rounds_down(self):
        self.r.open_account(1, "a")
        self.r.deposit(2, "a", 10000)
        self.r.spend(3, "a", 250)          # 12.5 -> 12
        self.r.spend(4, "a", 90)           # 4.5  -> 4
        self.r.spend(5, "a", 19)           # 0.95 -> 0
        self.assertEqual(self.r.balance(6, "a"), 10000 - 250 - 90 - 19)
        self.assertEqual(self.r.balance(3 + WAIT, "a"), 9641 + 12)
        self.assertEqual(self.r.balance(4 + WAIT, "a"), 9641 + 12 + 4)
        self.assertEqual(self.r.balance(5 + WAIT, "a"), 9641 + 12 + 4 + 0)

    def test_cashback_lands_exactly_at_due_timestamp(self):
        self.r.open_account(1, "a")
        self.r.deposit(2, "a", 1000)
        self.r.spend(3, "a", 250)
        self.assertEqual(self.r.balance(3 + WAIT - 1, "a"), 750)
        self.assertEqual(self.r.balance(3 + WAIT, "a"), 762)

    def test_settlement_happens_before_the_operation_at_that_timestamp(self):
        self.r.open_account(1, "a")
        self.r.deposit(2, "a", 1000)
        self.r.spend(3, "a", 250)
        # deposit AT the due timestamp must already include the cashback
        self.assertEqual(self.r.deposit(3 + WAIT, "a", 100), 750 + 12 + 100)

    def test_reward_status(self):
        self.r.open_account(1, "a")
        self.r.open_account(2, "b")
        self.r.deposit(3, "a", 1000)
        rid = self.r.spend(4, "a", 200)
        self.assertEqual(self.r.reward_status(5, "a", rid), "PENDING")
        self.assertIsNone(self.r.reward_status(6, "ghost", rid))
        self.assertIsNone(self.r.reward_status(7, "b", rid))       # wrong owner
        self.assertIsNone(self.r.reward_status(8, "a", "reward99"))
        self.assertEqual(self.r.reward_status(4 + WAIT, "a", rid), "PAID")

    def test_balance_of_missing_account(self):
        self.assertIsNone(self.r.balance(1, "ghost"))

    def test_spend_can_use_freshly_settled_cashback(self):
        self.r.open_account(1, "a")
        self.r.deposit(2, "a", 1000)
        self.r.spend(3, "a", 1000)                 # balance 0, cashback 50 due at 3+WAIT
        self.assertIsNone(self.r.spend(4, "a", 50))
        self.assertEqual(self.r.spend(3 + WAIT, "a", 50), "reward2")
        self.assertEqual(self.r.balance(3 + WAIT + 1, "a"), 0)


if __name__ == "__main__":
    unittest.main()
