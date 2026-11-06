"""Reference solution for exercises/ex19_typed_model.py."""
import inspect
import reprlib
import types
import typing
from typing import Any, ClassVar, Union, get_args, get_origin

try:
    import annotationlib
except ImportError:  # < 3.14
    annotationlib = None


class _Missing:
    def __repr__(self):
        return "MISSING"


class _FactoryDefault:
    def __repr__(self):
        return "<factory>"


MISSING = _Missing()
_FACTORY = _FactoryDefault()
_MUTABLE_DEFAULTS = (list, dict, set, bytearray)


class Field:
    """Data descriptor: __set__ makes it win over the instance __dict__."""

    __slots__ = ("default", "default_factory", "name", "owner")

    def __init__(self, default=MISSING, default_factory=MISSING):
        if default is not MISSING and default_factory is not MISSING:
            raise ValueError("cannot set both default and default_factory")
        self.default = default
        self.default_factory = default_factory
        self.name = None
        self.owner = None

    def __set_name__(self, owner, name):
        self.owner, self.name = owner, name

    @property
    def type(self):
        return self.owner._resolved_types()[self.name]

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return obj.__dict__[self.name]
        except KeyError:
            raise AttributeError(self.name) from None

    def __set__(self, obj, value):
        self._store(obj, value)

    def __delete__(self, obj):
        raise AttributeError(f"cannot delete field {self.name!r}")

    def _store(self, obj, value):
        _check(value, self.type, self.name)  # validate before mutating
        obj.__dict__[self.name] = value

    def __repr__(self):
        return f"Field(name={self.name!r}, default={self.default!r})"


def field(*, default=MISSING, default_factory=MISSING):
    return Field(default, default_factory)


def _own_annotations(cls):
    # FORWARDREF: get the names without evaluating types that may not exist
    # yet (e.g. `books: list[Book]` while Book is still undefined).
    if annotationlib is not None:
        return annotationlib.get_annotations(cls, format=annotationlib.Format.FORWARDREF)
    return dict(cls.__dict__.get("__annotations__", {}))


def _is_classvar(annotation):
    return annotation is ClassVar or get_origin(annotation) is ClassVar


def _typename(tp):
    if isinstance(tp, type) and not get_args(tp):
        return tp.__name__
    return repr(tp).replace("typing.", "")


def _fail(path, tp, value):
    raise TypeError(f"{path}: expected {_typename(tp)}, got {type(value).__name__}")


def _check(value, tp, path):
    if tp is Any:
        return
    if tp is None or tp is type(None):
        if value is not None:
            _fail(path, tp, value)
        return
    origin = get_origin(tp)
    if origin is Union or origin is types.UnionType:
        for arg in get_args(tp):
            try:
                _check(value, arg, path)
                return
            except TypeError:
                pass
        _fail(path, tp, value)
    if origin is list:
        if not isinstance(value, list):
            _fail(path, tp, value)
        (item_tp,) = get_args(tp) or (Any,)
        for i, item in enumerate(value):
            _check(item, item_tp, f"{path}[{i}]")
        return
    if origin is dict:
        if not isinstance(value, dict):
            _fail(path, tp, value)
        key_tp, val_tp = get_args(tp) or (Any, Any)
        for k, v in value.items():
            _check(k, key_tp, f"{path}.<key {k!r}>")
            _check(v, val_tp, f"{path}[{k!r}]")
        return
    if origin is not None:
        raise TypeError(f"{path}: unsupported annotation {tp!r}")
    if tp is int:
        if isinstance(value, bool) or not isinstance(value, int):
            _fail(path, tp, value)
        return
    if tp is float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            _fail(path, tp, value)
        return
    if isinstance(tp, type):
        if not isinstance(value, tp):
            _fail(path, tp, value)
        return
    raise TypeError(f"{path}: unsupported annotation {tp!r}")


class Model:
    __model_fields__: ClassVar[dict[str, Field]] = {}
    __model_frozen__: ClassVar[bool] = False

    def __init_subclass__(cls, *, frozen=None, **kwargs):
        super().__init_subclass__(**kwargs)
        parent_frozen = any(getattr(base, "__model_frozen__", False) for base in cls.__mro__[1:])
        if frozen is None:
            frozen = parent_frozen
        elif parent_frozen and not frozen:
            raise TypeError(f"{cls.__name__}: cannot un-freeze a frozen parent")
        cls.__model_frozen__ = frozen

        fields = {}
        for base in reversed(cls.__mro__[1:]):
            fields.update(base.__dict__.get("__own_fields__", {}))

        own = {}
        for name, annotation in _own_annotations(cls).items():
            if _is_classvar(annotation):
                continue
            value = cls.__dict__.get(name, MISSING)
            if isinstance(value, Field):
                f = value  # __set_name__ already ran during class creation
            else:
                f = Field(default=value)
                setattr(cls, name, f)
                f.__set_name__(cls, name)  # setattr after creation doesn't call it
            if isinstance(f.default, _MUTABLE_DEFAULTS):
                raise TypeError(
                    f"{cls.__name__}.{name}: mutable default {type(f.default).__name__} "
                    f"is shared between instances; use field(default_factory=...)"
                )
            own[name] = f
        cls.__own_fields__ = own
        fields.update(own)  # an override keeps the parent's position
        cls.__model_fields__ = fields

        cls.__hash__ = Model._frozen_hash if frozen else None
        cls.__signature__ = inspect.Signature(
            [
                inspect.Parameter(
                    name,
                    inspect.Parameter.KEYWORD_ONLY,
                    default=(
                        f.default if f.default is not MISSING
                        else _FACTORY if f.default_factory is not MISSING
                        else inspect.Parameter.empty
                    ),
                )
                for name, f in fields.items()
            ]
        )

    @classmethod
    def _resolved_types(cls):
        # Lazy: resolved on first validation, when forward references exist.
        resolved = cls.__dict__.get("__model_types__")
        if resolved is None:
            resolved = typing.get_type_hints(cls, localns={cls.__name__: cls})
            cls.__model_types__ = resolved
        return resolved

    def __init__(self, **kwargs):
        cls = type(self)
        fields = cls.__model_fields__
        unknown = kwargs.keys() - fields.keys()
        if unknown:
            raise TypeError(f"{cls.__name__}() got unexpected field(s): {', '.join(sorted(unknown))}")
        for name, f in fields.items():
            if name in kwargs:
                value = kwargs[name]
            elif f.default_factory is not MISSING:
                value = f.default_factory()
            elif f.default is not MISSING:
                value = f.default
            else:
                raise TypeError(f"{cls.__name__}() missing required field {name!r}")
            f._store(self, value)  # bypasses __setattr__, so frozen models can init

    def __setattr__(self, name, value):
        if type(self).__model_frozen__:
            raise AttributeError(f"{type(self).__name__} is frozen; cannot set {name!r}")
        super().__setattr__(name, value)

    def __delattr__(self, name):
        if type(self).__model_frozen__:
            raise AttributeError(f"{type(self).__name__} is frozen; cannot delete {name!r}")
        super().__delattr__(name)

    def _values(self):
        return tuple(getattr(self, name) for name in type(self).__model_fields__)

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return self._values() == other._values()

    def _frozen_hash(self):
        return hash((type(self), self._values()))

    @reprlib.recursive_repr()
    def __repr__(self):
        body = ", ".join(f"{name}={getattr(self, name)!r}" for name in type(self).__model_fields__)
        return f"{type(self).__name__}({body})"
