"""Warm-up errors2: custom exceptions and raise ... from

Make InsufficientFunds a useful exception, and chain ConfigError to the
original error.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/04_errors/errors2.py
"""
import unittest
import json

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


class InsufficientFunds(Exception):
    """Raised by Account.withdraw. Must have .balance and .amount attributes,
    and str(error) must mention both numbers."""


class ConfigError(Exception):
    pass


class Account:
    def __init__(self, balance):
        self.balance = balance

    def withdraw(self, amount):
        if amount > self.balance:
            raise Exception("insufficient funds")
        self.balance -= amount
        return self.balance


def load_config(text):
    """Parse a JSON object. Bad JSON -> ConfigError, chained to the original error
    with `raise ... from ...` (so error.__cause__ is the JSONDecodeError)."""
    try:
        return json.loads(text)
    except Exception:
        raise ConfigError("invalid config")


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_withdraw_ok(self):
        self.assertEqual(Account(100).withdraw(30), 70)

    def test_insufficient_funds(self):
        account = Account(50)
        with self.assertRaises(InsufficientFunds) as cm:
            account.withdraw(80)
        error = cm.exception
        self.assertEqual((error.balance, error.amount), (50, 80))
        self.assertIn("50", str(error))
        self.assertIn("80", str(error))
        self.assertEqual(account.balance, 50)

    def test_config_error_is_chained(self):
        self.assertEqual(load_config('{"a": 1}'), {"a": 1})
        with self.assertRaises(ConfigError) as cm:
            load_config("{not json")
        self.assertIsInstance(cm.exception.__cause__, json.JSONDecodeError)


if __name__ == "__main__":
    unittest.main()
