"""Warm-up decorators1: writing a decorator with functools.wraps

Fix count_calls: the wrapped function must work normally and keep its name
and docstring.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/08_decorators/decorators1.py
"""
import unittest
import functools

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def count_calls(fn):
    """Decorator. wrapper.calls is the number of calls so far.
    The decorated function keeps its __name__ and __doc__."""

    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return fn(args, kwargs)

    wrapper.calls = 0
    return wrapper


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_counts_and_passes_arguments(self):
        @count_calls
        def add(a, b=0):
            """Add two numbers."""
            return a + b

        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add(1, b=5), 6)
        self.assertEqual(add.calls, 2)

    def test_keeps_metadata(self):
        @count_calls
        def add(a, b=0):
            """Add two numbers."""
            return a + b

        self.assertEqual(add.__name__, "add")
        self.assertEqual(add.__doc__, "Add two numbers.")


if __name__ == "__main__":
    unittest.main()
