"""Warm-up threads1: race conditions, Lock, ThreadPoolExecutor

Make Counter thread-safe and implement parallel_map.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/10_concurrency/threads1.py
"""
import unittest
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


class Counter:
    """A counter that many threads can increment safely."""

    def __init__(self):
        self.value = 0

    def increment(self):
        current = self.value
        time.sleep(0)  # simulates work between the read and the write
        self.value = current + 1


def parallel_map(fn, items, workers=4):
    """Like list(map(fn, items)), but runs fn in a pool of threads. Results in input order."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_counter_is_thread_safe(self):
        counter = Counter()

        def work():
            for _ in range(500):
                counter.increment()

        threads = [threading.Thread(target=work) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(counter.value, 4000)

    def test_parallel_map_order_and_speed(self):
        def slow_square(x):
            time.sleep(0.05)
            return x * x

        t0 = time.perf_counter()
        self.assertEqual(parallel_map(slow_square, range(8), workers=8), [x * x for x in range(8)])
        self.assertLess(time.perf_counter() - t0, 0.3)


if __name__ == "__main__":
    unittest.main()
