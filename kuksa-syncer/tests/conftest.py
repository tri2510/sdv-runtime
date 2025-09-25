from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
KUKSA_SYNCER_DIR = REPO_ROOT / "kuksa-syncer"
CPP_PROJECTS_DIR = REPO_ROOT / "cpp-projects"

# Ensure project modules are importable when tests run via `python -m pytest`
if str(KUKSA_SYNCER_DIR) not in sys.path:
    sys.path.insert(0, str(KUKSA_SYNCER_DIR))


@pytest.fixture(scope="session")
def structured_project_dir() -> Path:
    """Path to the cmake-structured sample used across tests."""
    return CPP_PROJECTS_DIR / "02-cmake-structured"


@pytest.fixture(scope="session")
def structured_project_binary(structured_project_dir: Path) -> Path:
    """Ensure the cmake-structured sample is built and return the binary path."""
    build_dir = structured_project_dir / "build"
    binary = build_dir / "vehicle_systems"

    if not binary.exists():
        build_script = structured_project_dir / "build.sh"
        if not build_script.exists():
            raise FileNotFoundError(f"Missing build script for {structured_project_dir}")

        # CMake sample is tiny; enforce a tight timeout to avoid hanging builds.
        subprocess.run(
            ["bash", str(build_script.name)],
            cwd=structured_project_dir,
            check=True,
            timeout=90,
        )

    return binary


@pytest.fixture(autouse=True)
def quiet_cpp_trace_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep ptrace logs quieter during tests unless explicitly overridden."""
    monkeypatch.setenv("CPP_TRACE_VERBOSE", os.getenv("CPP_TRACE_VERBOSE", "0"))
