"""Pick the implementation under test.

Default: your code in exercises/.  Set SOLUTIONS=1 to run against solutions/.
"""
import importlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PACKAGE = "solutions" if os.environ.get("SOLUTIONS") == "1" else "exercises"


def load(name: str):
    return importlib.import_module(f"{PACKAGE}.{name}")
