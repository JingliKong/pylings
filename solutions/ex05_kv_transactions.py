"""Reference solution for exercises/ex05_kv_transactions.py.

Design: writes go straight to ``_data`` (reads are a plain dict lookup);
each open transaction keeps an *undo log*: for every key it touched, the
value that key had when the transaction first touched it (or ``_MISSING``).

- rollback: restore those originals -> O(keys touched).
- commit:   merge the undo log into the parent's, keeping the parent's
            entry when both have one (the parent's original is older).
- count:    a Counter over current values, updated on every write.
"""
import contextlib
from collections import Counter

_MISSING = object()


class NoTransaction(RuntimeError):
    pass


class KV:
    def __init__(self):
        self._data = {}
        self._counts = Counter()
        self._undo = []  # stack of {key: original value or _MISSING}

    # -- low-level write: keeps _counts in sync ----------------------------
    def _write(self, key, value):
        old = self._data.get(key, _MISSING)
        if old is not _MISSING:
            self._decr(old)
        if value is _MISSING:
            self._data.pop(key, None)
        else:
            self._data[key] = value
            self._counts[value] += 1

    def _decr(self, value):
        self._counts[value] -= 1
        if not self._counts[value]:
            del self._counts[value]  # don't let the Counter grow forever

    def _remember(self, key):
        if self._undo:
            self._undo[-1].setdefault(key, self._data.get(key, _MISSING))

    # -- public API -------------------------------------------------------------
    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._remember(key)
        self._write(key, value)

    def delete(self, key):
        if key not in self._data:
            return False
        self._remember(key)
        self._write(key, _MISSING)
        return True

    def count(self, value):
        return self._counts.get(value, 0)

    def begin(self):
        self._undo.append({})

    def commit(self):
        if not self._undo:
            raise NoTransaction("commit without begin")
        log = self._undo.pop()
        if self._undo:
            parent = self._undo[-1]
            for key, original in log.items():
                parent.setdefault(key, original)

    def rollback(self):
        if not self._undo:
            raise NoTransaction("rollback without begin")
        for key, original in self._undo.pop().items():
            self._write(key, original)

    @contextlib.contextmanager
    def transaction(self):
        self.begin()
        try:
            yield self
        except BaseException:
            self.rollback()  # BaseException: KeyboardInterrupt mid-block must not leave it half-applied
            raise
        else:
            self.commit()

    @property
    def depth(self):
        return len(self._undo)

    def __len__(self):
        return len(self._data)
