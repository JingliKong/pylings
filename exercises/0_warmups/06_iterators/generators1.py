"""Warm-up generators1: generator functions and laziness

Implement the generators. read_records must be lazy.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/06_iterators/generators1.py
"""
import unittest
import inspect
import itertools

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


def countdown(n):
    """Yield n, n-1, ..., 1."""
    raise NotImplementedError


def read_records(lines):
    """Lazily yield {"name": ..., "age": int} for lines like "ann,31".
    Skip blank lines and lines starting with "#". Must be a generator."""
    records = []
    for line in lines:
        name, age = line.split(",")
        records.append({"name": name, "age": int(age)})
    return records


def fibonacci():
    """Infinite generator: 0, 1, 1, 2, 3, 5, 8, ..."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_countdown(self):
        self.assertEqual(list(countdown(3)), [3, 2, 1])
        self.assertEqual(list(countdown(0)), [])

    def test_read_records(self):
        lines = ["ann,31", "", "# comment", "bob,25"]
        self.assertEqual(list(read_records(lines)), [{"name": "ann", "age": 31}, {"name": "bob", "age": 25}])

    def test_read_records_is_lazy(self):
        self.assertTrue(inspect.isgenerator(read_records([])))
        exploding = itertools.chain(["ann,31"], (1 / 0 for _ in [1]))
        self.assertEqual(next(read_records(exploding)), {"name": "ann", "age": 31})

    def test_fibonacci(self):
        self.assertEqual(list(itertools.islice(fibonacci(), 8)), [0, 1, 1, 2, 3, 5, 8, 13])


if __name__ == "__main__":
    unittest.main()
