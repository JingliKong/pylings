"""Solution: generators1 — generator functions and laziness

Why: A function with `yield` returns a generator; its body runs step by step
on each `next()`, so it can process huge or infinite inputs. Building a list
reads everything first.
"""
import unittest
import inspect
import itertools

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


def countdown(n):
    """Yield n, n-1, ..., 1."""
    while n > 0:
        yield n
        n -= 1


def read_records(lines):
    """Lazily yield {"name": ..., "age": int} for lines like "ann,31".
    Skip blank lines and lines starting with "#". Must be a generator."""
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, age = line.split(",")
        yield {"name": name, "age": int(age)}


def fibonacci():
    """Infinite generator: 0, 1, 1, 2, 3, 5, 8, ..."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


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
