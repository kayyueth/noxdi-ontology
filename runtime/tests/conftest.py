"""Shared paths and fixtures for the runtime test suite."""

from __future__ import annotations

import sys
from pathlib import Path

# The project root is the parent of the `runtime/` package.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = PROJECT_ROOT / "runtime"

# Ensure the project root is on sys.path so `import runtime.*` works when
# tests are invoked from any cwd.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
