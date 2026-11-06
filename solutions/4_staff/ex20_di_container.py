"""Reference solution for exercises/4_staff/ex20_di_container.py."""
import inspect
import threading
import typing
from dataclasses import dataclass
from typing import Any, Callable

LIFETIMES = frozenset({"transient", "scoped", "singleton"})


class ResolutionError(LookupError):
    pass


class CircularDependencyError(ResolutionError):
    pass


@dataclass(frozen=True, slots=True)
class _Registration:
    provider: Callable[..., Any]
    lifetime: str


def _name(tp):
    return getattr(tp, "__qualname__", repr(tp))


def _autowirable(tp):
    return (
        isinstance(tp, type)
        and tp.__module__ != "builtins"
        and not inspect.isabstract(tp)
        and not getattr(tp, "_is_protocol", False)
    )


def _parameters(provider):
    """Yield (name, parameter, type hint or None) for each injectable parameter."""
    target = provider.__init__ if isinstance(provider, type) else provider
    hints = {} if target is object.__init__ else typing.get_type_hints(target)
    for name, param in inspect.signature(provider).parameters.items():
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
        if param.kind is param.POSITIONAL_ONLY:
            raise ResolutionError(f"{_name(provider)}: positional-only parameter {name!r} is not injectable")
        yield name, param, hints.get(name)


def _close_all(instances):
    errors = []
    for instance in reversed(instances):
        close = getattr(instance, "close", None)
        if callable(close):
            try:
                close()
            except Exception as e:  # keep closing the rest
                errors.append(e)
    if errors:
        raise ExceptionGroup("errors while closing", errors)


class Container:
    def __init__(self):
        self._registrations = {}
        self._singletons = {}
        self._owned = []  # singletons in creation order, for close()
        # One re-entrant lock for all singleton construction: simple and
        # deadlock-free (per-key locks can deadlock when two singletons are
        # built in opposite orders on two threads). Cost: singleton
        # construction is serialised — fine, it happens once.
        self._lock = threading.RLock()

    def register(self, interface, implementation=None, *, factory=None, lifetime="transient"):
        if lifetime not in LIFETIMES:
            raise ValueError(f"unknown lifetime {lifetime!r}; expected one of {sorted(LIFETIMES)}")
        if implementation is not None and factory is not None:
            raise ValueError("pass either implementation or factory, not both")
        provider = factory or implementation or interface
        self._registrations[interface] = _Registration(provider, lifetime)
        return self

    def resolve(self, interface):
        return self._resolve(interface, None, (), False)

    def scope(self):
        return Scope(self)

    def close(self):
        with self._lock:
            owned, self._owned = self._owned, []
            self._singletons.clear()
        _close_all(owned)

    def _registration(self, interface):
        registration = self._registrations.get(interface)
        if registration is None and _autowirable(interface):
            registration = _Registration(interface, "transient")
        return registration

    def _resolve(self, interface, scope, path, in_singleton):
        if interface in path:
            cycle = path[path.index(interface):] + (interface,)
            raise CircularDependencyError("circular dependency: " + " -> ".join(map(_name, cycle)))
        registration = self._registration(interface)
        if registration is None:
            needed_by = f" (needed by {_name(path[-1])})" if path else ""
            raise ResolutionError(f"no registration for {_name(interface)}{needed_by}")
        path = path + (interface,)

        if registration.lifetime == "singleton":
            with self._lock:
                if interface in self._singletons:
                    return self._singletons[interface]
                # Singleton dependencies are built without the scope: a
                # scoped dependency would otherwise be captured forever.
                instance = self._build(registration.provider, None, path, True)
                self._singletons[interface] = instance
                self._owned.append(instance)
                return instance

        if registration.lifetime == "scoped":
            if scope is None:
                chain = " -> ".join(map(_name, path))
                if in_singleton:
                    raise ResolutionError(
                        f"captive dependency: scoped {_name(interface)} cannot be injected "
                        f"into a singleton ({chain})"
                    )
                raise ResolutionError(f"scoped {_name(interface)} must be resolved from a scope")
            if interface in scope._instances:
                return scope._instances[interface]
            instance = self._build(registration.provider, scope, path, in_singleton)
            scope._instances[interface] = instance
            scope._owned.append(instance)
            return instance

        return self._build(registration.provider, scope, path, in_singleton)

    def _build(self, provider, scope, path, in_singleton):
        kwargs = {}
        for name, param, hint in _parameters(provider):
            has_default = param.default is not param.empty
            if hint is None or self._registration(hint) is None:
                if has_default:
                    continue
                what = "no type hint" if hint is None else f"cannot resolve {_name(hint)}"
                raise ResolutionError(f"{_name(provider)}: parameter {name!r}: {what}")
            kwargs[name] = self._resolve(hint, scope, path, in_singleton)
        return provider(**kwargs)


class Scope:
    """One unit of work (e.g. a request). Not meant to be shared across threads."""

    def __init__(self, container):
        self._container = container
        self._instances = {}
        self._owned = []
        self._closed = False

    def resolve(self, interface):
        if self._closed:
            raise RuntimeError("scope is closed")
        return self._container._resolve(interface, self, (), False)

    def close(self):
        if not self._closed:
            self._closed = True
            owned, self._owned = self._owned, []
            self._instances.clear()
            _close_all(owned)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()
