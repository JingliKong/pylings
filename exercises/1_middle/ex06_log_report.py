"""Exercise 06 — Access-log report.                         Level: Middle

Time box: 40 min.  A very common take-home / live task: parse messy input,
aggregate, rank.  Graded on robustness (bad lines must not crash the job),
exact definitions (percentiles!), and clean data modelling.

Each line looks like::

    2026-11-03T10:15:02Z GET /api/users/42?verbose=1 200 123ms
    <timestamp>          <method> <path>          <status> <latency>

    report = analyze(open("access.log"), since=..., until=...)
    report.top(3, by="p95")   # -> [RouteStats(...), ...]

Requirements
------------
1. ``analyze(lines, *, since=None, until=None) -> Report``.  ``lines`` is any
   iterable of strings (may end with ``"\\n"``); consume it in one pass.
2. A valid line has exactly 5 whitespace-separated fields:
   - timestamp: ISO-8601 with timezone (``...Z`` or ``+05:00``);
   - method: an uppercase word (``GET``, ``POST``, ...);
   - path: starts with ``/``;
   - status: integer 100–599;
   - latency: a non-negative number followed by ``ms`` (``12`` or ``12.5``).
   Blank lines are ignored silently.  Any other bad line is skipped and
   counted in ``report.malformed`` — never raise.
3. Time filter: keep lines with ``since <= ts < until`` (either bound may be
   ``None``).  Bounds are timezone-aware datetimes; compare instants, not
   wall-clock strings (``10:00+05:00`` == ``05:00Z``).
4. Route normalisation: drop the query string, then replace every path
   segment that is all digits with ``{id}``:
   ``/api/users/42/orders/7?x=1`` -> ``/api/users/{id}/orders/{id}``.
5. ``report.routes`` is a dict ``(method, route) -> RouteStats`` with fields
   ``method, route, count, errors, p50, p95`` (latencies in ms, as float) and
   a property ``error_rate`` (= errors / count).  ``errors`` counts
   status >= 500.
6. Percentiles use the **nearest-rank** method: sort the latencies; the
   p-th percentile is the value at 1-based rank ``ceil(p / 100 * n)``.
7. ``report.top(n, by)`` with ``by`` in ``{"count", "errors", "error_rate",
   "p50", "p95"}`` returns the ``n`` routes with the highest value, ties
   broken by ``(route, method)`` ascending.  Unknown ``by`` -> ``ValueError``.

Discussion
----------
- Nearest-rank vs linear interpolation (``statistics.quantiles``): which do
  monitoring tools use?  Why can't you average p95s across servers?
- The log is 200 GB.  What changes?  (Streaming, sketches like t-digest /
  HDR histogram, parallel by file chunk, then merge.)
- Your ``{id}`` rule also turns ``/v2`` into ``/v2`` but ``/2024`` into
  ``/{id}``.  How would you handle UUIDs and slugs?  Who should own route
  templates — the log parser or the web framework?
- How would you test this with property-based testing (Hypothesis)?
"""
from dataclasses import dataclass


@dataclass
class RouteStats:
    method: str
    route: str
    count: int
    errors: int
    p50: float
    p95: float

    @property
    def error_rate(self):
        raise NotImplementedError


class Report:
    def __init__(self, routes, malformed):
        self.routes = routes
        self.malformed = malformed

    def top(self, n, by="count"):
        raise NotImplementedError


def analyze(lines, *, since=None, until=None):
    raise NotImplementedError
