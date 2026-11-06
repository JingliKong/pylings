"""Solution: iterators1 — iterables vs iterators

Why: An ITERATOR is one-shot: `__iter__` returns itself and its state is
used up. An ITERABLE (like a list) returns a NEW iterator from each
`__iter__` call, so it can be looped over many times.
"""
import unittest

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


class Countdown:
    """Iterable from start down to 1. It can be iterated MANY times:
    list(c) == list(c) == [3, 2, 1]."""

    def __init__(self, start):
        self.start = start

    def __iter__(self):
        # A generator method: every call to iter() gets a fresh, independent iterator.
        n = self.start
        while n > 0:
            yield n
            n -= 1


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
