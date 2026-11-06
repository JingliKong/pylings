"""Solution: errors2 — custom exceptions and raise ... from

Why: Callers catch exceptions by type, so raise a specific class and put the
data on it as attributes. `raise X from e` records the original error as
`__cause__` ("The above exception was the direct cause...").
"""
import unittest
import json

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


class InsufficientFunds(Exception):
    """Raised by Account.withdraw. Must have .balance and .amount attributes,
    and str(error) must mention both numbers."""

    def __init__(self, balance, amount):
        super().__init__(f"cannot withdraw {amount}: balance is {balance}")
        self.balance = balance
        self.amount = amount


class ConfigError(Exception):
    pass


class Account:
    def __init__(self, balance):
        self.balance = balance

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFunds(self.balance, amount)
        self.balance -= amount
        return self.balance


def load_config(text):
    """Parse a JSON object. Bad JSON -> ConfigError, chained to the original error
    with `raise ... from ...` (so error.__cause__ is the JSONDecodeError)."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ConfigError(f"invalid config: {e}") from e


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
