"""Reference solution for exercises/1_middle/ex03_retry.py."""
import asyncio
import functools
import inspect
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
    # Validate at decoration time: a misconfigured decorator should fail at
    # import, not at 3am on the first error.
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    if isinstance(on, type):
        on = (on,)
    on = tuple(on)

    def delay_for(k):
        d = min(max_delay, base_delay * factor ** (k - 1))
        return rng() * d if jitter else d

    def decorator(fn):
        # The sync and async wrappers share the policy; only "how to wait"
        # differs.  A single wrapper can't serve both: an async wrapper must
        # be `async def` so that callers (and iscoroutinefunction) see it.
        if inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                for attempt in range(1, attempts + 1):
                    try:
                        return await fn(*args, **kwargs)
                    except on as exc:
                        if attempt == attempts:
                            raise  # bare raise: same object, traceback intact
                        delay = delay_for(attempt)
                        if on_retry is not None:
                            on_retry(attempt, exc, delay)
                    await async_sleep(delay)  # outside except: don't chain the next error to this one

            return async_wrapper

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except on as exc:
                    if attempt == attempts:
                        raise
                    delay = delay_for(attempt)
                    if on_retry is not None:
                        on_retry(attempt, exc, delay)
                sleep(delay)

        return wrapper

    return decorator
