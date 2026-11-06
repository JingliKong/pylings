"""Pick the implementation under test.

Default: your code in exercises/.  Set SOLUTIONS=1 to run against solutions/.
Exercises live in level folders (exercises/1_middle/ex05_....py), so modules
are found by file name and loaded from their path.
"""
import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / ("solutions" if os.environ.get("SOLUTIONS") == "1" else "exercises")


def load(name: str):
    if name in sys.modules:
        return sys.modules[name]
    matches = sorted(BASE.rglob(f"{name}.py"))
    if len(matches) != 1:
        raise ImportError(f"expected exactly one {name}.py under {BASE}, found {len(matches)}")
    spec = importlib.util.spec_from_file_location(name, matches[0])
    module = importlib.util.module_from_spec(spec)
    # Register before executing: typing.get_type_hints, dataclasses and pickle
    # look the module up in sys.modules by name.
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        del sys.modules[name]
        raise
    return module
