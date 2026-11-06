"""Solution: decorators2 — decorators that take arguments

Why: `@repeat(3)` first CALLS `repeat(3)`, which must return the real
decorator; that decorator gets the function. Three levels: factory →
decorator → wrapper. A decorator doesn't have to wrap: it can register or
annotate the function and return it unchanged.
"""
import unittest
import functools

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def repeat(times):
    """@repeat(3) runs the function 3 times and returns the list of results.
    repeat(0) must raise ValueError immediately, when decorating."""
    if times < 1:
        raise ValueError("times must be >= 1")

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return [fn(*args, **kwargs) for _ in range(times)]

        return wrapper

    return decorator


def tag(*labels):
    """@tag("slow", "db") stores the labels on the function: fn.tags == {"slow", "db"}.
    The function itself is returned (no wrapper)."""

    def decorator(fn):
        fn.tags = set(labels)
        return fn

    return decorator


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
