import gc
import unittest

from _loader import load

EventBus = load("ex09_event_bus").EventBus


class TestEventBus(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus()
        self.calls = []

    def rec(self, name):
        def handler(event, payload):
            self.calls.append((name, event, payload))

        return handler

    def test_basic_emit_and_unsubscribe(self):
        unsub = self.bus.subscribe("a.b", self.rec("h"))
        self.assertEqual(self.bus.emit("a.b", 1), 1)
        unsub()
        unsub()  # idempotent
        self.assertEqual(self.bus.emit("a.b", 2), 0)
        self.assertEqual(self.calls, [("h", "a.b", 1)])

    def test_same_handler_twice_is_two_subscriptions(self):
        h = self.rec("h")
        u1 = self.bus.subscribe("x", h)
        self.bus.subscribe("x", h)
        self.assertEqual(self.bus.emit("x"), 2)
        u1()
        self.assertEqual(self.bus.emit("x"), 1)

    def test_wildcard_one_segment(self):
        self.bus.subscribe("order.*", self.rec("w"))
        self.bus.emit("order.paid")
        self.bus.emit("order")
        self.bus.emit("order.paid.late")
        self.bus.emit("user.paid")
        self.assertEqual([c[1] for c in self.calls], ["order.paid"])
        self.bus.subscribe("*.paid", self.rec("w2"))
        self.assertEqual(self.bus.handler_count("order.paid"), 2)

    def test_priority_then_subscription_order(self):
        self.bus.subscribe("e", self.rec("low1"))
        self.bus.subscribe("e", self.rec("high"), priority=10)
        self.bus.subscribe("e", self.rec("low2"))
        self.bus.subscribe("e", self.rec("neg"), priority=-1)
        self.bus.emit("e")
        self.assertEqual([c[0] for c in self.calls], ["high", "low1", "low2", "neg"])

    def test_failing_handlers_isolated_and_grouped(self):
        e1, e2 = ValueError("one"), KeyError("two")

        def bad1(e, p):
            raise e1

        def bad2(e, p):
            raise e2

        self.bus.subscribe("e", bad1)
        self.bus.subscribe("e", self.rec("ok"))
        self.bus.subscribe("e", bad2)
        with self.assertRaises(ExceptionGroup) as cm:
            self.bus.emit("e")
        self.assertEqual(list(cm.exception.exceptions), [e1, e2])
        self.assertEqual([c[0] for c in self.calls], ["ok"])

    def test_once(self):
        self.bus.subscribe("e", self.rec("once"), once=True)
        self.bus.emit("e")
        self.bus.emit("e")
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.bus.handler_count("e"), 0)

    def test_once_with_reentrant_emit(self):
        count = 0

        def handler(e, p):
            nonlocal count
            count += 1
            self.bus.emit("e")

        self.bus.subscribe("e", handler, once=True)
        self.bus.emit("e")
        self.assertEqual(count, 1)

    def test_subscribe_during_emit_not_called(self):
        def adder(e, p):
            self.bus.subscribe("e", self.rec("late"))

        self.bus.subscribe("e", adder)
        self.bus.emit("e")
        self.assertEqual(self.calls, [])
        self.bus.emit("e")
        self.assertEqual([c[0] for c in self.calls], ["late"])

    def test_unsubscribe_during_emit_not_called(self):
        unsubs = {}

        def killer(e, p):
            unsubs["victim"]()

        self.bus.subscribe("e", killer)
        unsubs["victim"] = self.bus.subscribe("e", self.rec("victim"))
        self.assertEqual(self.bus.emit("e"), 1)
        self.assertEqual(self.calls, [])

    def test_bound_methods_held_weakly(self):
        calls = self.calls

        class Listener:
            def on(self, e, p):
                calls.append("listener")

        obj = Listener()
        self.bus.subscribe("e", obj.on)
        self.bus.emit("e")
        self.assertEqual(calls, ["listener"])
        del obj
        gc.collect()
        self.assertEqual(self.bus.handler_count("e"), 0)
        self.assertEqual(self.bus.emit("e"), 0)
        self.assertEqual(calls, ["listener"])

    def test_lambdas_held_strongly(self):
        self.bus.subscribe("e", lambda e, p: self.calls.append("lambda"))
        gc.collect()
        self.bus.emit("e")
        self.assertEqual(self.calls, ["lambda"])

    def test_handler_count(self):
        self.bus.subscribe("a", self.rec("1"))
        self.bus.subscribe("*", self.rec("2"))
        self.bus.subscribe("b", self.rec("3"))
        self.assertEqual(self.bus.handler_count("a"), 2)
        self.assertEqual(self.bus.handler_count("c"), 1)


if __name__ == "__main__":
    unittest.main()
