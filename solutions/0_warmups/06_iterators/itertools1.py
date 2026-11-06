"""Solution: itertools1 — groupby, pairwise, product, count + islice

Why: `groupby` groups CONSECUTIVE equal items (sort first if you want all
equal items together). `count()` is infinite; `islice` takes a bounded piece
of any iterator lazily.
"""
import unittest
import itertools

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def runs(text):
    """'aaabcc' -> [('a', 3), ('b', 1), ('c', 2)]   (itertools.groupby)"""
    return [(char, len(list(group))) for char, group in itertools.groupby(text)]


def neighbours(items):
    """[1, 2, 3] -> [(1, 2), (2, 3)]   (itertools.pairwise)"""
    return list(itertools.pairwise(items))


def all_variants(colors, sizes):
    """(['red', 'blue'], ['S', 'M']) -> [('red', 'S'), ('red', 'M'), ('blue', 'S'), ('blue', 'M')]"""
    return list(itertools.product(colors, sizes))


def squares_over(limit, n):
    """The first n squares (1, 4, 9, ...) greater than limit. Use itertools.count and islice."""
    squares = (i * i for i in itertools.count(1))
    return list(itertools.islice((s for s in squares if s > limit), n))


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
