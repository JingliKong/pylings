import itertools
import unittest

from _loader import load

M = load("ex01_iter_tools")


def counting(iterable, log):
    for x in iterable:
        log.append(x)
        yield x


class TestChunked(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(list(M.chunked(range(5), 2)), [[0, 1], [2, 3], [4]])
        self.assertEqual(list(M.chunked(range(4), 2)), [[0, 1], [2, 3]])
        self.assertEqual(list(M.chunked([], 3)), [])

    def test_invalid_n_raises_at_call_time(self):
        for n in (0, -1):
            with self.assertRaises(ValueError):
                M.chunked([1, 2], n)  # no next() call

    def test_lazy_on_infinite_input(self):
        log = []
        gen = M.chunked(counting(itertools.count(), log), 3)
        self.assertEqual(next(gen), [0, 1, 2])
        self.assertEqual(log, [0, 1, 2])


class TestSlidingWindow(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(list(M.sliding_window("abcd", 3)), [("a", "b", "c"), ("b", "c", "d")])
        self.assertEqual(list(M.sliding_window([1, 2], 1)), [(1,), (2,)])

    def test_shorter_than_window(self):
        self.assertEqual(list(M.sliding_window([1, 2], 3)), [])
        self.assertEqual(list(M.sliding_window([], 1)), [])

    def test_invalid_n_raises_at_call_time(self):
        with self.assertRaises(ValueError):
            M.sliding_window([1], 0)

    def test_lazy(self):
        log = []
        gen = M.sliding_window(counting(itertools.count(), log), 2)
        self.assertEqual(next(gen), (0, 1))
        self.assertEqual(next(gen), (1, 2))
        self.assertEqual(log, [0, 1, 2])


class TestFlatten(unittest.TestCase):
    def test_full(self):
        self.assertEqual(list(M.flatten([1, [2, [3, [4]]], (5,), []])), [1, 2, 3, 4, 5])

    def test_strings_and_bytes_are_atoms(self):
        self.assertEqual(
            list(M.flatten(["ab", [b"cd", [bytearray(b"e")]]])),
            ["ab", b"cd", bytearray(b"e")],
        )

    def test_dict_expands_to_keys(self):
        self.assertEqual(list(M.flatten([{"a": 1, "b": 2}])), ["a", "b"])

    def test_depth(self):
        data = [1, [2, [3, [4]]]]
        self.assertEqual(list(M.flatten(data, depth=0)), [1, [2, [3, [4]]]])
        self.assertEqual(list(M.flatten(data, depth=1)), [1, 2, [3, [4]]])
        self.assertEqual(list(M.flatten(data, depth=2)), [1, 2, 3, [4]])

    def test_negative_depth_raises_at_call_time(self):
        with self.assertRaises(ValueError):
            M.flatten([1], depth=-1)

    def test_deep_nesting_no_recursion_error(self):
        data = [0]
        for i in range(1, 10_000):
            data = [data, i]
        out = list(M.flatten(data))
        self.assertEqual(out, list(range(10_000)))

    def test_lazy_with_infinite_inner(self):
        out = list(itertools.islice(M.flatten([[0], itertools.count(1)]), 5))
        self.assertEqual(out, [0, 1, 2, 3, 4])


class TestUniqueEverseen(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(list(M.unique_everseen("AAABBBCCDAABBB")), list("ABCD"))

    def test_key(self):
        self.assertEqual(list(M.unique_everseen("AbBa", key=str.lower)), ["A", "b"])

    def test_unhashable(self):
        data = [[1], [2], [1], {"a": 1}, {"a": 1}, 3, 3]
        self.assertEqual(list(M.unique_everseen(data)), [[1], [2], {"a": 1}, 3])

    def test_lazy(self):
        gen = M.unique_everseen(itertools.cycle([1, 2, 3, 4]))
        self.assertEqual(list(itertools.islice(gen, 4)), [1, 2, 3, 4])


if __name__ == "__main__":
    unittest.main()
