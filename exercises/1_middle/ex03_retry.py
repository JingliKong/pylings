"""Exercise 03 — A retry decorator you'd let into production.   Level: Middle

Time box: 30 min.  Everybody has written ``for i in range(3): try: ...``.
The interview is about the details: which errors, how long to wait, what
happens on the last attempt, and does it work for ``async def``.

    @retry(on=(ConnectionError, TimeoutError), attempts=4, base_delay=0.2)
    def fetch(url): ...

    @retry(on=(ConnectionError,))
    async def fetch_async(url): ...

Requirements
------------
1. ``retry(*, on, attempts=3, base_delay=0.1, factor=2.0, max_delay=5.0,
   jitter=False, sleep=time.sleep, async_sleep=asyncio.sleep,
   rng=random.random, on_retry=None)`` returns a decorator.
   ``on`` is required: an exception class or a tuple of them.
2. ``attempts`` is the TOTAL number of calls (``attempts=1`` = no retries).
   ``attempts < 1`` -> ``ValueError`` when ``retry(...)`` is called, i.e. at
   decoration time, not at the first call.
3. Only exceptions that are instances of ``on`` are retried.  Anything else
   propagates immediately, untouched.
4. Delay before retry number ``k`` (k = 1 for the first retry) is
   ``min(max_delay, base_delay * factor ** (k - 1))``.  With ``jitter=True``
   use "full jitter": ``rng() * that_delay``.
5. No sleep after the final failed attempt.  The final exception is
   re-raised as-is (the same exception object, not wrapped).
6. Works on regular functions (uses ``sleep``) AND on ``async def``
   functions (the wrapper is itself ``async def`` and awaits
   ``async_sleep``).  ``inspect.iscoroutinefunction(wrapped)`` must be True
   for async functions.
7. ``on_retry(attempt, exc, delay)`` is called (if given) before each sleep;
   ``attempt`` is the number of the attempt that just failed (1-based).
8. ``functools.wraps`` semantics.

Discussion
----------
- Why is retrying *every* exception a bug, even beyond "it hides bugs"?
  Think about non-idempotent operations (charging a card).
- What is a retry storm, and how does jitter help?  What about retries at
  several layers (client -> gateway -> service -> DB)?
- How would you add an overall deadline (``timeout=10``) that includes the
  sleeps?  How do you honour an HTTP ``Retry-After`` header?
- How do you make ``@retry`` work both with and without parentheses?
  Would you?
"""
import asyncio
import random
import time


def retry(
    *,
    on,
    attempts=3,
    base_delay=0.1,
    factor=2.0,
    max_delay=5.0,
    jitter=False,
    sleep=time.sleep,
    async_sleep=asyncio.sleep,
    rng=random.random,
    on_retry=None,
):
    raise NotImplementedError
