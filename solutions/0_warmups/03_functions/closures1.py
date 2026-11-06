"""Solution: closures1 — closures, late binding, nonlocal

Why: Closures capture variables, not values: all four lambdas read `i` when
they are CALLED, after the loop ended. Assigning to a name makes it local,
so `count += 1` needs `nonlocal`.
"""
import unittest

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def make_multipliers():
    """Return [f0, f1, f2, f3] where fi(x) == i * x."""
    # Default arguments are evaluated when each lambda is created.
    return [lambda x, i=i: i * x for i in range(4)]


def make_counter():
    """Return a function that returns 1, 2, 3, ... on each call. Counters are independent."""
    count = 0

    def counter():
        nonlocal count
        count += 1
        return count

    return counter


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_multipliers(self):
        fs = make_multipliers()
        self.assertEqual([f(10) for f in fs], [0, 10, 20, 30])

    def test_counter(self):
        c1, c2 = make_counter(), make_counter()
        self.assertEqual([c1(), c1(), c1()], [1, 2, 3])
        self.assertEqual(c2(), 1)


if __name__ == "__main__":
    unittest.main()
