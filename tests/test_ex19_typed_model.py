import inspect
import unittest
from typing import Any, ClassVar

from _loader import load

M = load("ex19_typed_model")
Model, field, Field = M.Model, M.field, M.Field


# Module-level so that forward references resolve through module globals.
class Address(Model):
    city: str
    zip: str | None = None


class User(Model):
    id: int
    name: str
    tags: list[str] = field(default_factory=list)
    address: Address | None = None
    scores: dict[str, float] = field(default_factory=dict)
    extra: Any = None
    registry: ClassVar[int] = 0


class Node(Model):
    value: int
    children: list[Node] = field(default_factory=list)


class Author(Model):
    name: str
    books: list[Book] = field(default_factory=list)


class Book(Model):
    title: str
    author: Author | None = None


class Base(Model):
    a: int
    b: int = 1


class Child(Base):
    c: int = 2
    b: int = 10


class Point(Model, frozen=True):
    x: float
    y: float


class Point3D(Point):
    z: float = 0.0


class TestConstruction(unittest.TestCase):
    def test_basic(self):
        u = User(id=1, name="ann")
        self.assertEqual((u.id, u.name, u.tags, u.address), (1, "ann", [], None))

    def test_missing_required(self):
        with self.assertRaisesRegex(TypeError, "name"):
            User(id=1)

    def test_unknown_field(self):
        with self.assertRaisesRegex(TypeError, "nope"):
            User(id=1, name="a", nope=2)

    def test_positional_rejected(self):
        with self.assertRaises(TypeError):
            User(1, "a")

    def test_default_factory_is_fresh(self):
        a, b = User(id=1, name="a"), User(id=2, name="b")
        a.tags.append("x")
        self.assertEqual(b.tags, [])

    def test_mutable_default_rejected_at_class_creation(self):
        with self.assertRaises(TypeError):
            class Bad(Model):
                items: list[int] = []

    def test_signature(self):
        sig = inspect.signature(User)
        self.assertEqual(list(sig.parameters), ["id", "name", "tags", "address", "scores", "extra"])
        self.assertTrue(all(p.kind is p.KEYWORD_ONLY for p in sig.parameters.values()))

    def test_classvar_is_not_a_field(self):
        self.assertEqual(User.registry, 0)
        params = inspect.signature(User).parameters
        self.assertIn("id", params)
        self.assertNotIn("registry", params)
        with self.assertRaises(TypeError):
            User(id=1, name="a", registry=5)

    def test_class_access_returns_descriptor(self):
        self.assertIsInstance(User.name, Field)
        self.assertEqual(User.name.name, "name")


class TestValidation(unittest.TestCase):
    def test_scalar_types(self):
        with self.assertRaisesRegex(TypeError, "id"):
            User(id="1", name="a")
        with self.assertRaises(TypeError):
            User(id=True, name="a")  # bool is not an int here

    def test_int_accepted_for_float_but_not_bool(self):
        self.assertEqual(Point(x=1, y=2.5).x, 1)
        with self.assertRaises(TypeError):
            Point(x=True, y=1.0)

    def test_list_path_in_message(self):
        with self.assertRaisesRegex(TypeError, r"tags\[1\]: expected str, got int"):
            User(id=1, name="a", tags=["ok", 2])

    def test_dict(self):
        User(id=1, name="a", scores={"x": 1, "y": 2.5})
        with self.assertRaises(TypeError):
            User(id=1, name="a", scores={"x": "high"})
        with self.assertRaises(TypeError):
            User(id=1, name="a", scores={1: 1.0})

    def test_optional_and_nested_model(self):
        User(id=1, name="a", address=Address(city="Tashkent"))
        with self.assertRaises(TypeError):
            User(id=1, name="a", address="Tashkent")

    def test_any(self):
        User(id=1, name="a", extra=object())

    def test_validation_on_assignment_keeps_old_value(self):
        u = User(id=1, name="a", tags=["x"])
        with self.assertRaises(TypeError):
            u.tags = "abc"
        self.assertEqual(u.tags, ["x"])
        u.tags = ["y"]
        self.assertEqual(u.tags, ["y"])

    def test_self_reference(self):
        tree = Node(value=1, children=[Node(value=2), Node(value=3)])
        self.assertEqual([c.value for c in tree.children], [2, 3])
        with self.assertRaisesRegex(TypeError, r"children\[0\]"):
            Node(value=1, children=[1])

    def test_mutual_reference(self):
        author = Author(name="Navoi")
        book = Book(title="Khamsa", author=author)
        author.books = [book]
        with self.assertRaises(TypeError):
            author.books = [author]


class TestInheritance(unittest.TestCase):
    def test_field_order_and_override(self):
        self.assertEqual(list(inspect.signature(Child).parameters), ["a", "b", "c"])
        child = Child(a=0)
        self.assertEqual((child.a, child.b, child.c), (0, 10, 2))
        self.assertEqual(Base(a=0).b, 1)


class TestFrozenEqRepr(unittest.TestCase):
    def test_frozen(self):
        p = Point(x=1, y=2)
        with self.assertRaises(AttributeError):
            p.x = 3
        with self.assertRaises(AttributeError):
            p.other = 3
        with self.assertRaises(AttributeError):
            del p.x
        self.assertEqual(p.x, 1)

    def test_frozen_inherited(self):
        p = Point3D(x=1, y=2)
        with self.assertRaises(AttributeError):
            p.z = 1.0

    def test_hashing(self):
        self.assertEqual(len({Point(x=1, y=2), Point(x=1, y=2)}), 1)
        with self.assertRaises(TypeError):
            hash(User(id=1, name="a"))

    def test_eq(self):
        self.assertEqual(User(id=1, name="a"), User(id=1, name="a"))
        self.assertNotEqual(User(id=1, name="a"), User(id=2, name="a"))
        self.assertNotEqual(Base(a=1, b=10), Child(a=1))

    def test_repr(self):
        self.assertEqual(repr(Point(x=1, y=2)), "Point(x=1, y=2)")
        self.assertEqual(repr(Address(city="X")), "Address(city='X', zip=None)")


if __name__ == "__main__":
    unittest.main()
