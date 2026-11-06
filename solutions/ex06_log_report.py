"""Reference solution for exercises/ex06_log_report.py."""
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

_METHOD = re.compile(r"[A-Z]+")
_LATENCY = re.compile(r"(\d+(?:\.\d+)?)ms")
_METRICS = {"count", "errors", "error_rate", "p50", "p95"}


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
        return self.errors / self.count if self.count else 0.0


class Report:
    def __init__(self, routes, malformed):
        self.routes = routes
        self.malformed = malformed

    def top(self, n, by="count"):
        if by not in _METRICS:
            raise ValueError(f"unknown metric {by!r}; expected one of {sorted(_METRICS)}")
        # Two stable sorts: secondary key first, then primary descending.
        # (Negating the primary key would also work for numbers, but this
        # pattern works for any type.)
        stats = sorted(self.routes.values(), key=lambda s: (s.route, s.method))
        stats.sort(key=lambda s: getattr(s, by), reverse=True)
        return stats[:n]


def normalize_route(path):
    path = path.split("?", 1)[0]
    return "/".join("{id}" if seg.isdecimal() else seg for seg in path.split("/"))


def _nearest_rank(sorted_values, p):
    rank = math.ceil(p * len(sorted_values) / 100)  # multiply first: keeps the rank exact for integer p
    return float(sorted_values[max(rank, 1) - 1])


def _parse(line):
    """Return (ts, method, path, status, latency_ms) or None if malformed."""
    parts = line.split()
    if len(parts) != 5:
        return None
    ts_s, method, path, status_s, latency_s = parts
    try:
        ts = datetime.fromisoformat(ts_s)
    except ValueError:
        return None
    if ts.tzinfo is None:  # naive timestamps are ambiguous: reject, don't guess
        return None
    if not _METHOD.fullmatch(method) or not path.startswith("/"):
        return None
    if not status_s.isdecimal() or not 100 <= int(status_s) <= 599:
        return None
    m = _LATENCY.fullmatch(latency_s)
    if m is None:
        return None
    return ts, method, path, int(status_s), float(m.group(1))


def analyze(lines, *, since=None, until=None):
    latencies = defaultdict(list)
    errors = defaultdict(int)
    malformed = 0
    for line in lines:
        if not line.strip():
            continue
        parsed = _parse(line)
        if parsed is None:
            malformed += 1
            continue
        ts, method, path, status, latency = parsed
        # Aware datetimes compare as instants regardless of their offsets.
        if (since is not None and ts < since) or (until is not None and ts >= until):
            continue
        key = (method, normalize_route(path))
        latencies[key].append(latency)
        if status >= 500:
            errors[key] += 1

    routes = {}
    for (method, route), values in latencies.items():
        values.sort()
        routes[method, route] = RouteStats(
            method=method,
            route=route,
            count=len(values),
            errors=errors[method, route],
            p50=_nearest_rank(values, 50),
            p95=_nearest_rank(values, 95),
        )
    return Report(routes, malformed)
