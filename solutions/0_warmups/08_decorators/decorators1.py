"""Solution: decorators1 — writing a decorator with functools.wraps

Why: `@deco` above `def f` means `f = deco(f)`. Inside the wrapper, `args`
is a tuple and `kwargs` a dict; pass them on with `*args, **kwargs`. Without
`functools.wraps` every decorated function is named "wrapper".
"""
import unittest
import functools

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def count_calls(fn):
    """Decorator. wrapper.calls is the number of calls so far.
    The decorated function keeps its __name__ and __doc__."""

    @functools.wraps(fn)  # copies __name__, __doc__, __module__..., sets __wrapped__
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return fn(*args, **kwargs)  # unpack again

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
