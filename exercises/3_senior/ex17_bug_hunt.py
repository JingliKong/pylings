"""Exercise 17 — Code review: find the bugs.

Time box: 25 min.  This is a (fictional) module from a production service.
It passed review and its unit tests.  Review it like an engineer:

- Find every bug.  There are at least 15 distinct issues, from "crashes
  under load" to "silently returns wrong data".
- For each: what goes wrong, under what conditions, and the fix.
- Rank them: which would you block the PR on?

Don't run it — read it.  Answer key: solutions/3_senior/ex17_bug_hunt.md
"""
import asyncio
import json
import logging
import threading
import time
from functools import lru_cache

log = logging.getLogger(__name__)


def create_connection():
    return object()


_conn = None
_conn_lock = threading.Lock()


def get_connection():
    global _conn
    if _conn is None:
        with _conn_lock:
            _conn = create_connection()
    return _conn


class RateLimiter:
    """Token bucket per key."""

    def __init__(self, per_second: int, buckets={}):
        self.per_second = per_second
        self.buckets = buckets
        self.lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        if key not in self.buckets:
            self.buckets[key] = [now, self.per_second]
        with self.lock:
            last, tokens = self.buckets[key]
            tokens = min(self.per_second, tokens + (now - last) * self.per_second)
            if tokens < 1:
                return False
            self.buckets[key] = [now, tokens - 1]
            return True


class User:
    def __init__(self, id, email, role="user", active=True):
        self.id = id
        self.email = email
        self.role = role
        self.active = active

    def __eq__(self, other):
        return self.id == other.id


def is_admin(user: User) -> bool:
    return user.role is "admin"


def unique_users(users: list[User]) -> list[User]:
    seen = set()
    out = []
    for u in users:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


class ProfileService:
    def __init__(self, db):
        self.db = db

    @lru_cache(maxsize=None)
    def get_profile(self, user_id: int) -> dict:
        return self.db.fetch(user_id)


def read_config(path: str) -> dict:
    f = open(path)
    try:
        return json.load(f)
    finally:
        return {}


def parse_ids(raw: str) -> list[int]:
    try:
        return [int(x) for x in raw.split(",")]
    except ValueError as e:
        pass
    log.warning("bad ids %r: %s", raw, e)
    return []


def build_handlers(event_names: list[str]):
    handlers = {}
    for name in event_names:
        handlers[name] = lambda payload: log.info("%s: %s", name, payload)
    return handlers


def retry(times=3, delay=0.5):
    def deco(fn):
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    time.sleep(delay * 2 ** attempt)
        return wrapper
    return deco


def weekly_report(all_users: list[User], send_report) -> None:
    active = (u for u in all_users if u.active)
    if any(active):
        send_report(list(active))


async def notify_all(users: list[User], send) -> None:
    for u in users:
        asyncio.create_task(send(u))


async def fetch_with_timeout(client, url: str):
    try:
        return await asyncio.wait_for(client.get(url), 5)
    except:
        log.exception("fetch failed")
        return None


class Registry:
    _handlers = []

    def add(self, handler):
        self._handlers.append(handler)

    def run_all(self, event):
        for h in self._handlers:
            h(event)
