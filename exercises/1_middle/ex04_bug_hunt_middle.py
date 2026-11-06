"""Exercise 04 — Code review: find the bugs (middle level).   Level: Middle

Time box: 20 min.  The warm-up version of Exercise 17.  This (fictional)
module from an online shop "works on my machine".  Review it:

- Find every bug.  There are at least 18 distinct issues: crashes, wrong
  results, security holes and "works until it doesn't".
- For each: what goes wrong, with an input that triggers it, and the fix.
- Which three would you block the PR on?

Don't run it — read it.  Answer key: solutions/1_middle/ex04_bug_hunt_middle.md
"""
import json
import os
import sqlite3
from datetime import datetime

DB_PATH = "orders.db"
UPLOAD_DIR = "/srv/uploads"
DEFAULT_SETTINGS = {"retries": 3, "timeout": 10, "features": {"beta": False}}


def get_db():
    return sqlite3.connect(DB_PATH)


class Order:
    items = []

    def __init__(self, order_id, customer, created_at=datetime.now()):
        self.order_id = order_id
        self.customer = customer
        self.created_at = created_at
        self.status = "new"

    def add_item(self, sku, price, qty=1):
        self.items.append({"sku": sku, "price": price, "qty": qty})

    def total(self):
        total = 0
        for item in self.items:
            total += item["price"] * item["qty"]
        return round(total, 2)

    def __repr__(self):
        return "Order(%s)" % self.order_id


def find_orders(customer):
    db = get_db()
    rows = db.execute(f"SELECT id, customer FROM orders WHERE customer = '{customer}'").fetchall()
    return [Order(r[0], r[1]) for r in rows]


def apply_discount(order, percent):
    assert 0 <= percent <= 100, "bad discount"
    return order.total() * (1 - percent / 100)


def remove_cancelled(orders):
    for o in orders:
        if o.status == "cancelled":
            orders.remove(o)
    return orders


def load_settings(path):
    settings = DEFAULT_SETTINGS.copy()
    with open(path) as f:
        user = json.load(f)
    for key, value in user.items():
        if key == "features":
            settings["features"].update(value)
        else:
            settings[key] = value
    return settings


def get_timeout(settings):
    return settings.get("timeout") or 30


def save_upload(filename, data: bytes):
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "w") as f:
        f.write(data)


def parse_quantity(text):
    try:
        return int(text)
    except:
        return 0


def latest_orders(orders, n=10):
    return orders.sort(key=lambda o: o.created_at, reverse=True)[:n]


def export_csv(orders):
    out = ""
    for o in orders:
        out += f"{o.order_id},{o.customer},{o.total()}\n"
    return out


def average_order_value(orders):
    return sum(o.total() for o in orders) / len(orders)


def is_recent(order):
    return (datetime.utcnow() - order.created_at).days < 7


def chunk(lst, size):
    return [lst[i:i + size] for i in range(0, len(lst) - size, size)]


def merge_tags(a, b):
    tags = a
    tags.extend(b)
    return list(set(tags))


class Cache:
    def __init__(self):
        self.data = {}

    def get_or_compute(self, key, fn):
        if self.data.get(key):
            return self.data[key]
        value = fn()
        self.data[key] = value
        return value
