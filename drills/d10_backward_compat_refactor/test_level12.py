"""These already pass. They must STILL pass when you are done."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from loader import load  # noqa: E402

M = load(__file__)


class TestLevel12(unittest.TestCase):
    def setUp(self):
        self.f = M.Flags()

    def test_enable_returns_empty(self):
        self.assertEqual(self.f.enable("acme", "beta"), "")

    def test_is_enabled(self):
        self.f.enable("acme", "beta")
        self.assertEqual(self.f.is_enabled("acme", "beta"), "true")
        self.assertEqual(self.f.is_enabled("acme", "alpha"), "false")
        self.assertEqual(self.f.is_enabled("other", "beta"), "false")

    def test_disable(self):
        self.f.enable("acme", "beta")
        self.assertEqual(self.f.disable("acme", "beta"), "true")
        self.assertEqual(self.f.disable("acme", "beta"), "false")
        self.assertEqual(self.f.disable("nobody", "beta"), "false")
        self.assertEqual(self.f.is_enabled("acme", "beta"), "false")

    def test_enable_is_idempotent(self):
        self.f.enable("acme", "beta")
        self.f.enable("acme", "beta")
        self.assertEqual(self.f.disable("acme", "beta"), "true")
        self.assertEqual(self.f.disable("acme", "beta"), "false")

    def test_list_flags(self):
        for flag in ("fx_hedge", "fx_spot", "ui_dark"):
            self.f.enable("acme", flag)
        self.assertEqual(self.f.list_flags("acme", "fx"), "fx_hedge, fx_spot")
        self.assertEqual(self.f.list_flags("acme", ""), "fx_hedge, fx_spot, ui_dark")
        self.assertEqual(self.f.list_flags("acme", "zz"), "")
        self.assertEqual(self.f.list_flags("ghost", ""), "")

    def test_timeless_flags_never_expire(self):
        self.f.enable("acme", "beta")
        self.assertEqual(self.f.is_enabled("acme", "beta"), "true")
        self.assertEqual(self.f.list_flags("acme", "b"), "beta")


if __name__ == "__main__":
    unittest.main()
