import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.f = M.Flags()

    def test_enable_at_has_no_expiry(self):
        self.assertEqual(self.f.enable_at("acme", "beta", 5), "")
        self.assertEqual(self.f.is_enabled_at("acme", "beta", 10 ** 9), "true")

    def test_ttl_half_open(self):
        self.f.enable_at_with_ttl("acme", "beta", 1, 9)
        self.assertEqual(self.f.is_enabled_at("acme", "beta", 1), "true")
        self.assertEqual(self.f.is_enabled_at("acme", "beta", 9), "true")
        self.assertEqual(self.f.is_enabled_at("acme", "beta", 10), "false")

    def test_reenable_resets_lifetime(self):
        self.f.enable_at_with_ttl("acme", "beta", 1, 9)
        self.f.enable_at_with_ttl("acme", "beta", 5, 10)
        self.assertEqual(self.f.is_enabled_at("acme", "beta", 14), "true")
        self.assertEqual(self.f.is_enabled_at("acme", "beta", 15), "false")

    def test_ttl_replaced_by_no_ttl(self):
        self.f.enable_at_with_ttl("acme", "beta", 1, 3)
        self.f.enable_at("acme", "beta", 2)
        self.assertEqual(self.f.is_enabled_at("acme", "beta", 10 ** 9), "true")

    def test_disable_at(self):
        self.f.enable_at_with_ttl("acme", "beta", 1, 10)
        self.assertEqual(self.f.disable_at("acme", "beta", 5), "true")
        self.assertEqual(self.f.disable_at("acme", "beta", 6), "false")
        self.assertEqual(self.f.is_enabled_at("acme", "beta", 7), "false")

    def test_disable_at_after_expiry_is_false(self):
        self.f.enable_at_with_ttl("acme", "beta", 1, 3)
        self.assertEqual(self.f.disable_at("acme", "beta", 4), "false")

    def test_list_flags_at_filters_expired(self):
        self.f.enable_at_with_ttl("acme", "fx_spot", 1, 5)
        self.f.enable_at("acme", "fx_hedge", 1)
        self.f.enable_at("acme", "ui_dark", 1)
        self.assertEqual(self.f.list_flags_at("acme", "fx", 3), "fx_hedge, fx_spot")
        self.assertEqual(self.f.list_flags_at("acme", "fx", 6), "fx_hedge")
        self.assertEqual(self.f.list_flags_at("acme", "", 6), "fx_hedge, ui_dark")
        self.assertEqual(self.f.list_flags_at("ghost", "", 6), "")

    def test_unknown_account_and_flag(self):
        self.assertEqual(self.f.is_enabled_at("ghost", "x", 1), "false")
        self.assertEqual(self.f.disable_at("ghost", "x", 1), "false")

    def test_accounts_are_independent(self):
        self.f.enable_at_with_ttl("a", "beta", 1, 5)
        self.f.enable_at_with_ttl("b", "beta", 1, 500)
        self.assertEqual(self.f.is_enabled_at("a", "beta", 10), "false")
        self.assertEqual(self.f.is_enabled_at("b", "beta", 10), "true")


if __name__ == "__main__":
    unittest.main()
