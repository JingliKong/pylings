"""Solution: datetime1 — timezone-aware datetimes

Why: Naive datetimes have no timezone, so comparing or converting them
silently goes wrong. Adding hours shifts the INSTANT; `astimezone` keeps the
instant and changes the clock. Store UTC, convert for display.
"""
import unittest
from datetime import date, datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


UTC_PLUS_5 = timezone(timedelta(hours=5), "UTC+05")


def utc_now():
    """The current time as a timezone-AWARE datetime in UTC."""
    return datetime.now(timezone.utc)  # utcnow() is naive and deprecated since 3.12


def to_utc_plus_5(dt):
    """Convert an aware datetime to UTC+5: the same instant, a different clock."""
    return dt.astimezone(UTC_PLUS_5)


def parse_timestamp(text):
    """'2026-11-06T10:00:00Z' or '...+05:00' -> aware datetime in UTC.
    A timestamp without an offset is ambiguous -> ValueError."""
    dt = datetime.fromisoformat(text)  # understands 'Z' since 3.11
    if dt.tzinfo is None:
        raise ValueError(f"timestamp without timezone: {text!r}")
    return dt.astimezone(timezone.utc)


def days_until(deadline, today):
    """Whole days from `today` to `deadline` (both datetime.date). Negative if it's in the past."""
    return (deadline - today).days


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
