from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
KUKSA_SYNCER_DIR = REPO_ROOT / "kuksa-syncer"
CPP_PROJECTS_DIR = REPO_ROOT / "cpp-projects"

# Ensure project modules are importable when tests run via `python -m pytest`
if str(KUKSA_SYNCER_DIR) not in sys.path:
    sys.path.insert(0, str(KUKSA_SYNCER_DIR))


@dataclass(frozen=True)
class SampleProject:
    key: str
    project_dir: Path
    binary_relative: Path
    build_steps: List[List[str]]
    project_type: str
    expected_vars: List[str]


SAMPLE_PROJECTS: Dict[str, SampleProject] = {
    "01-basic-types": SampleProject(
        key="01-basic-types",
        project_dir=CPP_PROJECTS_DIR / "01-basic-types",
        binary_relative=Path("basic_types_monitor"),
        build_steps=[["bash", "build.sh"]],
        project_type="gcc",
        expected_vars=["steering_angle", "battery_level", "engine_rpm"],
    ),
    "02-cmake-structured": SampleProject(
        key="02-cmake-structured",
        project_dir=CPP_PROJECTS_DIR / "02-cmake-structured",
        binary_relative=Path("build") / "vehicle_systems",
        build_steps=[["bash", "build.sh"]],
        project_type="cmake",
        expected_vars=["actual_speed", "battery_voltage", "engine_rpm"],
    ),
    "03-makefile-build": SampleProject(
        key="03-makefile-build",
        project_dir=CPP_PROJECTS_DIR / "03-makefile-build",
        binary_relative=Path("adas_monitor"),
        build_steps=[["make", "clean"], ["make"]],
        project_type="make",
        expected_vars=["front_distance", "closing_velocity", "time_to_collision"],
    ),
    "04-complex-structures": SampleProject(
        key="04-complex-structures",
        project_dir=CPP_PROJECTS_DIR / "04-complex-structures",
        binary_relative=Path("complex_vehicle_system"),
        build_steps=[["bash", "build.sh"]],
        project_type="gcc",
        expected_vars=["system_uptime", "total_errors", "engine_rpm"],
    ),
    "05-embedded-style": SampleProject(
        key="05-embedded-style",
        project_dir=CPP_PROJECTS_DIR / "05-embedded-style",
        binary_relative=Path("embedded_ecu_system"),
        build_steps=[["bash", "build.sh"]],
        project_type="gcc",
        expected_vars=["status_reg1_raw", "can_tx_counter", "active_dtc_count"],
    ),
    "06-matlab-style": SampleProject(
        key="06-matlab-style",
        project_dir=CPP_PROJECTS_DIR / "06-matlab-style",
        binary_relative=Path("matlab_generated_code"),
        build_steps=[["bash", "build.sh"]],
        project_type="gcc",
        expected_vars=["control_cycle_count", "fault_count", "throttle_position"],
    ),
    "07-simulink-blocks": SampleProject(
        key="07-simulink-blocks",
        project_dir=CPP_PROJECTS_DIR / "07-simulink-blocks",
        binary_relative=Path("simulink_vehicle_model"),
        build_steps=[["bash", "build.sh"]],
        project_type="gcc",
        expected_vars=["simulation_step", "control_updates", "steering_input"],
    ),
}


_BUILT_PROJECTS: set[str] = set()


def ensure_sample_project_built(sample: SampleProject) -> Path:
    """Run the project's build steps if needed and return the binary path."""
    binary_path = sample.project_dir / sample.binary_relative

    if sample.key in _BUILT_PROJECTS and binary_path.exists():
        return binary_path

    for step in sample.build_steps:
        subprocess.run(
            step,
            cwd=sample.project_dir,
            check=True,
            timeout=180,
        )

    if not binary_path.exists():
        raise FileNotFoundError(f"Binary not produced for {sample.key}: {binary_path}")

    _BUILT_PROJECTS.add(sample.key)
    return binary_path


@pytest.fixture(scope="session")
def ensure_sample_built():
    return ensure_sample_project_built


@pytest.fixture(scope="session")
def structured_project_dir() -> Path:
    """Path to the cmake-structured sample used across tests."""
    return SAMPLE_PROJECTS["02-cmake-structured"].project_dir


@pytest.fixture(scope="session")
def structured_project_binary() -> Path:
    """Ensure the cmake-structured sample is built and return the binary path."""
    sample = SAMPLE_PROJECTS["02-cmake-structured"]
    return ensure_sample_project_built(sample)


@pytest.fixture(autouse=True)
def quiet_cpp_trace_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep ptrace logs quieter during tests unless explicitly overridden."""
    monkeypatch.setenv("CPP_TRACE_VERBOSE", os.getenv("CPP_TRACE_VERBOSE", "0"))


__all__ = [
    "SampleProject",
    "SAMPLE_PROJECTS",
    "ensure_sample_project_built",
]
