"""Reference solution for exercises/3_senior/ex16_async_worker_pool.py."""
import asyncio
import contextlib


class WorkerPool:
    def __init__(self, handler, *, workers, max_queue, timeout=None):
        if workers < 1:
            raise ValueError("workers must be >= 1")
        if max_queue < 1:
            raise ValueError("max_queue must be >= 1")
        self._handler = handler
        self._n = workers
        self._timeout = timeout
        self._queue = asyncio.Queue(maxsize=max_queue)
        self._workers = []
        self._closed = False

    async def __aenter__(self):
        self._workers = [asyncio.create_task(self._worker(), name=f"pool-worker-{i}") for i in range(self._n)]
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.shutdown(drain=exc_type is None)
        return False

    # -- submitting -------------------------------------------------------------
    async def submit(self, job):
        if self._closed or not self._workers:
            raise RuntimeError("pool is not running")
        fut = asyncio.get_running_loop().create_future()
        try:
            await self._queue.put((job, fut))  # backpressure
        except asyncio.QueueShutDown:
            # shutdown() wakes blocked putters with QueueShutDown.
            raise RuntimeError("pool is shutting down") from None
        return fut

    # -- workers ------------------------------------------------------------------
    async def _run(self, job):
        async with asyncio.timeout(self._timeout):  # timeout=None -> no limit
            return await self._handler(job)

    async def _worker(self):
        while True:
            try:
                job, fut = await self._queue.get()
            except asyncio.QueueShutDown:
                return  # graceful: queue shut down AND empty
            if fut.done():
                continue  # caller cancelled it while it was queued
            task = asyncio.create_task(self._run(job))
            # Caller cancels the future -> cancel the running handler.
            fut.add_done_callback(lambda f, t=task: t.cancel() if f.cancelled() else None)
            try:
                # asyncio.wait does not raise when `task` fails or is cancelled,
                # so a CancelledError here can only mean *this worker* is
                # being cancelled (hard shutdown).
                await asyncio.wait({task})
            except asyncio.CancelledError:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task  # don't leave it running past the worker
                fut.cancel()
                raise
            self._settle(fut, task)

    @staticmethod
    def _settle(fut, task):
        if task.cancelled():
            fut.cancel()
            return
        exc = task.exception()  # also marks the task's exception as retrieved
        if fut.done():
            return  # caller cancelled the future; result is unwanted
        if exc is not None:
            fut.set_exception(exc)
        else:
            fut.set_result(task.result())

    # -- shutdown -----------------------------------------------------------------
    def _cancel_queued(self):
        while True:
            try:
                _, fut = self._queue.get_nowait()
            except (asyncio.QueueEmpty, asyncio.QueueShutDown):
                return
            fut.cancel()

    async def shutdown(self, *, drain=True):
        self._closed = True
        self._queue.shutdown()  # rejects new and blocked put()s; get() drains what's left
        if not drain:
            self._cancel_queued()
            for w in self._workers:
                w.cancel()
        if self._workers:
            # gather (not wait) so a second, escalating shutdown(drain=False)
            # and this one both return once every worker is done.
            await asyncio.gather(*self._workers, return_exceptions=True)
