"""Warm-up context2: contextlib.contextmanager and suppress

Fix temp_attr so it always restores the value, and implement
first_line_or_default.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/07_context/context2.py
"""
import unittest
import contextlib
import os
import tempfile
from contextlib import contextmanager

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


@contextmanager
def temp_attr(obj, name, value):
    """Set obj.<name> = value inside the block; restore the old value afterwards,
    even if the block raises."""
    old = getattr(obj, name)
    setattr(obj, name, value)
    yield
    setattr(obj, name, old)


def first_line_or_default(path, default):
    """First line of the file (without newline), or default if the file doesn't exist.
    Use contextlib.suppress instead of try/except."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    class Config:
        debug = False

    def test_temp_attr(self):
        cfg = self.Config()
        with temp_attr(cfg, "debug", True):
            self.assertTrue(cfg.debug)
        self.assertFalse(cfg.debug)

    def test_temp_attr_restores_on_error(self):
        cfg = self.Config()
        with self.assertRaises(ValueError):
            with temp_attr(cfg, "debug", True):
                raise ValueError
        self.assertFalse(cfg.debug)

    def test_first_line_or_default(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "a.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write("hello\nworld\n")
            self.assertEqual(first_line_or_default(path, "x"), "hello")
            self.assertEqual(first_line_or_default(os.path.join(d, "missing.txt"), "x"), "x")


if __name__ == "__main__":
    unittest.main()
