import asyncio
import contextlib
import itertools
import random
import unittest

from _loader import load

bounded_map = load("ex15_async_bounded_map").bounded_map


def other_tasks():
    return asyncio.all_tasks() - {asyncio.current_task()}


class TestBoundedMap(unittest.IsolatedAsyncioTestCase):
    async def test_preserves_input_order(self):
        rng = random.Random(7)
        delays = [rng.random() / 100 for _ in range(30)]

        async def work(i):
            await asyncio.sleep(delays[i])
            return i * i

        out = [r async for r in bounded_map(work, range(30), limit=5)]
        self.assertEqual(out, [i * i for i in range(30)])

    async def test_concurrency_limit_respected_and_reached(self):
        active = peak = 0

        async def work(x):
            nonlocal active, peak
            active += 1
            peak = max(peak, active)
            await asyncio.sleep(0.005 * (x % 3))
            active -= 1
            return x

        out = [r async for r in bounded_map(work, range(40), limit=4)]
        self.assertEqual(out, list(range(40)))
        self.assertEqual(peak, 4)

    async def test_lazy_on_infinite_source(self):
        pulled = 0

        def source():
            nonlocal pulled
            for i in itertools.count():
                pulled += 1
                yield i

        async def ident(x):
            await asyncio.sleep(0)
            return x

        got = []
        async with contextlib.aclosing(bounded_map(ident, source(), limit=3)) as agen:
            async for r in agen:
                got.append(r)
                if len(got) == 5:
                    break
        self.assertEqual(got, [0, 1, 2, 3, 4])
        self.assertLessEqual(pulled, 5 + 3)
        self.assertEqual(other_tasks(), set())

    async def test_async_iterable_source(self):
        async def source():
            for i in range(5):
                await asyncio.sleep(0)
                yield i

        async def double(x):
            return x * 2

        out = [r async for r in bounded_map(double, source(), limit=2)]
        self.assertEqual(out, [0, 2, 4, 6, 8])

    async def test_empty(self):
        async def f(x):
            return x

        self.assertEqual([r async for r in bounded_map(f, [], limit=3)], [])

    async def test_invalid_limit(self):
        async def f(x):
            return x

        with self.assertRaises(ValueError):
            async for _ in bounded_map(f, [1], limit=0):
                pass

    async def test_fail_fast_cancels_and_awaits_others(self):
        cancelled = []

        async def work(x):
            try:
                if x == 1:
                    await asyncio.sleep(0.01)
                    raise ValueError("bad item")
                await asyncio.sleep(10)
                return x
            except asyncio.CancelledError:
                cancelled.append(x)
                raise

        loop = asyncio.get_running_loop()
        t0 = loop.time()
        with self.assertRaises(ValueError) as ctx:
            async for _ in bounded_map(work, range(4), limit=4):
                pass
        self.assertEqual(str(ctx.exception), "bad item")
        self.assertLess(loop.time() - t0, 2)
        self.assertEqual(sorted(cancelled), [0, 2, 3])
        self.assertEqual(other_tasks(), set())

    async def test_early_close_cancels_in_flight(self):
        cancelled = []

        async def work(x):
            try:
                if x == 0:
                    await asyncio.sleep(0)
                    return x
                await asyncio.sleep(10)
                return x
            except asyncio.CancelledError:
                cancelled.append(x)
                raise

        async with contextlib.aclosing(bounded_map(work, range(10), limit=3)) as agen:
            async for r in agen:
                self.assertEqual(r, 0)
                break
        self.assertEqual(sorted(cancelled), [1, 2])
        self.assertEqual(other_tasks(), set())


if __name__ == "__main__":
    unittest.main()
