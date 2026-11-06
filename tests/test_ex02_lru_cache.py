import inspect
import time
import unittest

from _loader import load

M = load("ex02_lru_cache")
LRUCache = M.LRUCache


class TestLRUCache(unittest.TestCase):
    def test_basic_get_put(self):
        c = LRUCache(2)
        self.assertIsNone(c.put("a", 1))
        self.assertIsNone(c.put("b", 2))
        self.assertEqual(c.get("a"), 1)
        self.assertEqual(c.get("b"), 2)
        self.assertEqual(len(c), 2)

    def test_missing_key_returns_default(self):
        c = LRUCache(2)
        self.assertIsNone(c.get("x"))
        self.assertEqual(c.get("x", 42), 42)
        self.assertEqual(len(c), 0)

    def test_stored_none_is_not_missing(self):
        c = LRUCache(2)
        c.put("a", None)
        self.assertIsNone(c.get("a", "MISSING"))
        self.assertIn("a", c)

    def test_evicts_least_recently_used(self):
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        self.assertEqual(c.put("c", 3), ("a", 1))
        self.assertNotIn("a", c)
        self.assertEqual(c.keys(), ["c", "b"])

    def test_get_counts_as_use(self):
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        c.get("a")
        self.assertEqual(c.put("c", 3), ("b", 2))
        self.assertEqual(c.keys(), ["c", "a"])

    def test_update_counts_as_use_and_does_not_evict(self):
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        self.assertIsNone(c.put("a", 10))
        self.assertEqual(len(c), 2)
        self.assertEqual(c.put("c", 3), ("b", 2))
        self.assertEqual(c.get("a"), 10)

    def test_contains_does_not_count_as_use(self):
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        self.assertIn("a", c)
        self.assertEqual(c.put("c", 3), ("a", 1))

    def test_delete(self):
        c = LRUCache(3)
        c.put("a", 1)
        c.put("b", 2)
        self.assertTrue(c.delete("a"))
        self.assertFalse(c.delete("a"))
        self.assertEqual(c.keys(), ["b"])
        self.assertEqual(len(c), 1)
        c.put("c", 3)
        c.put("d", 4)
        self.assertEqual(len(c), 3)  # deleted slot was really freed

    def test_capacity_one(self):
        c = LRUCache(1)
        c.put("a", 1)
        self.assertEqual(c.put("b", 2), ("a", 1))
        self.assertEqual(c.keys(), ["b"])

    def test_invalid_capacity(self):
        for cap in (0, -1):
            with self.assertRaises(ValueError):
                LRUCache(cap)

    def test_keys_order_after_many_ops(self):
        c = LRUCache(4)
        for k in "abcd":
            c.put(k, k)
        c.get("b")
        c.put("a", "A")
        c.delete("c")
        self.assertEqual(c.keys(), ["a", "b", "d"])

    def test_operations_are_constant_time(self):
        c = LRUCache(50_000)
        t0 = time.perf_counter()
        for i in range(200_000):
            c.put(i, i)
            c.get(i - 10)
        self.assertLess(time.perf_counter() - t0, 3.0)
        self.assertEqual(len(c), 50_000)

    def test_does_not_use_ordereddict(self):
        src = inspect.getsource(M)
        code = "\n".join(line for line in src.splitlines() if not line.lstrip().startswith("#"))
        body = code.split('"""', 2)[-1]  # skip module docstring
        self.assertNotIn("OrderedDict", body)
        self.assertNotIn("lru_cache", body)


if __name__ == "__main__":
    unittest.main()
