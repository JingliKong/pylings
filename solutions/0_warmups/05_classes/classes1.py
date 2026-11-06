"""Solution: classes1 — __init__, attributes, __repr__

Why: `x = x` in `__init__` assigns a local variable; attributes need `self.x
= x`. `__repr__` is what the REPL, debuggers and containers show; make it
look like the code that builds the object.
"""
import unittest

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


class Point:
    """Point(3, 4) has .x and .y, repr(Point(3, 4)) == "Point(x=3, y=4)",
    and p.distance_to(other) is the straight-line distance."""

    def __init__(self, x, y):
        self.x = x  # without `self.` these were just local variables
        self.y = y

    def distance_to(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5  # or math.dist

    def __repr__(self):
        return f"Point(x={self.x!r}, y={self.y!r})"


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_attributes(self):
        p = Point(3, 4)
        self.assertEqual((p.x, p.y), (3, 4))

    def test_repr(self):
        self.assertEqual(repr(Point(3, 4)), "Point(x=3, y=4)")
        self.assertEqual(str([Point(1, 2)]), "[Point(x=1, y=2)]")

    def test_distance(self):
        self.assertEqual(Point(0, 0).distance_to(Point(3, 4)), 5.0)
        self.assertEqual(Point(1, 1).distance_to(Point(4, 5)), 5.0)


if __name__ == "__main__":
    unittest.main()
