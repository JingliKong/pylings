import asyncio
import unittest

from _loader import load

WorkerPool = load("ex16_async_worker_pool").WorkerPool


def other_tasks():
    return {t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.done()}


async def settle(n=5):
    for _ in range(n):
        await asyncio.sleep(0)


class TestWorkerPool(unittest.IsolatedAsyncioTestCase):
    async def test_results_and_errors(self):
        async def handler(x):
            await asyncio.sleep(0)
            if x < 0:
                raise ValueError(x)
            return x * 2

        async with WorkerPool(handler, workers=2, max_queue=10) as pool:
            futs = [await pool.submit(x) for x in (1, -1, 2, -2, 3)]
            results = await asyncio.gather(*futs, return_exceptions=True)
        self.assertEqual(results[0::2], [2, 4, 6])
        self.assertIsInstance(results[1], ValueError)
        self.assertIsInstance(results[3], ValueError)
        self.assertEqual(other_tasks(), set())

    async def test_concurrency_limit(self):
        active = peak = 0

        async def handler(x):
            nonlocal active, peak
            active += 1
            peak = max(peak, active)
            await asyncio.sleep(0.005)
            active -= 1

        async with WorkerPool(handler, workers=3, max_queue=100) as pool:
            futs = [await pool.submit(i) for i in range(20)]
            await asyncio.gather(*futs)
        self.assertEqual(peak, 3)

    async def test_backpressure(self):
        release = asyncio.Event()

        async def handler(x):
            await release.wait()
            return x

        async with WorkerPool(handler, workers=1, max_queue=1) as pool:
            f1 = await pool.submit(1)
            await settle()  # worker picks up job 1
            f2 = await pool.submit(2)  # fills the queue
            with self.assertRaises(TimeoutError):
                await asyncio.wait_for(pool.submit(3), 0.05)
            release.set()
            self.assertEqual(await asyncio.gather(f1, f2), [1, 2])

    async def test_timeout_per_job(self):
        async def handler(x):
            await asyncio.sleep(x)
            return x

        async with WorkerPool(handler, workers=1, max_queue=10, timeout=0.05) as pool:
            slow = await pool.submit(10)
            fast = await pool.submit(0)
            with self.assertRaises(TimeoutError):
                await slow
            self.assertEqual(await fast, 0)

    async def test_cancel_queued_future_skips_job(self):
        release = asyncio.Event()
        ran = []

        async def handler(x):
            ran.append(x)
            await release.wait()
            return x

        async with WorkerPool(handler, workers=1, max_queue=10) as pool:
            f1 = await pool.submit(1)
            f2 = await pool.submit(2)
            f3 = await pool.submit(3)
            f2.cancel()
            release.set()
            self.assertEqual(await f1, 1)
            self.assertEqual(await f3, 3)
        self.assertEqual(ran, [1, 3])

    async def test_cancel_running_future_cancels_handler(self):
        handler_cancelled = asyncio.Event()

        async def handler(x):
            if x == "stuck":
                try:
                    await asyncio.sleep(100)
                except asyncio.CancelledError:
                    handler_cancelled.set()
                    raise
            return x

        async with WorkerPool(handler, workers=1, max_queue=10) as pool:
            f1 = await pool.submit("stuck")
            await settle()
            f1.cancel()
            await asyncio.wait_for(handler_cancelled.wait(), 1)
            f2 = await pool.submit("next")
            self.assertEqual(await asyncio.wait_for(f2, 1), "next")  # worker survived

    async def test_graceful_shutdown_drains(self):
        done = []

        async def handler(x):
            await asyncio.sleep(0.001)
            done.append(x)
            return x

        pool = WorkerPool(handler, workers=2, max_queue=100)
        async with pool:
            futs = [await pool.submit(i) for i in range(10)]
        self.assertEqual(sorted(done), list(range(10)))
        self.assertTrue(all(f.done() and not f.cancelled() for f in futs))
        with self.assertRaises(RuntimeError):
            await pool.submit(99)
        await pool.shutdown()  # idempotent
        self.assertEqual(other_tasks(), set())

    async def test_blocked_submitter_rejected_on_shutdown(self):
        release = asyncio.Event()

        async def handler(x):
            await release.wait()
            return x

        pool = WorkerPool(handler, workers=1, max_queue=1)
        await pool.__aenter__()
        f1 = await pool.submit(1)
        await settle()
        f2 = await pool.submit(2)
        blocked = asyncio.create_task(pool.submit(3))
        await settle()
        self.assertFalse(blocked.done())
        stopper = asyncio.create_task(pool.shutdown(drain=True))
        await settle()
        with self.assertRaises(RuntimeError):
            await asyncio.wait_for(blocked, 1)
        release.set()
        await asyncio.wait_for(stopper, 1)
        self.assertEqual(await asyncio.gather(f1, f2), [1, 2])
        self.assertEqual(other_tasks(), set())

    async def test_hard_shutdown_cancels(self):
        handler_cancelled = asyncio.Event()

        async def handler(x):
            try:
                await asyncio.sleep(100)
            except asyncio.CancelledError:
                handler_cancelled.set()
                raise

        pool = WorkerPool(handler, workers=1, max_queue=10)
        await pool.__aenter__()
        running = await pool.submit(1)
        queued = await pool.submit(2)
        await settle()
        await asyncio.wait_for(pool.shutdown(drain=False), 1)
        self.assertTrue(handler_cancelled.is_set())
        self.assertTrue(running.cancelled())
        self.assertTrue(queued.cancelled())
        self.assertEqual(other_tasks(), set())

    async def test_escalate_graceful_to_hard(self):
        async def handler(x):
            await asyncio.sleep(100)

        pool = WorkerPool(handler, workers=1, max_queue=10)
        await pool.__aenter__()
        fut = await pool.submit(1)
        await settle()
        graceful = asyncio.create_task(pool.shutdown(drain=True))
        await settle()
        self.assertFalse(graceful.done())
        await asyncio.wait_for(pool.shutdown(drain=False), 1)
        await asyncio.wait_for(graceful, 1)
        self.assertTrue(fut.cancelled())
        self.assertEqual(other_tasks(), set())

    async def test_aexit_with_error_cancels_and_propagates(self):
        async def handler(x):
            await asyncio.sleep(100)

        with self.assertRaises(KeyError):
            async with WorkerPool(handler, workers=2, max_queue=10) as pool:
                fut = await pool.submit(1)
                await settle()
                raise KeyError("boom")
        self.assertTrue(fut.cancelled())
        self.assertEqual(other_tasks(), set())

    async def test_validation(self):
        async def h(x):
            return x

        with self.assertRaises(ValueError):
            WorkerPool(h, workers=0, max_queue=1)
        with self.assertRaises(ValueError):
            WorkerPool(h, workers=1, max_queue=0)


if __name__ == "__main__":
    unittest.main()
