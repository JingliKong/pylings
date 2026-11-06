"""Reference solution for exercises/2_middle_plus/ex08_rate_limiter.py.

Lazy refill: a bucket is just ``(tokens, last_update)``.  We never run a
timer; on each access we add ``elapsed * rate`` tokens.  That makes an idle
key cost nothing but its dict entry, and ``cleanup`` can drop it once it
would be full.
"""
import threading
import time


class RateLimiter:
    def __init__(self, rate, capacity, *, clock=time.monotonic):
        if rate <= 0:
            raise ValueError("rate must be > 0")
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self._rate = rate
        self._capacity = capacity
        self._clock = clock
        self._lock = threading.Lock()  # one lock: simple and correct; see Discussion for sharding
        self._buckets = {}  # key -> [tokens, last_update]

    def _validate(self, tokens):
        if not 0 < tokens <= self._capacity:
            raise ValueError(f"tokens must be in (0, {self._capacity}]")

    def _refill(self, key, now):
        """Return the up-to-date bucket for key.  Caller holds the lock."""
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = self._buckets[key] = [float(self._capacity), now]
            return bucket
        elapsed = now - bucket[1]
        if elapsed > 0:  # clock went backwards -> elapsed <= 0 -> add nothing
            bucket[0] = min(self._capacity, bucket[0] + elapsed * self._rate)
            bucket[1] = now
        # If the clock went backwards we keep the *later* timestamp, so the
        # time that "un-happened" isn't counted twice when the clock recovers.
        return bucket

    def acquire(self, key, tokens=1):
        self._validate(tokens)
        with self._lock:
            # Read the clock under the lock: otherwise a thread with an older
            # `now` can run after one with a newer `now`.
            bucket = self._refill(key, self._clock())
            if bucket[0] >= tokens:
                bucket[0] -= tokens
                return True
            return False

    def wait_time(self, key, tokens=1):
        self._validate(tokens)
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                return 0.0
            bucket = self._refill(key, self._clock())
            missing = tokens - bucket[0]
            return 0.0 if missing <= 0 else missing / self._rate

    def cleanup(self):
        with self._lock:
            now = self._clock()
            full = [
                key
                for key, (tok, last) in self._buckets.items()
                if tok + max(0.0, now - last) * self._rate >= self._capacity
            ]
            for key in full:
                del self._buckets[key]
            return len(full)

    def __len__(self):
        with self._lock:
            return len(self._buckets)
