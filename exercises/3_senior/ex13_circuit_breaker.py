"""Exercise 13 — Thread-safe circuit breaker.                Level: Senior

Time box: 45 min.  When a dependency is down, retrying makes it worse.  A
circuit breaker fails fast instead and probes for recovery.  The state
machine is easy; the concurrency is where people get it wrong.

    breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

    @breaker
    def charge(order): ...

    try:
        charge(order)
    except CircuitOpenError as e:
        return 503, {"Retry-After": math.ceil(e.retry_after)}

States::

    CLOSED --(threshold consecutive failures)--> OPEN
    OPEN   --(recovery_timeout elapsed)-------> HALF_OPEN
    HALF_OPEN --(trial succeeds)--> CLOSED
    HALF_OPEN --(trial fails)-----> OPEN (timer restarts)

Requirements
------------
1. ``CircuitBreaker(*, failure_threshold=5, recovery_timeout=30.0,
   half_open_max_calls=1, expected=(Exception,), clock=time.monotonic,
   on_state_change=None)``.  ``failure_threshold < 1``,
   ``recovery_timeout < 0`` or ``half_open_max_calls < 1`` -> ``ValueError``.
2. ``breaker.call(fn, *args, **kwargs)`` and ``@breaker`` (with
   ``functools.wraps``).  ``breaker.state`` is ``"closed"``, ``"open"`` or
   ``"half_open"``.  The OPEN -> HALF_OPEN move happens lazily: ``state`` (and
   ``call``) report ``"half_open"`` once the timeout has elapsed.
3. CLOSED: an exception that is an instance of ``expected`` counts as a
   failure; a success resets the count to 0 (the threshold is for
   *consecutive* failures).  Other exceptions propagate and count as
   neither.  The exception always propagates unchanged.
4. OPEN: raise ``CircuitOpenError`` without calling ``fn``.  Its
   ``retry_after`` attribute = seconds until the breaker goes half-open.
5. HALF_OPEN: at most ``half_open_max_calls`` trial calls may run at the same
   time; extra callers get ``CircuitOpenError`` (``retry_after=0.0``).
   A trial success -> CLOSED; a trial ``expected`` failure -> OPEN with a fresh
   timer.  A trial that raises a non-``expected`` exception just frees its
   slot.
6. Thread-safe.  Never hold the internal lock while ``fn`` runs.
7. **Stale results are ignored**: the outcome of a call that started before
   the most recent state transition must not change the state.  (A slow call
   that started while CLOSED and succeeds after the breaker opened must not
   close it.)
8. ``on_state_change(old, new)`` is called once per transition, *without*
   holding the internal lock (it may read ``breaker.state``).

Discussion
----------
- Why "consecutive failures" and not "failure rate over a window"?  When is
  each better?  What about slow calls — are they failures?
- Should a ``CircuitOpenError`` count as a failure in an outer breaker?
- One breaker per process vs per host vs per endpoint: what's the blast
  radius of each?  Why might per-process breakers in 200 pods all open at
  once?
- How do retries, timeouts, circuit breakers and bulkheads compose?  In
  what order do you wrap them?
"""
import time


class CircuitOpenError(RuntimeError):
    def __init__(self, retry_after):
        super().__init__(f"circuit open; retry after {retry_after:.2f}s")
        self.retry_after = retry_after


class CircuitBreaker:
    def __init__(
        self,
        *,
        failure_threshold=5,
        recovery_timeout=30.0,
        half_open_max_calls=1,
        expected=(Exception,),
        clock=time.monotonic,
        on_state_change=None,
    ):
        raise NotImplementedError

    @property
    def state(self):
        raise NotImplementedError

    def call(self, fn, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, fn):
        raise NotImplementedError
