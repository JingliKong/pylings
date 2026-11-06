"""Exercise 16 — asyncio worker pool with backpressure and graceful shutdown.
                                                           Level: Senior

Time box: 50 min.  Every async service ends up with one of these (webhook
sender, email queue, crawler).  The happy path is 15 lines.  Shutdown and
cancellation are the interview.

    async with WorkerPool(send_webhook, workers=8, max_queue=1000) as pool:
        fut = await pool.submit(event)      # waits if the queue is full
        status = await fut                  # result of send_webhook(event)

Requirements
------------
1. ``WorkerPool(handler, *, workers, max_queue, timeout=None)``.  ``handler``
   is an ``async def`` function of one argument.  ``workers < 1`` or
   ``max_queue < 1`` -> ``ValueError``.  Workers start in ``__aenter__``.
2. At most ``workers`` handler calls run concurrently.
3. ``await pool.submit(job)`` -> an ``asyncio.Future`` that resolves to
   ``handler(job)``'s result, or holds its exception.  A failing job must
   not kill its worker.
4. Backpressure: ``submit`` waits while ``max_queue`` jobs are queued (not
   yet picked up by a worker).
5. ``timeout`` (seconds) per job: a job that runs longer gets
   ``TimeoutError`` in its future and the worker moves on.
6. If the *caller* cancels the returned future: a queued job is skipped; a
   running job's handler is cancelled.  Workers keep working.
7. ``await pool.shutdown(drain=True)``: stop accepting work (``submit`` ->
   ``RuntimeError``, including submitters currently blocked on a full
   queue), finish every queued and running job, stop the workers.
8. ``await pool.shutdown(drain=False)``: stop accepting work; cancel running
   handlers and cancel the futures of queued jobs; stop the workers.
9. ``shutdown`` is idempotent, and ``drain=False`` may be called while a
   ``drain=True`` shutdown is in progress (escalation, e.g. on a second
   SIGTERM).
10. ``__aexit__``: ``shutdown(drain=True)`` on normal exit,
    ``shutdown(drain=False)`` if the block raised.  Don't swallow the error.
11. After shutdown, no task created by the pool is still running.

Hint: ``asyncio.Queue.shutdown()`` exists since 3.13.

Discussion
----------
- Why does cancelling a task that is ``await``-ing another task cancel the
  inner one too, but ``asyncio.shield`` stops that?
- How do you tell "my worker is being cancelled" apart from "the handler I
  awaited was cancelled"?  (``Task.cancelling()``)
- In Kubernetes, the pod gets SIGTERM, then SIGKILL after
  ``terminationGracePeriodSeconds``.  Wire this pool to that.  What about
  jobs that were queued only in memory?
- This pool is in-memory.  When do you need a durable queue instead, and
  what does "at-least-once" force you to do in ``handler``?
"""


class WorkerPool:
    def __init__(self, handler, *, workers, max_queue, timeout=None):
        raise NotImplementedError

    async def __aenter__(self):
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc, tb):
        raise NotImplementedError

    async def submit(self, job):
        raise NotImplementedError

    async def shutdown(self, *, drain=True):
        raise NotImplementedError
