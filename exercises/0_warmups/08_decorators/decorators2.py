"""Warm-up decorators2: decorators that take arguments

Implement the decorator factories `repeat` and `tag`.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/08_decorators/decorators2.py
"""
import unittest
import functools

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def repeat(times):
    """@repeat(3) runs the function 3 times and returns the list of results.
    repeat(0) must raise ValueError immediately, when decorating."""
    raise NotImplementedError


def tag(*labels):
    """@tag("slow", "db") stores the labels on the function: fn.tags == {"slow", "db"}.
    The function itself is returned (no wrapper)."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_repeat(self):
        calls = []

        @repeat(3)
        def ping(x):
            calls.append(x)
            return len(calls)

        self.assertEqual(ping("a"), [1, 2, 3])
        self.assertEqual(ping.__name__, "ping")

    def test_repeat_validates_early(self):
        with self.assertRaises(ValueError):
            repeat(0)

    def test_tag(self):
        def job():
            return 1

        decorated = tag("slow", "db")(job)
        self.assertIs(decorated, job)
        self.assertEqual(job.tags, {"slow", "db"})


if __name__ == "__main__":
    unittest.main()
