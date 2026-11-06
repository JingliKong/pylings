"""Warm-up asyncio1: asyncio.gather and timeouts

Make fetch_all concurrent and implement fetch_or_default with a timeout.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/10_concurrency/asyncio1.py
"""
import unittest
import asyncio
import time

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


async def fetch(name, delay):
    await asyncio.sleep(delay)
    return name.upper()


async def fetch_all(names, delay):
    """Fetch every name CONCURRENTLY. Results in the same order as names."""
    results = []
    for name in names:
        results.append(await fetch(name, delay))
    return results


async def fetch_or_default(name, delay, timeout, default):
    """Like fetch(), but give up after `timeout` seconds and return default."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_all_is_concurrent(self):
        t0 = time.perf_counter()
        self.assertEqual(await fetch_all(["a", "b", "c", "d", "e"], 0.1), ["A", "B", "C", "D", "E"])
        self.assertLess(time.perf_counter() - t0, 0.3)

    async def test_fetch_or_default(self):
        self.assertEqual(await fetch_or_default("x", 1.0, 0.05, "late"), "late")
        self.assertEqual(await fetch_or_default("x", 0.0, 1.0, "late"), "X")


if __name__ == "__main__":
    unittest.main()
