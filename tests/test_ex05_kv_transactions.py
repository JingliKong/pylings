import time
import unittest

from _loader import load

M = load("ex05_kv_transactions")
KV = M.KV


class TestKV(unittest.TestCase):
    def test_basic_ops(self):
        db = KV()
        db.set("a", 1)
        self.assertEqual(db.get("a"), 1)
        self.assertIsNone(db.get("zz"))
        self.assertEqual(db.get("zz", 0), 0)
        self.assertTrue(db.delete("a"))
        self.assertFalse(db.delete("a"))
        self.assertEqual(len(db), 0)

    def test_count(self):
        db = KV()
        db.set("a", 10)
        db.set("b", 10)
        db.set("c", 20)
        self.assertEqual(db.count(10), 2)
        db.set("a", 20)
        self.assertEqual((db.count(10), db.count(20)), (1, 2))
        db.delete("c")
        self.assertEqual(db.count(20), 1)
        self.assertEqual(db.count(999), 0)

    def test_rollback_restores_set_and_delete(self):
        db = KV()
        db.set("a", 1)
        db.set("b", 2)
        db.begin()
        db.set("a", 100)
        db.delete("b")
        db.set("c", 3)
        self.assertEqual((db.get("a"), db.get("b"), db.get("c")), (100, None, 3))
        self.assertEqual(db.count(100), 1)
        db.rollback()
        self.assertEqual((db.get("a"), db.get("b"), db.get("c")), (1, 2, None))
        self.assertEqual((db.count(1), db.count(2), db.count(3), db.count(100)), (1, 1, 0, 0))
        self.assertEqual(len(db), 2)

    def test_multiple_writes_same_key_in_tx(self):
        db = KV()
        db.set("a", 1)
        db.begin()
        db.set("a", 2)
        db.set("a", 3)
        db.delete("a")
        db.set("a", 4)
        db.rollback()
        self.assertEqual(db.get("a"), 1)
        self.assertEqual(db.count(1), 1)

    def test_nested_rollback_inner_only(self):
        db = KV()
        db.begin()
        db.set("a", 1)
        db.begin()
        db.set("a", 2)
        db.rollback()
        self.assertEqual(db.get("a"), 1)
        self.assertEqual(db.depth, 1)
        db.commit()
        self.assertEqual(db.get("a"), 1)
        self.assertEqual(db.depth, 0)

    def test_inner_commit_is_undone_by_outer_rollback(self):
        db = KV()
        db.set("a", "orig")
        db.begin()
        db.set("b", 1)
        db.begin()
        db.set("a", "inner")
        db.set("c", 3)
        db.commit()
        self.assertEqual(db.get("a"), "inner")
        db.rollback()
        self.assertEqual((db.get("a"), db.get("b"), db.get("c")), ("orig", None, None))
        self.assertEqual(db.count("inner"), 0)

    def test_outer_touched_key_first(self):
        db = KV()
        db.set("a", 0)
        db.begin()
        db.set("a", 1)
        db.begin()
        db.set("a", 2)
        db.commit()
        db.rollback()
        self.assertEqual(db.get("a"), 0)

    def test_no_transaction_errors(self):
        db = KV()
        with self.assertRaises(M.NoTransaction):
            db.commit()
        with self.assertRaises(M.NoTransaction):
            db.rollback()
        self.assertTrue(issubclass(M.NoTransaction, RuntimeError))

    def test_context_manager(self):
        db = KV()
        with db.transaction():
            db.set("a", 1)
        self.assertEqual(db.get("a"), 1)
        self.assertEqual(db.depth, 0)
        with self.assertRaises(ZeroDivisionError):
            with db.transaction():
                db.set("a", 2)
                with db.transaction():
                    db.set("b", 3)
                1 / 0
        self.assertEqual((db.get("a"), db.get("b")), (1, None))
        self.assertEqual(db.depth, 0)

    def test_inner_context_failure_keeps_outer(self):
        db = KV()
        with db.transaction():
            db.set("a", 1)
            try:
                with db.transaction():
                    db.set("a", 2)
                    raise ValueError
            except ValueError:
                pass
            self.assertEqual(db.get("a"), 1)
        self.assertEqual(db.get("a"), 1)

    def test_begin_is_cheap_on_big_store(self):
        db = KV()
        for i in range(200_000):
            db.set(i, i % 7)
        t0 = time.perf_counter()
        for i in range(3_000):
            db.begin()
            db.set(i, -1)
            db.rollback()
        self.assertLess(time.perf_counter() - t0, 1.0, "begin/rollback must not copy the store")
        t0 = time.perf_counter()
        for _ in range(3_000):
            db.count(3)
        self.assertLess(time.perf_counter() - t0, 1.0, "count() must not scan the store")
        self.assertEqual(db.count(-1), 0)


if __name__ == "__main__":
    unittest.main()
