import unittest
from decimal import Decimal

from _loader import load

M = load("ex07_money")
Money = M.Money


def usd(x):
    return Money(x, "USD")


class TestConstruction(unittest.TestCase):
    def test_normalises_to_minor_units(self):
        self.assertEqual(usd(5).amount, Decimal("5.00"))
        self.assertEqual(usd("5.1").amount, Decimal("5.10"))
        self.assertEqual(Money("100", "JPY").amount, Decimal("100"))
        self.assertEqual(Money(Decimal("1.234"), "BHD").amount, Decimal("1.234"))

    def test_rejects_float_and_bad_types(self):
        for bad in (0.1, 1.0, True, None, [1]):
            with self.assertRaises(TypeError, msg=repr(bad)):
                usd(bad)

    def test_rejects_excess_precision_instead_of_rounding(self):
        with self.assertRaises(ValueError):
            usd("1.005")
        with self.assertRaises(ValueError):
            Money("1.5", "JPY")

    def test_rejects_bad_values_and_currency(self):
        for bad in ("abc", "NaN", "Infinity", Decimal("-inf")):
            with self.assertRaises(ValueError, msg=repr(bad)):
                usd(bad)
        with self.assertRaises(ValueError):
            Money("1", "XYZ")

    def test_immutable(self):
        m = usd("1")
        with self.assertRaises(AttributeError):
            m.amount = Decimal("2")
        with self.assertRaises(AttributeError):
            m.other = 1
        self.assertEqual(m.amount, Decimal("1.00"))

    def test_str_repr(self):
        self.assertEqual(str(usd("19.9")), "19.90 USD")
        self.assertEqual(repr(usd("19.9")), "Money('19.90', 'USD')")
        self.assertEqual(str(Money("-0", "USD")), "0.00 USD")


class TestEqualityHashing(unittest.TestCase):
    def test_equal_and_same_hash(self):
        self.assertEqual(usd("1.0"), usd(1))
        self.assertEqual(hash(usd("1.0")), hash(usd(1)))
        self.assertEqual(len({usd("1"), usd("1.00"), usd("2")}), 2)

    def test_currency_matters(self):
        self.assertNotEqual(usd(10), Money(10, "EUR"))

    def test_eq_with_other_types_is_false(self):
        self.assertFalse(usd(1) == 1)
        self.assertFalse(usd(1) == Decimal("1.00"))
        self.assertTrue(usd(1) != "1.00 USD")


class TestArithmetic(unittest.TestCase):
    def test_add_sub(self):
        self.assertEqual(usd("1.10") + usd("2.25"), usd("3.35"))
        self.assertEqual(usd("1") - usd("2.5"), usd("-1.5"))

    def test_currency_mismatch(self):
        self.assertTrue(issubclass(M.CurrencyMismatch, ValueError))
        with self.assertRaises(M.CurrencyMismatch):
            usd(1) + Money(1, "EUR")
        with self.assertRaises(M.CurrencyMismatch):
            usd(1) < Money(1, "EUR")

    def test_add_number_is_type_error(self):
        with self.assertRaises(TypeError):
            usd(1) + 5
        with self.assertRaises(TypeError):
            usd(1) + Decimal("5")
        with self.assertRaises(TypeError):
            5 + usd(1)

    def test_sum_without_start(self):
        self.assertEqual(sum([usd("0.10")] * 10), usd("1"))
        self.assertEqual(sum([usd(1), usd(2)]), usd(3))

    def test_multiply(self):
        self.assertEqual(usd("19.99") * 3, usd("59.97"))
        self.assertEqual(3 * usd("19.99"), usd("59.97"))
        self.assertEqual(usd("1.00") * Decimal("0.125"), usd("0.12"))  # half-even: 0.125 -> 0.12
        self.assertEqual(usd("1.00") * Decimal("0.135"), usd("0.14"))  # half-even: 0.135 -> 0.14
        for bad in (1.5, usd(2), True):
            with self.assertRaises(TypeError, msg=repr(bad)):
                usd(1) * bad

    def test_unary_and_bool(self):
        self.assertEqual(-usd("1.5"), usd("-1.5"))
        self.assertEqual(abs(usd("-1.5")), usd("1.5"))
        self.assertFalse(usd(0))
        self.assertTrue(usd("0.01"))

    def test_ordering(self):
        self.assertLess(usd(1), usd(2))
        self.assertLessEqual(usd(2), usd("2.00"))
        self.assertGreater(usd(3), usd(2))
        self.assertEqual(max([usd(1), usd(5), usd(3)]), usd(5))
        with self.assertRaises(TypeError):
            usd(1) < 2


class TestAllocate(unittest.TestCase):
    def test_even_split(self):
        self.assertEqual(usd(100).allocate([1, 1, 1]), [usd("33.34"), usd("33.33"), usd("33.33")])

    def test_sums_exactly(self):
        for amount in ("0.01", "0.05", "99.99", "1000000.01"):
            for ratios in ([1, 1, 1], [3, 7], [1, 2, 3, 4, 5, 6, 7], [Decimal("0.3"), Decimal("0.7")]):
                parts = usd(amount).allocate(ratios)
                self.assertEqual(sum(parts), usd(amount), (amount, ratios))
                self.assertEqual(len(parts), len(ratios))

    def test_largest_remainder_wins(self):
        # 0.05 by 3:7 -> exact 1.5c / 3.5c -> floor 1c / 3c, leftover 1c: tie -> index 0
        self.assertEqual(usd("0.05").allocate([3, 7]), [usd("0.02"), usd("0.03")])
        # 0.10 by 1:1:5 -> 1.43c / 1.43c / 7.14c -> floor 1/1/7, leftover 1c -> index 0
        self.assertEqual(usd("0.10").allocate([1, 1, 5]), [usd("0.02"), usd("0.01"), usd("0.07")])
        # 1.00 by 1:2 -> 33.33 / 66.67 -> floor 33/66, leftover 1c goes to the .67 remainder
        self.assertEqual(usd("1.00").allocate([1, 2]), [usd("0.33"), usd("0.67")])

    def test_zero_ratio_gets_nothing(self):
        self.assertEqual(usd("10").allocate([0, 1, 1]), [usd(0), usd(5), usd(5)])

    def test_negative_amount_mirrors(self):
        self.assertEqual(usd(-100).allocate([1, 1, 1]), [usd("-33.34"), usd("-33.33"), usd("-33.33")])

    def test_zero_decimal_currency(self):
        self.assertEqual(Money(100, "JPY").allocate([1, 1, 1]), [Money(34, "JPY"), Money(33, "JPY"), Money(33, "JPY")])

    def test_invalid_ratios(self):
        for ratios in ([], [0, 0], [1, -1], [0.5, 0.5]):
            with self.assertRaises(ValueError, msg=repr(ratios)):
                usd(1).allocate(ratios)


if __name__ == "__main__":
    unittest.main()
