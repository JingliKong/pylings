"""Solution: context1 — writing a context-manager class

Why: `with X() as v` binds `v` to whatever `__enter__` returns. `__exit__`
always runs; returning True means "I handled the exception" and suppresses
it.
"""
import unittest
import time

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


class Timer:
    """with Timer() as t: ...
    Afterwards t.elapsed is the number of seconds the block took.
    Exceptions inside the block must propagate."""

    def __enter__(self):
        self.start = time.perf_counter()
        return self  # this is what `as t` receives

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        return False  # a truthy return value would swallow the exception


class Tag:
    """with Tag(out, "b"): out.append("hi")   ->   out == ["<b>", "hi", "</b>"]
    The closing tag is written even if the block raises."""

    def __init__(self, out, name):
        self.out = out
        self.name = name

    def __enter__(self):
        self.out.append(f"<{self.name}>")
        return self

    def __exit__(self, exc_type, exc, tb):
        self.out.append(f"</{self.name}>")
        return False


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_timer_measures(self):
        with Timer() as t:
            time.sleep(0.02)
        self.assertGreaterEqual(t.elapsed, 0.015)

    def test_timer_lets_exceptions_through(self):
        with self.assertRaises(KeyError):
            with Timer():
                raise KeyError("x")

    def test_tag(self):
        out = []
        with Tag(out, "b"):
            out.append("hi")
        self.assertEqual(out, ["<b>", "hi", "</b>"])

    def test_tag_nested_and_on_error(self):
        out = []
        with self.assertRaises(ValueError):
            with Tag(out, "p"):
                with Tag(out, "i"):
                    raise ValueError
        self.assertEqual(out, ["<p>", "<i>", "</i>", "</p>"])


if __name__ == "__main__":
    unittest.main()
