import threading
import time
import unittest

from _loader import load

M = load("ex12_singleflight_cache")
memoize = M.memoize


class TestMemoize(unittest.TestCase):
    def test_caches_and_counts(self):
        calls = []

        @memoize()
        def f(x):
            calls.append(x)
            return x * 2

        self.assertEqual([f(1), f(1), f(2)], [2, 2, 4])
        self.assertEqual(calls, [1, 2])
        self.assertEqual(f.cache_info(), M.CacheInfo(hits=1, misses=2, currsize=2))

    def test_kwarg_order_does_not_matter(self):
        calls = []

        @memoize()
        def f(a, b):
            calls.append((a, b))
            return a + b

        f(a=1, b=2)
        f(b=2, a=1)
        self.assertEqual(len(calls), 1)

    def test_unhashable_args(self):
        @memoize()
        def f(x):
            return x

        with self.assertRaises(TypeError):
            f([1, 2])

    def test_wraps(self):
        def original(x):
            return x

        wrapped = memoize()(original)
        self.assertEqual(wrapped.__name__, "original")
        self.assertIs(wrapped.__wrapped__, original)

    def test_ttl_with_fake_clock(self):
        now = [0.0]
        calls = []

        @memoize(ttl=10, clock=lambda: now[0])
        def f(x):
            calls.append(x)
            return x

        f(1)
        now[0] = 9.99
        f(1)
        self.assertEqual(len(calls), 1)
        now[0] = 10.0
        f(1)
        self.assertEqual(len(calls), 2)

    def test_lru_eviction(self):
        calls = []

        @memoize(maxsize=2)
        def f(x):
            calls.append(x)
            return x

        f(1), f(2), f(1), f(3)  # 2 is least recently used -> evicted
        f(1)
        f(2)
        self.assertEqual(calls, [1, 2, 3, 2])
        self.assertEqual(f.cache_info().currsize, 2)

    def test_exceptions_not_cached(self):
        calls = []

        @memoize()
        def f(x):
            calls.append(x)
            if len(calls) == 1:
                raise ValueError("transient")
            return x

        with self.assertRaises(ValueError):
            f(1)
        self.assertEqual(f(1), 1)
        self.assertEqual(len(calls), 2)

    def test_cache_clear(self):
        calls = []

        @memoize()
        def f(x):
            calls.append(x)
            return x

        f(1)
        f.cache_clear()
        self.assertEqual(f.cache_info(), M.CacheInfo(0, 0, 0))
        f(1)
        self.assertEqual(len(calls), 2)

    def test_single_flight(self):
        started, release = threading.Event(), threading.Event()
        calls = []

        @memoize()
        def slow(x):
            calls.append(x)
            started.set()
            release.wait(5)
            return x * 2

        results = []
        lock = threading.Lock()

        def run():
            r = slow(1)
            with lock:
                results.append(r)

        threads = [threading.Thread(target=run) for _ in range(10)]
        threads[0].start()
        self.assertTrue(started.wait(5))
        for t in threads[1:]:
            t.start()
        time.sleep(0.1)  # let followers pile up on the in-flight call
        release.set()
        for t in threads:
            t.join(5)
        self.assertEqual(calls, [1])
        self.assertEqual(results, [2] * 10)
        self.assertEqual(slow.cache_info().misses, 1)
        self.assertEqual(slow.cache_info().hits, 9)

    def test_single_flight_exception_reaches_all_waiters(self):
        started, release = threading.Event(), threading.Event()
        calls = []

        @memoize()
        def boom(x):
            calls.append(x)
            started.set()
            release.wait(5)
            raise ValueError(x)

        errors = []
        lock = threading.Lock()

        def run():
            try:
                boom(1)
            except ValueError as e:
                with lock:
                    errors.append(e)

        threads = [threading.Thread(target=run) for _ in range(5)]
        threads[0].start()
        self.assertTrue(started.wait(5))
        for t in threads[1:]:
            t.start()
        time.sleep(0.1)
        release.set()
        for t in threads:
            t.join(5)
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(errors), 5)
        with self.assertRaises(ValueError):
            boom(1)  # not cached -> runs again
        self.assertEqual(len(calls), 2)

    def test_different_keys_do_not_block_each_other(self):
        started, release = threading.Event(), threading.Event()

        @memoize()
        def f(x):
            if x == 1:
                started.set()
                release.wait(5)
            return x

        t = threading.Thread(target=f, args=(1,))
        t.start()
        try:
            self.assertTrue(started.wait(5))
            t0 = time.perf_counter()
            self.assertEqual(f(2), 2)
            self.assertLess(time.perf_counter() - t0, 1.0)
        finally:
            release.set()
            t.join(5)


if __name__ == "__main__":
    unittest.main()
