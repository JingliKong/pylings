"""Reference solution for exercises/ex09_event_bus.py.

Single-threaded by design (state the assumption in an interview).  For
threads, guard ``_subs`` with a lock and copy the snapshot under it — but
never call handlers while holding it.
"""
import inspect
import itertools
import weakref


class _Subscription:
    __slots__ = ("pattern", "priority", "seq", "once", "active", "_ref", "_strong", "__weakref__")

    def __init__(self, pattern, handler, priority, seq, once, on_dead):
        self.pattern = tuple(pattern.split("."))
        self.priority = priority
        self.seq = seq
        self.once = once
        self.active = True
        if inspect.ismethod(handler):
            # obj.method creates a NEW bound-method object on every access, so
            # weakref.ref(obj.method) dies immediately.  WeakMethod stores
            # weak(obj) + the function and rebuilds the bound method.
            self._ref = weakref.WeakMethod(handler, lambda _ref: on_dead(self))
            self._strong = None
        else:
            self._ref = None
            self._strong = handler

    def handler(self):
        return self._strong if self._ref is None else self._ref()

    def matches(self, segments):
        return len(self.pattern) == len(segments) and all(
            p == "*" or p == s for p, s in zip(self.pattern, segments)
        )


class EventBus:
    def __init__(self):
        self._subs = []
        self._seq = itertools.count()

    def _remove(self, sub):
        sub.active = False
        try:
            self._subs.remove(sub)
        except ValueError:
            pass  # already removed: unsubscribe must be idempotent

    def subscribe(self, pattern, handler, *, priority=0, once=False):
        if not callable(handler):
            raise TypeError("handler must be callable")
        # The weakref callback must not keep the bus alive either.
        bus_ref = weakref.ref(self)

        def on_dead(sub):
            bus = bus_ref()
            if bus is not None:
                bus._remove(sub)

        sub = _Subscription(pattern, handler, priority, next(self._seq), once, on_dead)
        self._subs.append(sub)
        sub_ref = weakref.ref(sub)

        def unsubscribe():
            s = sub_ref()
            if s is not None:
                self._remove(s)

        return unsubscribe

    def _matching(self, event):
        segments = tuple(event.split("."))
        return sorted(
            (s for s in self._subs if s.active and s.matches(segments)),
            key=lambda s: (-s.priority, s.seq),
        )

    def emit(self, event, payload=None):
        snapshot = self._matching(event)  # later subscriptions are not called
        errors = []
        called = 0
        for sub in snapshot:
            if not sub.active:  # unsubscribed by an earlier handler
                continue
            handler = sub.handler()
            if handler is None:  # owner was garbage-collected
                self._remove(sub)
                continue
            if sub.once:
                self._remove(sub)  # BEFORE calling: re-entrant emit must not see it
            called += 1
            try:
                handler(event, payload)
            except Exception as exc:  # not BaseException: let KeyboardInterrupt through
                errors.append(exc)
        if errors:
            raise ExceptionGroup(f"{len(errors)} handler(s) failed for {event!r}", errors)
        return called

    def handler_count(self, event):
        return sum(1 for s in self._matching(event) if s.handler() is not None)
