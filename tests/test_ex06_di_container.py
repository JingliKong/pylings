import abc
import threading
import time
import typing
import unittest

from _loader import load

M = load("ex06_di_container")
Container, ResolutionError, CircularDependencyError = (
    M.Container,
    M.ResolutionError,
    M.CircularDependencyError,
)


class Clock(abc.ABC):
    @abc.abstractmethod
    def now(self) -> float: ...


class FixedClock(Clock):
    def now(self) -> float:
        return 42.0


class Repo:
    def __init__(self, clock: Clock):
        self.clock = clock


class Service:
    def __init__(self, repo: Repo, clock: Clock, retries: int = 3):
        self.repo, self.clock, self.retries = repo, clock, retries


class NeedsName:
    def __init__(self, name: str):
        self.name = name


class Notifier(typing.Protocol):
    def send(self, msg: str) -> None: ...


class EmailNotifier:
    def send(self, msg: str) -> None:
        pass


class Config:
    def __init__(self, env: str):
        self.env = env


def make_repo(clock: Clock) -> Repo:
    repo = Repo(clock)
    repo.from_factory = True
    return repo


class CycA:
    def __init__(self, b: CycB): ...


class CycB:
    def __init__(self, c: CycC): ...


class CycC:
    def __init__(self, a: CycA): ...


CLOSED = []


class Conn:
    def close(self):
        CLOSED.append("conn")


class Session:
    def __init__(self, conn: Conn):
        self.conn = conn

    def close(self):
        CLOSED.append("session")


class Handler:
    def __init__(self, session: Session):
        self.session = session

    def close(self):
        CLOSED.append("handler")


class RequestCtx:
    pass


class Middle:
    def __init__(self, ctx: RequestCtx):
        self.ctx = ctx


class GlobalCache:
    def __init__(self, middle: Middle):
        self.middle = middle


class SlowSingleton:
    instances = 0

    def __init__(self):
        time.sleep(0.05)
        type(self).instances += 1


class TestResolve(unittest.TestCase):
    def setUp(self):
        CLOSED.clear()
        self.c = Container()
        self.c.register(Clock, FixedClock)

    def test_autowire_chain_and_defaults(self):
        svc = self.c.resolve(Service)
        self.assertIsInstance(svc.repo, Repo)
        self.assertIsInstance(svc.repo.clock, FixedClock)
        self.assertEqual(svc.retries, 3)

    def test_unregistered_abstract_fails(self):
        with self.assertRaises(ResolutionError):
            Container().resolve(Repo)

    def test_builtin_required_param_fails(self):
        with self.assertRaisesRegex(ResolutionError, "name|str"):
            self.c.resolve(NeedsName)

    def test_protocol(self):
        with self.assertRaises(ResolutionError):
            self.c.resolve(Notifier)
        self.c.register(Notifier, EmailNotifier)
        self.assertIsInstance(self.c.resolve(Notifier), EmailNotifier)

    def test_factory(self):
        self.c.register(Config, factory=lambda: Config("prod"))
        self.c.register(Repo, factory=make_repo)
        self.assertEqual(self.c.resolve(Config).env, "prod")
        self.assertTrue(self.c.resolve(Repo).from_factory)

    def test_bad_registration(self):
        with self.assertRaises(ValueError):
            self.c.register(Repo, lifetime="forever")
        with self.assertRaises(ValueError):
            self.c.register(Repo, Repo, factory=make_repo)

    def test_transient_vs_singleton(self):
        self.assertIsNot(self.c.resolve(Repo), self.c.resolve(Repo))
        self.c.register(Repo, lifetime="singleton")
        self.assertIs(self.c.resolve(Repo), self.c.resolve(Repo))

    def test_singleton_thread_safe(self):
        SlowSingleton.instances = 0
        self.c.register(SlowSingleton, lifetime="singleton")
        barrier = threading.Barrier(16)
        got = []
        lock = threading.Lock()

        def run():
            barrier.wait()
            inst = self.c.resolve(SlowSingleton)
            with lock:
                got.append(inst)

        threads = [threading.Thread(target=run) for _ in range(16)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(10)
        self.assertEqual(SlowSingleton.instances, 1)
        self.assertEqual(len({id(x) for x in got}), 1)

    def test_cycle_message(self):
        with self.assertRaises(CircularDependencyError) as ctx:
            self.c.resolve(CycA)
        self.assertIn("CycA -> CycB -> CycC -> CycA", str(ctx.exception))
        self.assertIsInstance(ctx.exception, ResolutionError)


class TestScopes(unittest.TestCase):
    def setUp(self):
        CLOSED.clear()
        self.c = Container()
        for cls in (Conn, Session, Handler):
            self.c.register(cls, lifetime="scoped")

    def test_scoped_identity(self):
        with self.c.scope() as s1, self.c.scope() as s2:
            self.assertIs(s1.resolve(Handler), s1.resolve(Handler))
            self.assertIs(s1.resolve(Handler).session, s1.resolve(Session))
            self.assertIsNot(s1.resolve(Handler), s2.resolve(Handler))

    def test_scoped_from_root_fails(self):
        with self.assertRaises(ResolutionError):
            self.c.resolve(Session)

    def test_close_order(self):
        with self.c.scope() as scope:
            scope.resolve(Handler)
        self.assertEqual(CLOSED, ["handler", "session", "conn"])

    def test_singletons_closed_by_container(self):
        c = Container()
        c.register(Conn, lifetime="singleton")
        c.register(Session, lifetime="singleton")
        c.resolve(Session)
        c.close()
        self.assertEqual(CLOSED, ["session", "conn"])

    def test_captive_dependency(self):
        self.c.register(RequestCtx, lifetime="scoped")
        self.c.register(GlobalCache, lifetime="singleton")  # -> Middle (transient) -> RequestCtx (scoped)
        with self.c.scope() as scope:
            with self.assertRaisesRegex(ResolutionError, "scoped"):
                scope.resolve(GlobalCache)

    def test_singleton_resolved_from_scope_is_shared(self):
        self.c.register(FixedClock, lifetime="singleton")
        with self.c.scope() as s1, self.c.scope() as s2:
            self.assertIs(s1.resolve(FixedClock), s2.resolve(FixedClock))
            self.assertIs(s1.resolve(FixedClock), self.c.resolve(FixedClock))


if __name__ == "__main__":
    unittest.main()
