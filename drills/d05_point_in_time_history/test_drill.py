import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLedger(unittest.TestCase):
    def setUp(self):
        self.g = M.Ledger()

    def _fixture(self):
        self.g.open(1, "a")
        self.g.credit(2, "a", 100)
        self.g.credit(5, "a", 50)
        self.g.debit(7, "a", 30)

    def test_basic_returns(self):
        self.assertIs(self.g.open(1, "a"), True)
        self.assertIs(self.g.open(2, "a"), False)
        self.assertEqual(self.g.credit(3, "a", 100), 100)
        self.assertEqual(self.g.debit(4, "a", 40), 60)
        self.assertIsNone(self.g.credit(5, "ghost", 1))
        self.assertIsNone(self.g.debit(6, "ghost", 1))

    def test_insufficient_debit_is_a_no_op(self):
        self.g.open(1, "a")
        self.g.credit(2, "a", 10)
        self.assertIsNone(self.g.debit(3, "a", 11))
        self.assertEqual(self.g.balance_at(4, "a", 3), 10)

    def test_includes_operation_at_exactly_time_at(self):
        self._fixture()
        self.assertEqual(self.g.balance_at(9, "a", 2), 100)
        self.assertEqual(self.g.balance_at(9, "a", 5), 150)
        self.assertEqual(self.g.balance_at(9, "a", 7), 120)

    def test_between_operations_holds_previous_value(self):
        self._fixture()
        self.assertEqual(self.g.balance_at(9, "a", 3), 100)
        self.assertEqual(self.g.balance_at(9, "a", 4), 100)
        self.assertEqual(self.g.balance_at(9, "a", 6), 150)

    def test_at_open_timestamp_is_zero(self):
        self._fixture()
        self.assertEqual(self.g.balance_at(9, "a", 1), 0)

    def test_before_creation_is_none(self):
        self._fixture()
        self.assertIsNone(self.g.balance_at(9, "a", 0))

    def test_future_time_at_is_current_state(self):
        self._fixture()
        self.assertEqual(self.g.balance_at(9, "a", 10 ** 9), 120)

    def test_unknown_account(self):
        self.assertIsNone(self.g.balance_at(1, "ghost", 1))

    def test_closed_account(self):
        self._fixture()
        self.assertIs(self.g.close(10, "a"), True)
        self.assertIs(self.g.close(11, "a"), False)
        self.assertEqual(self.g.balance_at(12, "a", 9), 120)
        self.assertIsNone(self.g.balance_at(12, "a", 10))
        self.assertIsNone(self.g.balance_at(12, "a", 11))

    def test_reopened_id_has_a_fresh_life(self):
        self._fixture()
        self.g.close(10, "a")
        self.assertIs(self.g.open(20, "a"), True)
        self.g.credit(21, "a", 7)
        self.assertEqual(self.g.balance_at(22, "a", 9), 120)   # old incarnation
        self.assertIsNone(self.g.balance_at(22, "a", 15))      # gap between lives
        self.assertEqual(self.g.balance_at(22, "a", 20), 0)
        self.assertEqual(self.g.balance_at(22, "a", 21), 7)

    def test_two_operations_same_timestamp_last_wins(self):
        self.g.open(1, "a")
        self.g.credit(2, "a", 10)
        self.g.credit(2, "a", 5)
        self.assertEqual(self.g.balance_at(3, "a", 2), 15)


if __name__ == "__main__":
    unittest.main()
