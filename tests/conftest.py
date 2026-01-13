"""Pytest configuration helpers for the fleet simulator tests."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the repository root (which contains the ``ship_combat`` package) is always
# available on ``sys.path`` even when pytest executes with ``tests`` as the working
# directory. This mirrors the manual ``PYTHONPATH=.`` workaround used previously but
# makes the behavior automatic for local and CI runs that simply execute ``pytest``.
REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT_STR = str(REPO_ROOT)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)
