#!/usr/bin/env python3
"""Convenience entry point to run the in-repo pytest suite."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


def main() -> int:
    extra_opts = os.environ.get("PYTEST_ADDOPTS", "").strip()
    filtered_opts = "-p no:pytest_sugar" if not extra_opts else f"-p no:pytest_sugar {extra_opts}"
    os.environ["PYTEST_ADDOPTS"] = filtered_opts

    repo_root = Path(__file__).resolve().parent
    tests_dir = repo_root / "kuksa-syncer" / "tests"
    default_args = [str(tests_dir)]
    return pytest.main(default_args + sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
