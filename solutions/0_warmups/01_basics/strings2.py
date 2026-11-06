"""Solution: strings2 — f-string formatting

Why: Format spec mini-language: `,` adds thousands separators, `.2f` two
decimals, `<10`/`>5` align and pad. `{x=}` (3.8+) prints the expression and
its value — handy for debugging.
"""
import unittest

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def format_price(amount):
    """1234.5 -> '$1,234.50'"""
    return f"${amount:,.2f}"


def format_row(name, qty):
    """Name left-aligned in 10 chars, qty right-aligned in 5: 'apple     |    3'"""
    return f"{name:<10}|{qty:>5}"


def debug_line(user_id, ok):
    """Exactly: 'user_id=42 ok=True'"""
    return f"{user_id=} {ok=}"


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_format_price(self):
        self.assertEqual(format_price(1234.5), "$1,234.50")
        self.assertEqual(format_price(0), "$0.00")
        self.assertEqual(format_price(1000000), "$1,000,000.00")

    def test_format_row(self):
        self.assertEqual(format_row("apple", 3), "apple     |    3")
        self.assertEqual(format_row("kiwi", 120), "kiwi      |  120")

    def test_debug_line(self):
        self.assertEqual(debug_line(42, True), "user_id=42 ok=True")


if __name__ == "__main__":
    unittest.main()
