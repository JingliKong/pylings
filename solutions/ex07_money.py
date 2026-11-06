"""Reference solution for exercises/ex07_money.py."""
import math
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation
from fractions import Fraction

CURRENCIES = {"USD": 2, "EUR": 2, "UZS": 2, "JPY": 0, "BHD": 3}


class CurrencyMismatch(ValueError):
    pass


def _quantum(currency):
    return Decimal(1).scaleb(-CURRENCIES[currency])  # USD -> Decimal('0.01')


class Money:
    __slots__ = ("amount", "currency")

    def __init__(self, amount, currency):
        # bool is an int subclass; Money(True, "USD") is never what you meant.
        if isinstance(amount, (float, bool)) or not isinstance(amount, (Decimal, int, str)):
            raise TypeError(f"amount must be Decimal, int or str, not {type(amount).__name__}")
        if currency not in CURRENCIES:
            raise ValueError(f"unknown currency {currency!r}")
        try:
            value = Decimal(amount)
            if not value.is_finite():
                raise ValueError(f"amount must be finite, got {amount!r}")
            quantized = value.quantize(_quantum(currency))
        except InvalidOperation:  # "abc", or too many digits for the context
            raise ValueError(f"invalid amount {amount!r}") from None
        if quantized != value:
            raise ValueError(f"{amount!r} has more precision than {currency} allows")
        if not quantized:
            quantized = quantized.copy_abs()  # no "-0.00 USD"
        object.__setattr__(self, "amount", quantized)
        object.__setattr__(self, "currency", currency)

    @classmethod
    def _make(cls, amount, currency):
        # Results of arithmetic are already in range; skip re-validation.
        m = object.__new__(cls)
        object.__setattr__(m, "amount", amount.copy_abs() if not amount else amount)
        object.__setattr__(m, "currency", currency)
        return m

    def __setattr__(self, name, value):
        raise AttributeError(f"{type(self).__name__} is immutable")

    __delattr__ = __setattr__

    # -- equality & hashing ---------------------------------------------------
    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented  # Python then falls back to identity -> False
        return self.currency == other.currency and self.amount == other.amount

    def __hash__(self):
        return hash((self.amount, self.currency))  # Decimal('1.0') and ('1.00') hash equal

    # -- arithmetic -------------------------------------------------------------
    def _check(self, other):
        if self.currency != other.currency:
            raise CurrencyMismatch(f"{self.currency} vs {other.currency}")

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return Money._make(self.amount + other.amount, self.currency)

    def __radd__(self, other):
        # sum() starts from int 0, so `0 + Money` must work.  Only 0, not any int.
        if type(other) is int and other == 0:
            return self
        return NotImplemented

    def __sub__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return Money._make(self.amount - other.amount, self.currency)

    def __mul__(self, n):
        if isinstance(n, bool) or not isinstance(n, (int, Decimal)):
            return NotImplemented
        value = (self.amount * n).quantize(_quantum(self.currency), rounding=ROUND_HALF_EVEN)
        return Money._make(value, self.currency)

    __rmul__ = __mul__

    def __neg__(self):
        return Money._make(-self.amount, self.currency)

    def __abs__(self):
        return Money._make(abs(self.amount), self.currency)

    def __bool__(self):
        return bool(self.amount)

    # -- ordering ---------------------------------------------------------------
    def _key(self, other):
        if not isinstance(other, Money):
            return None
        self._check(other)
        return other.amount

    def __lt__(self, other):
        o = self._key(other)
        return NotImplemented if o is None else self.amount < o

    def __le__(self, other):
        o = self._key(other)
        return NotImplemented if o is None else self.amount <= o

    def __gt__(self, other):
        o = self._key(other)
        return NotImplemented if o is None else self.amount > o

    def __ge__(self, other):
        o = self._key(other)
        return NotImplemented if o is None else self.amount >= o

    # -- allocation (largest remainder / Hamilton method) -------------------
    def allocate(self, ratios):
        ratios = list(ratios)
        if not ratios:
            raise ValueError("need at least one ratio")
        for r in ratios:
            if isinstance(r, (bool, float)) or not isinstance(r, (int, Decimal)) or r < 0:
                raise ValueError(f"invalid ratio {r!r}")
        total = sum(ratios)
        if total <= 0:
            raise ValueError("ratios must have a positive sum")

        minor = CURRENCIES[self.currency]
        units = int(self.amount.scaleb(minor))  # exact integer number of cents
        sign, units = (-1 if units < 0 else 1), abs(units)

        shares, remainders = [], []
        for i, r in enumerate(ratios):
            exact = Fraction(units) * Fraction(r) / Fraction(total)  # exact, no float drift
            base = math.floor(exact)
            shares.append(base)
            remainders.append((exact - base, i))
        leftover = units - sum(shares)
        for _, i in sorted(remainders, key=lambda t: (-t[0], t[1]))[:leftover]:
            shares[i] += 1
        return [Money._make(Decimal(sign * s).scaleb(-minor), self.currency) for s in shares]

    # -- display ------------------------------------------------------------------
    def __str__(self):
        return f"{self.amount:f} {self.currency}"

    def __repr__(self):
        return f"Money('{self.amount:f}', '{self.currency}')"
