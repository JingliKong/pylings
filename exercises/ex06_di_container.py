"""Exercise 06 — A dependency-injection container with lifetimes.

Time box: 60 min.  Constructor injection driven by type hints, the way
FastAPI/Dishka/Lagom-style containers work.

    class Repo:
        def __init__(self, db: Database, clock: Clock): ...

    c = Container()
    c.register(Database, PostgresDatabase, lifetime="singleton")
    c.register(Clock, SystemClock)
    c.register(Session, lifetime="scoped")
    repo = c.resolve(Repo)               # Repo is auto-wired

    with c.scope() as scope:             # e.g. one per HTTP request
        s1 = scope.resolve(Session)
        assert scope.resolve(Session) is s1

API
---
``register(interface, implementation=None, *, factory=None, lifetime="transient")``
    ``implementation`` defaults to ``interface``.  ``factory`` is a callable
    whose own parameters are injected the same way.  Lifetimes:
    "transient" (new every time), "singleton" (one per container),
    "scoped" (one per scope).  Bad lifetime / both implementation and
    factory -> ``ValueError``.
``resolve(interface)`` / ``scope()`` / ``close()``; ``Scope`` has
``resolve()``, ``close()`` and is a context manager.

Requirements
------------
1. Parameters are injected by their type hints (``typing.get_type_hints``).
   A parameter with a default that cannot be resolved keeps its default
   (e.g. ``retries: int = 3``).  A required parameter that cannot be
   resolved -> ``ResolutionError`` naming it.
2. Unregistered *concrete* classes are auto-wired as transient.  Abstract
   classes, Protocols and builtins (``int``, ``str``…) are never auto-wired
   -> ``ResolutionError``.
3. Singletons: exactly one instance even when 16 threads resolve at once.
4. Scoped: one instance per scope.  Resolving a scoped service from the
   root container -> ``ResolutionError``.  A singleton (directly or
   transitively) depending on a scoped service -> ``ResolutionError``
   mentioning "scoped" (the "captive dependency" bug).
5. Cycles -> ``CircularDependencyError`` (subclass of ``ResolutionError``)
   whose message shows the cycle: ``"CycA -> CycB -> CycC -> CycA"``.
6. Leaving a scope calls ``close()`` (if present) on the scoped instances
   it created, in REVERSE creation order.  ``Container.close()`` does the
   same for singletons.

Discussion
----------
- Why is "singleton depends on scoped" a bug, and how do real frameworks
  detect it?
- What is the cost of holding one lock while constructing singletons?
  How could two singletons constructed in different threads deadlock with
  per-key locks?
- Service locator vs. dependency injection: why does it matter?
"""


class ResolutionError(LookupError):
    pass


class CircularDependencyError(ResolutionError):
    pass


class Container:
    def register(self, interface, implementation=None, *, factory=None, lifetime="transient"):
        raise NotImplementedError

    def resolve(self, interface):
        raise NotImplementedError

    def scope(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
