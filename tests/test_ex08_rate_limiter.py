import threading
import unittest

from _loader import load

RateLimiter = load("ex08_rate_limiter").RateLimiter


class FakeClock:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()

    def make(self, rate=1, capacity=3):
        return RateLimiter(rate, capacity, clock=self.clock)

    def test_new_key_starts_full_then_denies(self):
        rl = self.make(capacity=3)
        self.assertEqual([rl.acquire("a") for _ in range(4)], [True, True, True, False])

    def test_refill_over_time(self):
        rl = self.make(rate=2, capacity=3)
        for _ in range(3):
            rl.acquire("a")
        self.assertFalse(rl.acquire("a"))
        self.clock.t += 0.5  # +1 token
        self.assertTrue(rl.acquire("a"))
        self.assertFalse(rl.acquire("a"))
        self.clock.t += 100  # refill caps at capacity
        self.assertEqual([rl.acquire("a") for _ in range(4)], [True, True, True, False])

    def test_fractional_rate_accumulates(self):
        rl = self.make(rate=0.5, capacity=1)
        self.assertTrue(rl.acquire("a"))
        self.clock.t += 1
        self.assertFalse(rl.acquire("a"))
        self.clock.t += 1
        self.assertTrue(rl.acquire("a"))

    def test_multi_token_acquire_is_all_or_nothing(self):
        rl = self.make(rate=1, capacity=5)
        self.assertTrue(rl.acquire("a", 4))
        self.assertFalse(rl.acquire("a", 2))
        self.assertTrue(rl.acquire("a", 1))  # the failed call took nothing

    def test_invalid_args(self):
        with self.assertRaises(ValueError):
            RateLimiter(0, 1)
        with self.assertRaises(ValueError):
            RateLimiter(1, 0)
        rl = self.make(capacity=3)
        for bad in (4, 0, -1):
            with self.assertRaises(ValueError):
                rl.acquire("a", bad)
            with self.assertRaises(ValueError):
                rl.wait_time("a", bad)

    def test_keys_are_independent(self):
        rl = self.make(capacity=1)
        self.assertTrue(rl.acquire("a"))
        self.assertTrue(rl.acquire("b"))
        self.assertFalse(rl.acquire("a"))

    def test_wait_time(self):
        rl = self.make(rate=2, capacity=4)
        self.assertEqual(rl.wait_time("new"), 0.0)
        self.assertTrue(rl.acquire("a", 4))
        self.assertAlmostEqual(rl.wait_time("a"), 0.5)
        self.assertAlmostEqual(rl.wait_time("a", 3), 1.5)
        self.assertAlmostEqual(rl.wait_time("a"), 0.5)  # did not consume
        self.clock.t += 0.5
        self.assertEqual(rl.wait_time("a"), 0.0)
        self.assertTrue(rl.acquire("a"))

    def test_clock_going_backwards(self):
        rl = self.make(rate=1, capacity=2)
        rl.acquire("a")
        rl.acquire("a")
        self.clock.t -= 50
        self.assertFalse(rl.acquire("a"))
        self.assertEqual(rl.wait_time("a"), 1.0)
        self.clock.t += 51  # back to +1 s after the original time
        self.assertTrue(rl.acquire("a"))
        self.assertFalse(rl.acquire("a"))

    def test_thread_safety_exact_count(self):
        rl = self.make(rate=1, capacity=10)  # frozen clock: no refill
        results = []
        lock = threading.Lock()
        barrier = threading.Barrier(50)

        def worker():
            barrier.wait()
            r = rl.acquire("hot")
            with lock:
                results.append(r)

        threads = [threading.Thread(target=worker) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(5)
        self.assertEqual(results.count(True), 10)
        self.assertEqual(len(results), 50)

    def test_cleanup_drops_only_full_buckets(self):
        rl = self.make(rate=1, capacity=2)
        rl.acquire("a")  # 1 token left
        rl.acquire("b")
        rl.acquire("b")  # 0 left
        rl.wait_time("a")
        self.assertEqual(len(rl), 2)
        self.clock.t += 1  # a is full again, b has 1
        self.assertEqual(rl.cleanup(), 1)
        self.assertEqual(len(rl), 1)
        self.assertTrue(rl.acquire("b"))
        self.assertFalse(rl.acquire("b"))  # b's state survived cleanup
        self.assertEqual([rl.acquire("a") for _ in range(3)], [True, True, False])


if __name__ == "__main__":
    unittest.main()
