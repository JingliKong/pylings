"""Exercise 15 — asyncio: ordered, bounded, fail-fast, leak-free map.

Time box: 45–60 min.  ``asyncio.gather(*[fn(x) for x in items])`` creates
every task up front (unbounded memory and concurrency), can't consume an
infinite source, and leaves the other tasks running when one fails.
Write the version you'd put in a shared library.

    async with contextlib.aclosing(bounded_map(fetch, urls, limit=10)) as results:
        async for page in results:
            ...

Requirements
------------
1. ``bounded_map(fn, items, *, limit)`` is an async generator.  ``fn`` is an
   ``async def`` function of one argument.  ``items`` may be a sync OR async
   iterable, possibly infinite.
2. Results are yielded in INPUT order.
3. At most ``limit`` calls of ``fn`` are in flight at once — and the limit
   should actually be reached when there is enough work.
4. Lazy: at any moment, (#items pulled from ``items``) - (#results yielded)
   <= ``limit``.
5. Fail fast: if any in-flight call raises, raise that exception promptly
   (do not wait for slower, earlier items) — the original exception, not an
   ExceptionGroup.  All other in-flight calls must be cancelled AND awaited
   before the exception leaves ``bounded_map``.
6. If the consumer stops early and closes the generator (``aclose()`` /
   ``contextlib.aclosing``), all in-flight calls are cancelled and awaited.
   No task may outlive the generator.
7. ``limit < 1`` -> ``ValueError``.

Discussion
----------
- Why is ``aclosing`` needed?  What happens on ``break`` without it?
- Why does the asyncio event loop only keep weak references to tasks, and
  what bug does that cause in fire-and-forget code?
- How would you change this to yield results in *completion* order?
  What's the head-of-line blocking trade-off of input order?
"""


async def bounded_map(fn, items, *, limit):
    raise NotImplementedError
    yield  # makes this an async generator
