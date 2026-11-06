"""Warm-up itertools1: groupby, pairwise, product, count + islice

Implement each function with the `itertools` module.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/06_iterators/itertools1.py
"""
import unittest
import itertools

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def runs(text):
    """'aaabcc' -> [('a', 3), ('b', 1), ('c', 2)]   (itertools.groupby)"""
    raise NotImplementedError


def neighbours(items):
    """[1, 2, 3] -> [(1, 2), (2, 3)]   (itertools.pairwise)"""
    raise NotImplementedError


def all_variants(colors, sizes):
    """(['red', 'blue'], ['S', 'M']) -> [('red', 'S'), ('red', 'M'), ('blue', 'S'), ('blue', 'M')]"""
    raise NotImplementedError


def squares_over(limit, n):
    """The first n squares (1, 4, 9, ...) greater than limit. Use itertools.count and islice."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_runs(self):
        self.assertEqual(runs("aaabcc"), [("a", 3), ("b", 1), ("c", 2)])
        self.assertEqual(runs("abca"), [("a", 1), ("b", 1), ("c", 1), ("a", 1)])

    def test_neighbours(self):
        self.assertEqual(neighbours([1, 2, 3]), [(1, 2), (2, 3)])
        self.assertEqual(neighbours([1]), [])

    def test_all_variants(self):
        self.assertEqual(
            all_variants(["red", "blue"], ["S", "M"]),
            [("red", "S"), ("red", "M"), ("blue", "S"), ("blue", "M")],
        )

    def test_squares_over(self):
        self.assertEqual(squares_over(10, 3), [16, 25, 36])


if __name__ == "__main__":
    unittest.main()
