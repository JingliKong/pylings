"""Exercise 07 — A ``Money`` value object.                  Level: Middle+

Time box: 40 min.  Tests the data model (``__eq__``/``__hash__``, operators,
``NotImplemented``, immutability), ``Decimal``, and one algorithm that
finance teams care a lot about: splitting an amount without losing a cent.

    price = Money("19.99", "USD")
    total = price * 3                      # Money('59.97', 'USD')
    sum([Money("1", "USD"), Money("2", "USD")])   # Money('3.00', 'USD')
    Money("100", "USD").allocate([1, 1, 1])
    # -> [Money('33.34', 'USD'), Money('33.33', 'USD'), Money('33.33', 'USD')]

Requirements
------------
1. ``Money(amount, currency)``.  ``amount`` is ``Decimal``, ``int`` or ``str``;
   ``float`` -> ``TypeError`` (``Money(0.1, ...)`` is how bugs start).
   ``currency`` must be a key of ``CURRENCIES`` (code -> number of minor
   units), else ``ValueError``.  NaN / infinity -> ``ValueError``.
2. The amount is stored with exactly the currency's minor units
   (``Money("5", "USD").amount == Decimal("5.00")``).  More precision than
   the currency allows -> ``ValueError`` (``Money("1.005", "USD")``) — never
   round silently on construction.
3. Immutable: assigning any attribute raises ``AttributeError``.
   Hashable, and ``Money("1.0", "USD") == Money("1", "USD")`` with equal
   hashes.  ``==`` with a non-``Money`` is ``False`` (not an exception).
4. ``+``, ``-`` between the same currency.  Different currencies ->
   ``CurrencyMismatch`` (a ``ValueError`` subclass).  ``Money + 5`` ->
   ``TypeError``.  ``sum(list_of_money)`` must work without a ``start``
   argument (think about what ``sum`` does first).
5. ``money * n`` and ``n * money`` for ``int`` / ``Decimal`` ``n``; the result is
   rounded to minor units with ROUND_HALF_EVEN.  ``float`` or ``Money``
   multipliers -> ``TypeError``.  Unary ``-``, ``abs()``, ``bool()``
   (False for zero).
6. Ordering (``<``, ``<=``, ``>``, ``>=``) for the same currency;
   ``CurrencyMismatch`` for different currencies; ``TypeError`` against other
   types.
7. ``allocate(ratios)`` splits the amount into ``len(ratios)`` parts that sum
   EXACTLY to the original.  Each part gets ``floor`` of its exact share in
   minor units; leftover minor units go one at a time to the parts with the
   largest fractional remainder (ties: lower index first).  Ratios are
   non-negative ints/Decimals with a positive sum, else ``ValueError``.
   Negative amounts mirror positive ones:
   ``Money("-100", "USD").allocate([1, 1, 1])`` -> ``[-33.34, -33.33, -33.33]``.
8. ``str(m)`` -> ``"19.99 USD"``; ``repr(m)`` -> ``"Money('19.99', 'USD')"``.

Discussion
----------
- Why do ``Decimal("1.0")`` and ``Decimal("1.00")`` compare equal?  Why must
  they hash equal?  What would break in a dict if they didn't?
- Why does ``a + b`` return ``NotImplemented`` instead of raising
  ``TypeError`` directly?  What does Python do next?
- Should ``Money("10", "USD") == Money("10", "EUR")`` be ``False`` or raise?
- Banker's rounding vs half-up: who decides, and where in the code should
  that decision live?
- Where do exchange rates belong — in ``Money``?
"""
from decimal import Decimal

CURRENCIES = {"USD": 2, "EUR": 2, "UZS": 2, "JPY": 0, "BHD": 3}


class CurrencyMismatch(ValueError):
    pass


class Money:
    def __init__(self, amount, currency):
        raise NotImplementedError

    def allocate(self, ratios):
        raise NotImplementedError
