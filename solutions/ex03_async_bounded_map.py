"""Reference solution for exercises/ex03_async_bounded_map.py."""
import asyncio
from collections import deque


def _aiter(items):
    if hasattr(items, "__aiter__"):
        return aiter(items)

    async def gen():
        for item in items:
            yield item

    return gen()


async def bounded_map(fn, items, *, limit):
    if limit < 1:
        raise ValueError("limit must be >= 1")
    source = _aiter(items)
    pending = deque()  # tasks in input order; len(pending) <= limit
    exhausted = False
    try:
        while True:
            while not exhausted and len(pending) < limit:
                try:
                    item = await anext(source)
                except StopAsyncIteration:
                    exhausted = True
                else:
                    pending.append(asyncio.create_task(fn(item)))
            if not pending:
                return

            head = pending[0]
            # Wait for the head, but wake on *any* completion so a failure
            # further back surfaces immediately (fail fast).
            while not head.done():
                done, _ = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    if not task.cancelled() and task.exception() is not None:
                        raise task.exception()
            pending.popleft()
            yield head.result()
    finally:
        # Runs on normal exit, on error, on aclose() (GeneratorExit) and if
        # the consumer task is cancelled. Cancel, then *await*, so no task
        # outlives us and no "exception was never retrieved" warnings.
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
        aclose = getattr(source, "aclose", None)
        if aclose is not None:
            await aclose()
