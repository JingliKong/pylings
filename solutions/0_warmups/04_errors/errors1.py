"""Solution: errors1 — narrow except, closing files, finally

Why: A bare `except:` also catches TypeError (a bug), KeyboardInterrupt and
SystemExit. `with open(...)` closes the file even when an exception happens.
`finally` runs on success, on error and on return.
"""
import unittest
import gc
import os
import tempfile
import warnings

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def parse_age(text):
    """int(text) if it is a whole number from 0 to 150, else None.
    Only bad VALUES return None: parse_age(None) is a programming error and must raise TypeError."""
    try:
        age = int(text)
    except ValueError:  # catch only what you can handle
        return None
    return age if 0 <= age <= 150 else None


def read_first_line(path):
    """First line of the file without its newline ('' for an empty file).
    A missing file raises FileNotFoundError. The file must always be closed."""
    with open(path, encoding="utf-8") as f:
        return f.readline().rstrip("\n")


def run_steps(steps, log):
    """Call each step() in order and append "ok" to log after each success.
    ALWAYS append "done" at the end, even if a step raises; the exception must still propagate."""
    try:
        for step in steps:
            step()
            log.append("ok")
    finally:
        log.append("done")


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_parse_age(self):
        self.assertEqual(parse_age("42"), 42)
        self.assertIsNone(parse_age("abc"))
        self.assertIsNone(parse_age("-1"))
        self.assertIsNone(parse_age("151"))
        with self.assertRaises(TypeError):
            parse_age(None)

    def test_read_first_line_closes_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "f.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write("first\nsecond\n")
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", ResourceWarning)
                self.assertEqual(read_first_line(path), "first")
                gc.collect()
            leaks = [w for w in caught if issubclass(w.category, ResourceWarning)]
            self.assertEqual(leaks, [], "the file was not closed")
        with self.assertRaises(FileNotFoundError):
            read_first_line("/definitely/missing/file.txt")

    def test_run_steps_always_logs_done(self):
        def boom():
            raise RuntimeError("step failed")

        log = []
        with self.assertRaises(RuntimeError):
            run_steps([lambda: None, boom, lambda: None], log)
        self.assertEqual(log, ["ok", "done"])
        log = []
        run_steps([lambda: None], log)
        self.assertEqual(log, ["ok", "done"])


if __name__ == "__main__":
    unittest.main()
