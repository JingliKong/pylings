import unittest
from datetime import datetime, timedelta, timezone

from _loader import load

M = load("ex06_log_report")
UTC = timezone.utc

GOOD = [
    "2026-11-03T10:00:00Z GET /api/users/1 200 10ms\n",
    "2026-11-03T10:00:01Z GET /api/users/2?x=1 200 20ms\n",
    "2026-11-03T10:00:02Z GET /api/users/3 503 30ms\n",
    "2026-11-03T10:00:03Z POST /api/users 201 50.5ms\n",
    "2026-11-03T15:00:04+05:00 GET /api/users/4/orders/77 200 5ms\n",  # == 10:00:04Z
]
BAD = [
    "garbage\n",
    "2026-11-03T10:00:04Z GET /api/users/4 200 abc\n",  # latency
    "2026-11-03T10:00:05 GET /x 200 1ms\n",  # naive timestamp
    "2026-11-03T10:00:06Z get /x 200 1ms\n",  # lowercase method
    "2026-11-03T10:00:07Z GET x 200 1ms\n",  # path without /
    "2026-11-03T10:00:08Z GET /x 700 1ms\n",  # status out of range
    "2026-11-03T10:00:09Z GET /x 200 -1ms\n",  # negative latency
    "not-a-date GET /x 200 1ms\n",
    "2026-11-03T10:00:10Z GET /x 200 1ms extra\n",
]


def ts(seconds):
    return datetime(2026, 11, 3, 10, 0, 0, tzinfo=UTC) + timedelta(seconds=seconds)


class TestAnalyze(unittest.TestCase):
    def test_aggregates_and_normalises_routes(self):
        r = M.analyze(GOOD)
        self.assertEqual(
            set(r.routes),
            {("GET", "/api/users/{id}"), ("POST", "/api/users"), ("GET", "/api/users/{id}/orders/{id}")},
        )
        s = r.routes["GET", "/api/users/{id}"]
        self.assertEqual((s.count, s.errors), (3, 1))
        self.assertEqual((s.p50, s.p95), (20.0, 30.0))
        self.assertAlmostEqual(s.error_rate, 1 / 3)
        self.assertEqual(r.routes["POST", "/api/users"].p50, 50.5)

    def test_malformed_lines_counted_never_raise(self):
        r = M.analyze(GOOD + BAD + ["\n", "   \n", ""])
        self.assertEqual(r.malformed, len(BAD))
        self.assertEqual(sum(s.count for s in r.routes.values()), len(GOOD))

    def test_single_pass_over_iterator(self):
        r = M.analyze(iter(GOOD))
        self.assertEqual(sum(s.count for s in r.routes.values()), len(GOOD))

    def test_time_window_is_half_open_and_offset_aware(self):
        r = M.analyze(GOOD, since=ts(1), until=ts(4))
        self.assertEqual(r.routes["GET", "/api/users/{id}"].count, 2)  # :01 and :02
        self.assertIn(("POST", "/api/users"), r.routes)  # :03
        self.assertNotIn(("GET", "/api/users/{id}/orders/{id}"), r.routes)  # :04 excluded
        r2 = M.analyze(GOOD, since=ts(4))
        self.assertEqual(list(r2.routes), [("GET", "/api/users/{id}/orders/{id}")])

    def test_window_bound_in_other_timezone(self):
        tashkent = timezone(timedelta(hours=5))
        since = datetime(2026, 11, 3, 15, 0, 3, tzinfo=tashkent)  # == 10:00:03Z
        r = M.analyze(GOOD, since=since)
        self.assertEqual(sum(s.count for s in r.routes.values()), 2)

    def test_nearest_rank_percentiles(self):
        lines = [f"2026-11-03T10:00:00Z GET /p {200} {i}ms" for i in range(100, 0, -1)]
        s = M.analyze(lines).routes["GET", "/p"]
        self.assertEqual((s.p50, s.p95), (50.0, 95.0))
        lines = [f"2026-11-03T10:00:00Z GET /p 200 {i}ms" for i in range(1, 21)]
        s = M.analyze(lines).routes["GET", "/p"]
        self.assertEqual((s.p50, s.p95), (10.0, 19.0))
        s = M.analyze(["2026-11-03T10:00:00Z GET /one 200 7ms"]).routes["GET", "/one"]
        self.assertEqual((s.p50, s.p95), (7.0, 7.0))

    def test_top_with_tie_breaking(self):
        lines = [
            "2026-11-03T10:00:00Z GET /b 200 5ms",
            "2026-11-03T10:00:00Z GET /a 200 5ms",
            "2026-11-03T10:00:00Z POST /a 500 5ms",
            "2026-11-03T10:00:00Z GET /c 500 9ms",
            "2026-11-03T10:00:00Z GET /c 200 9ms",
        ]
        r = M.analyze(lines)
        keys = lambda stats: [(s.method, s.route) for s in stats]
        self.assertEqual(keys(r.top(1, by="count")), [("GET", "/c")])
        self.assertEqual(keys(r.top(4, by="p95")), [("GET", "/c"), ("GET", "/a"), ("POST", "/a"), ("GET", "/b")])
        self.assertEqual(keys(r.top(2, by="error_rate")), [("POST", "/a"), ("GET", "/c")])
        self.assertEqual(len(r.top(10)), 4)

    def test_top_unknown_metric(self):
        with self.assertRaises(ValueError):
            M.analyze(GOOD).top(3, by="p99")


if __name__ == "__main__":
    unittest.main()
