"""Warm-up datetime1: timezone-aware datetimes

Fix the functions so all datetimes are timezone-aware.

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/09_stdlib/datetime1.py
"""
import unittest
from datetime import date, datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


UTC_PLUS_5 = timezone(timedelta(hours=5), "UTC+05")


def utc_now():
    """The current time as a timezone-AWARE datetime in UTC."""
    return datetime.utcnow()


def to_utc_plus_5(dt):
    """Convert an aware datetime to UTC+5: the same instant, a different clock."""
    return dt + timedelta(hours=5)


def parse_timestamp(text):
    """'2026-11-06T10:00:00Z' or '...+05:00' -> aware datetime in UTC.
    A timestamp without an offset is ambiguous -> ValueError."""
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")


def days_until(deadline, today):
    """Whole days from `today` to `deadline` (both datetime.date). Negative if it's in the past."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_utc_now_is_aware(self):
        now = utc_now()
        self.assertIsNotNone(now.tzinfo)
        self.assertEqual(now.utcoffset(), timedelta(0))
        self.assertLess(abs((now - datetime.now(timezone.utc)).total_seconds()), 5)

    def test_to_utc_plus_5(self):
        dt = datetime(2026, 11, 6, 10, 0, tzinfo=timezone.utc)
        local = to_utc_plus_5(dt)
        self.assertEqual(local.hour, 15)
        self.assertEqual(local.utcoffset(), timedelta(hours=5))
        self.assertEqual(local, dt)  # same instant

    def test_parse_timestamp(self):
        expected = datetime(2026, 11, 6, 10, tzinfo=timezone.utc)
        self.assertEqual(parse_timestamp("2026-11-06T10:00:00Z"), expected)
        self.assertEqual(parse_timestamp("2026-11-06T15:00:00+05:00"), expected)
        self.assertEqual(parse_timestamp("2026-11-06T15:00:00+05:00").utcoffset(), timedelta(0))
        with self.assertRaises(ValueError):
            parse_timestamp("2026-11-06T10:00:00")

    def test_days_until(self):
        self.assertEqual(days_until(date(2026, 12, 31), date(2026, 11, 6)), 55)
        self.assertEqual(days_until(date(2026, 11, 1), date(2026, 11, 6)), -5)


if __name__ == "__main__":
    unittest.main()
