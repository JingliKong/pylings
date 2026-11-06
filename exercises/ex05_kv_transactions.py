"""Exercise 05 — In-memory key-value store with nested transactions.
                                                           Level: Middle

Time box: 35 min.  A classic live-coding task.  The naive answer (copy the
whole dict on ``begin``) passes the functional tests and fails the
performance one — say why before you write it.

    db = KV()
    db.set("a", 10)
    db.begin()
    db.set("a", 20)
    db.count(20)        # -> 1
    db.rollback()
    db.get("a")         # -> 10

    with db.transaction():
        db.set("b", 1)  # committed when the block exits normally

Requirements
------------
1. ``set(key, value)``, ``get(key, default=None)``,
   ``delete(key) -> bool`` (False if it wasn't there), ``len(db)``.
2. ``count(value)`` -> number of keys currently holding ``value``.  Must be
   O(1), not a scan, and must reflect uncommitted changes.
3. ``begin()`` opens a (possibly nested) transaction.  Reads always see the
   latest writes, including uncommitted ones.
4. ``rollback()`` undoes everything since the matching ``begin()`` —
   innermost transaction only.  ``commit()`` closes the innermost
   transaction and keeps its changes; they become part of the enclosing
   transaction (so rolling back the outer one undoes them too).
5. ``commit()`` / ``rollback()`` with no open transaction -> ``NoTransaction``
   (a ``RuntimeError`` subclass).
6. ``db.transaction()`` is a context manager: commit on normal exit,
   rollback on exception, and the exception propagates.  It nests.
7. ``begin()`` must cost O(1), and a transaction's memory must be
   proportional to the number of keys it touched — not to the size of the
   store.
8. ``db.depth`` -> number of open transactions.

Discussion
----------
- Two designs: (a) keep per-transaction "write sets" and look up through
  the stack on ``get``; (b) apply writes immediately and keep an *undo log*.
  Trade-offs for reads, commits, rollbacks?  Which one does a real database
  look more like?
- How do you represent "deleted inside a transaction" in design (a)?
- What would it take to support concurrent transactions from different
  threads with snapshot isolation?
"""


class NoTransaction(RuntimeError):
    pass


class KV:
    def __init__(self):
        raise NotImplementedError

    def get(self, key, default=None):
        raise NotImplementedError

    def set(self, key, value):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    def count(self, value):
        raise NotImplementedError

    def begin(self):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError

    def transaction(self):
        raise NotImplementedError

    @property
    def depth(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError
