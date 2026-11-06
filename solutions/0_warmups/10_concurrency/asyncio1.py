"""Solution: asyncio1 — asyncio.gather and timeouts

Why: `await` in a loop runs one call after another. `asyncio.gather` (or a
TaskGroup) runs them concurrently and returns results in input order.
`asyncio.timeout` cancels the inner work and raises TimeoutError.
"""
import unittest
import asyncio
import time

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


async def fetch(name, delay):
    await asyncio.sleep(delay)
    return name.upper()


async def fetch_all(names, delay):
    """Fetch every name CONCURRENTLY. Results in the same order as names."""
    return await asyncio.gather(*(fetch(name, delay) for name in names))


async def fetch_or_default(name, delay, timeout, default):
    """Like fetch(), but give up after `timeout` seconds and return default."""
    try:
        async with asyncio.timeout(timeout):  # 3.11+; older: asyncio.wait_for
            return await fetch(name, delay)
    except TimeoutError:
        return default


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
