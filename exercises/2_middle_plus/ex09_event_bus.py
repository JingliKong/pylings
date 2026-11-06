"""Exercise 09 — In-process event bus.                       Level: Middle+

Time box: 40 min.  Looks like a 10-line dict-of-lists.  The interview is
about what happens when handlers fail, unsubscribe during dispatch, or
belong to objects that should be garbage-collected.

    bus = EventBus()
    unsub = bus.subscribe("order.paid", send_receipt)
    bus.subscribe("order.*", audit_log, priority=10)
    bus.subscribe("order.paid", alert_once, once=True)
    bus.emit("order.paid", {"id": 7})
    unsub()

Requirements
------------
1. ``subscribe(pattern, handler, *, priority=0, once=False)`` returns an
   ``unsubscribe()`` callable (calling it twice is harmless).  Subscribing the
   same handler twice creates two independent subscriptions.
2. Patterns are dot-separated.  ``*`` matches exactly one segment:
   ``"order.*"`` matches ``"order.paid"`` but not ``"order"`` or
   ``"order.paid.late"``.  Other segments match literally.
3. ``emit(event, payload=None)`` calls ``handler(event, payload)`` for each
   matching subscription: higher ``priority`` first, then subscription
   order.  Returns the number of handlers called.
4. A failing handler must not stop the others.  After all handlers ran, if
   any raised, ``emit`` raises an ``ExceptionGroup`` containing all of their
   exceptions (in call order).
5. ``once=True``: the handler runs at most once, even if it emits the same
   event re-entrantly from inside itself.
6. Changes during ``emit``: a handler subscribed while an ``emit`` is running
   is not called by that ``emit``; a handler unsubscribed while an ``emit`` is
   running (by an earlier handler) is not called by it either.
7. Bound methods are held **weakly**: subscribing ``obj.method`` must not
   keep ``obj`` alive; once ``obj`` is collected, the subscription is gone.
   Plain functions and lambdas are held strongly (or nobody would keep
   ``bus.subscribe("x", lambda e, p: ...)`` alive).
8. ``handler_count(event)`` -> number of live subscriptions matching
   ``event``.

Discussion
----------
- Why is holding bound methods strongly a classic memory leak in GUI and
  plugin code?  Why can't you just use ``weakref.ref(obj.method)``?
- ExceptionGroup vs logging and swallowing vs failing fast: who should
  decide?  How would ``except*`` look at the call site?
- How would an async version differ?  Should ``emit`` await handlers
  sequentially, concurrently, or not at all ("fire and forget")?
- In-process bus vs a real broker (Kafka, RabbitMQ, Redis Streams): what
  guarantees do you lose if the process crashes after ``emit`` returns?
  What's the "outbox pattern"?
"""


class EventBus:
    def subscribe(self, pattern, handler, *, priority=0, once=False):
        raise NotImplementedError

    def emit(self, event, payload=None):
        raise NotImplementedError

    def handler_count(self, event):
        raise NotImplementedError
