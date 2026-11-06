"""Warm-up classes1: __init__, attributes, __repr__

Fix Point and add a __repr__.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/05_classes/classes1.py
"""
import unittest

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


class Point:
    """Point(3, 4) has .x and .y, repr(Point(3, 4)) == "Point(x=3, y=4)",
    and p.distance_to(other) is the straight-line distance."""

    def __init__(self, x, y):
        x = x
        y = y

    def distance_to(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y)) ** 0.5

    # TODO: __repr__


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
