"""Warm-up context1: writing a context-manager class

Fix Timer and implement Tag.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/07_context/context1.py
"""
import unittest
import time

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


class Timer:
    """with Timer() as t: ...
    Afterwards t.elapsed is the number of seconds the block took.
    Exceptions inside the block must propagate."""

    def __enter__(self):
        self.start = time.perf_counter()

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        return True


class Tag:
    """with Tag(out, "b"): out.append("hi")   ->   out == ["<b>", "hi", "</b>"]
    The closing tag is written even if the block raises."""

    def __init__(self, out, name):
        raise NotImplementedError


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
