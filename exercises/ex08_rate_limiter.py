"""Exercise 08 — Per-key token-bucket rate limiter.          Level: Middle+

Time box: 40 min.  (Exercise 17 has a broken one — this is the fixed
version.)  Every API gateway has one; the bugs are in time handling,
locking and memory.

    limiter = RateLimiter(rate=5, capacity=10)   # 5 tokens/s, bursts of 10
    if not limiter.acquire(client_ip):
        return 429, {"Retry-After": math.ceil(limiter.wait_time(client_ip))}

Requirements
------------
1. ``RateLimiter(rate, capacity, *, clock=time.monotonic)``: ``rate`` tokens
   per second are added to each key's bucket, up to ``capacity``.
   ``rate <= 0`` or ``capacity < 1`` -> ``ValueError``.
2. A key seen for the first time starts with a full bucket.
3. ``acquire(key, tokens=1) -> bool``: if the bucket holds at least
   ``tokens``, take them and return ``True``; otherwise take nothing and
   return ``False``.  Fractional tokens accumulate (rate=0.5 -> one token
   every 2 s).  ``tokens > capacity`` or ``tokens <= 0`` -> ``ValueError``
   (it could never succeed / makes no sense).
4. ``wait_time(key, tokens=1) -> float``: seconds until ``acquire(key,
   tokens)`` would succeed (0.0 if it would succeed now).  Does not consume.
5. Thread-safe: with a frozen clock, 50 threads calling ``acquire`` on one
   key with ``capacity=10`` get exactly 10 ``True``.
6. Robust to the clock: if ``clock()`` ever returns a smaller value than
   before (bad injected clock, VM migration), treat elapsed time as 0 — never
   remove tokens or exceed capacity because of it.
7. Memory: ``len(limiter)`` = number of keys currently tracked.
   ``cleanup() -> int`` drops every bucket that would be full by now
   (indistinguishable from a brand-new key, so dropping it changes no
   behaviour) and returns how many were dropped.

Discussion
----------
- Token bucket vs leaky bucket vs fixed window vs sliding-window log vs
  sliding-window counter: memory per key, burst behaviour, accuracy at window
  edges.
- Why ``time.monotonic()`` and not ``time.time()``?
- ``cleanup()`` is O(keys).  How would you make eviction amortised O(1)
  instead (hint: a heap or an ordered dict keyed by "full at" time)?
- You have 20 API servers.  How do you enforce one global limit?  (Redis +
  Lua script / ``INCR`` + ``EXPIRE``; local buckets with a share of the
  rate; what happens when Redis is down — fail open or closed?)
- One lock for all keys becomes a bottleneck.  Options?
"""
import time


class RateLimiter:
    def __init__(self, rate, capacity, *, clock=time.monotonic):
        raise NotImplementedError

    def acquire(self, key, tokens=1):
        raise NotImplementedError

    def wait_time(self, key, tokens=1):
        raise NotImplementedError

    def cleanup(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError
