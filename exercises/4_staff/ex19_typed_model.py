"""Exercise 19 — A mini pydantic/attrs: descriptors, __init_subclass__, typing.

Time box: 60–75 min.  Requires Python 3.14 (PEP 649 deferred annotations).
No dataclasses, attrs or pydantic.

    class Address(Model):
        city: str
        zip: str | None = None

    class User(Model):
        id: int
        name: str
        tags: list[str] = field(default_factory=list)
        address: Address | None = None
        registry: ClassVar[int] = 0        # not a field

    u = User(id=1, name="ann")
    u.tags = ["a", 2]   # TypeError: tags[1]: expected str, got int

Requirements
------------
1. Fields come from the class's own annotations (``ClassVar`` excluded) plus
   inherited fields.  Parent fields come first; a subclass that re-annotates
   a field overrides its default but keeps its position.
2. ``__init__`` takes keyword-only arguments.  Missing required field or
   unknown keyword -> ``TypeError`` naming the field.
   ``inspect.signature(User)`` shows the fields as keyword-only parameters.
3. Each field is a **data descriptor** (``Field``); ``User.name`` returns the
   ``Field`` object, which knows its ``.name``.
4. Validate on ``__init__`` AND on attribute assignment.  A failed
   assignment leaves the old value in place.  Supported annotations:
   ``int``, ``float``, ``str``, ``bool``, ``None``, ``X | Y``/``Optional``,
   ``list[T]``, ``dict[K, V]``, ``Any``, other ``Model`` subclasses.
   - ``bool`` is NOT accepted as ``int``; ``int`` IS accepted as ``float``.
   - Error messages carry a path: ``"tags[1]: expected str, got int"``.
5. Types must be resolved LAZILY (at first validation, not at class
   creation) so that self-referential and mutually-referential models work::

       class Node(Model):
           children: list[Node] = field(default_factory=list)

       class Author(Model):
           books: list[Book] = field(default_factory=list)
       class Book(Model):           # defined after Author
           author: Author | None = None

6. A bare mutable default (``list``, ``dict``, ``set``) -> ``TypeError`` at
   class creation.  ``field(default_factory=...)`` gives a fresh value per
   instance.
7. ``class Point(Model, frozen=True)``: any attribute assignment or deletion
   raises ``AttributeError``; frozen instances are hashable.  Non-frozen
   instances are unhashable.  Subclasses inherit frozen-ness.
8. ``__eq__`` (same class and same field values) and ``__repr__``
   (``Point(x=1, y=2)``).

Discussion
----------
- Why must ``Field`` be a *data* descriptor?  What would break with only
  ``__get__``?
- When exactly does ``__set_name__`` run, and why doesn't ``setattr(cls,
  name, Field())`` after class creation trigger it?
- What changed for libraries like this one in 3.14 (PEP 649), and why
  can't you call ``typing.get_type_hints`` inside ``__init_subclass__``?
"""
from typing import ClassVar

MISSING = object()


class Field:
    def __init__(self, default=MISSING, default_factory=MISSING):
        self.default = default
        self.default_factory = default_factory


def field(*, default=MISSING, default_factory=MISSING):
    return Field(default, default_factory)


class Model:
    def __init_subclass__(cls, *, frozen=None, **kwargs):
        super().__init_subclass__(**kwargs)
        # TODO

    def __init__(self, **kwargs):
        raise NotImplementedError
