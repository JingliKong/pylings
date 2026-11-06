"""Warm-up iterators1: iterables vs iterators

Make Countdown iterable more than once (and in nested loops).

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/06_iterators/iterators1.py
"""
import unittest

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


class Countdown:
    """Iterable from start down to 1. It can be iterated MANY times:
    list(c) == list(c) == [3, 2, 1]."""

    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_iterate_twice(self):
        c = Countdown(3)
        self.assertEqual(list(c), [3, 2, 1])
        self.assertEqual(list(c), [3, 2, 1])

    def test_nested_loops(self):
        c = Countdown(2)
        self.assertEqual([(a, b) for a in c for b in c], [(2, 2), (2, 1), (1, 2), (1, 1)])


if __name__ == "__main__":
    unittest.main()
