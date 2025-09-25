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
        expected_vars=[
            "battery_level",
            "brake_applied",
            "current_speed",
            "cycle",
            "distance_traveled",
            "drive_mode",
            "engine_cycles",
            "engine_rpm",
            "engine_running",
            "fuel_level",
            "gear_position",
            "gps_latitude",
            "gps_longitude",
            "headlights_on",
            "microsecond_timestamp",
            "odometer_reading",
            "print_counter",
            "steering_angle",
            "temperature_offset",
            "tire_pressure_psi",
            "total_engine_runtime",
            "turn_signal_left",
            "turn_signal_right",
        ],
    ),
    "02-cmake-structured": SampleProject(
        key="02-cmake-structured",
        project_dir=CPP_PROJECTS_DIR / "02-cmake-structured",
        binary_relative=Path("build") / "vehicle_systems",
        build_steps=[["bash", "build.sh"]],
        project_type="cmake",
        expected_vars=[
            "abs_active",
            "actual_speed",
            "battery_current",
            "battery_soc",
            "battery_temp",
            "battery_voltage",
            "brake_pressure",
            "cruise_control_active",
            "cycle",
            "engine_load",
            "engine_rpm",
            "engine_temp",
            "esp_active",
            "gear_number",
            "gps_altitude",
            "gps_latitude",
            "gps_longitude",
            "imu_accel_x",
            "imu_accel_y",
            "imu_accel_z",
            "imu_gyro_x",
            "imu_gyro_y",
            "imu_gyro_z",
            "print_counter",
            "target_speed",
            "throttle_position",
            "tire_pressure_fl",
            "tire_pressure_fr",
            "tire_pressure_rl",
            "tire_pressure_rr",
            "tire_temp_fl",
            "tire_temp_fr",
            "tire_temp_rl",
            "tire_temp_rr",
            "transmission_locked",
        ],
    ),
    "03-makefile-build": SampleProject(
        key="03-makefile-build",
        project_dir=CPP_PROJECTS_DIR / "03-makefile-build",
        binary_relative=Path("adas_monitor"),
        build_steps=[["make", "clean"], ["make"]],
        project_type="make",
        expected_vars=[
            "acc_enabled",
            "acceleration_command",
            "actual_distance",
            "brake_request",
            "closing_velocity",
            "collision_warning",
            "current_speed",
            "following_mode",
            "front_distance",
            "lane_angle",
            "lane_departure_warning",
            "lane_position",
            "left_lane_detected",
            "lka_active",
            "right_lane_detected",
            "set_speed",
            "steering_torque",
            "target_distance",
            "time_to_collision",
            "warning_level",
        ],
    ),
    "04-complex-structures": SampleProject(
        key="04-complex-structures",
        project_dir=CPP_PROJECTS_DIR / "04-complex-structures",
        binary_relative=Path("complex_vehicle_system"),
        build_steps=[["bash", "build.sh"]],
        project_type="gcc",
        expected_vars=[
            "abs_active",
            "active_warnings",
            "clutch_engaged",
            "cpu_usage",
            "diagnostics_active",
            "emergency_brake",
            "engine_fault",
            "engine_rpm",
            "engine_torque",
            "esp_active",
            "fire_detected",
            "fuel_consumption",
            "gear_ratio",
            "impact_sensor_x",
            "impact_sensor_y",
            "impact_sensor_z",
            "memory_usage",
            "oil_pressure",
            "rollover_detected",
            "seatbelt_warning",
            "system_health",
            "system_uptime",
            "tcs_active",
            "total_errors",
            "transmission_fault",
        ],
    ),
    "05-embedded-style": SampleProject(
        key="05-embedded-style",
        project_dir=CPP_PROJECTS_DIR / "05-embedded-style",
        binary_relative=Path("embedded_ecu_system"),
        build_steps=[["bash", "build.sh"]],
        project_type="gcc",
        expected_vars=[
            "active_dtc_count",
            "can_error_counter",
            "can_rx_counter",
            "can_tx_counter",
            "cpu_load_percent",
            "dtc_b0xxx",
            "dtc_c0xxx",
            "dtc_p0xxx",
            "dtc_u0xxx",
            "heap_usage_bytes",
            "lin_frame_counter",
            "main_loop_counter",
            "memory_fragmentation_percent",
            "stack_usage_bytes",
            "status_reg1_raw",
            "status_reg2_raw",
            "task_execution_time_us",
        ],
    ),
    "06-matlab-style": SampleProject(
        key="06-matlab-style",
        project_dir=CPP_PROJECTS_DIR / "06-matlab-style",
        binary_relative=Path("matlab_generated_code"),
        build_steps=[["bash", "build.sh"]],
        project_type="gcc",
        expected_vars=[
            "brake_enable",
            "brake_pressure",
            "brake_torque_cmd",
            "control_cycle_count",
            "engine_enable",
            "engine_torque_cmd",
            "fault_count",
            "kd_speed",
            "ki_speed",
            "kp_speed",
            "prev_speed_error",
            "safety_override",
            "speed_error",
            "speed_integral",
            "steering_angle",
            "steering_torque_cmd",
            "throttle_position",
            "time",
            "vehicle_speed",
        ],
    ),
    "07-simulink-blocks": SampleProject(
        key="07-simulink-blocks",
        project_dir=CPP_PROJECTS_DIR / "07-simulink-blocks",
        binary_relative=Path("simulink_vehicle_model"),
        build_steps=[["bash", "build.sh"]],
        project_type="gcc",
        expected_vars=[
            "abs_intervention",
            "acceleration_sensor",
            "accelerator_pedal",
            "air_density",
            "brake_command",
            "brake_gain",
            "brake_pedal",
            "control_updates",
            "cruise_control_active",
            "drag_coefficient",
            "engine_speed",
            "gyro_sensor",
            "lateral_acceleration",
            "simulation_step",
            "speed_sensor",
            "stability_control",
            "steering_command",
            "steering_gain",
            "steering_input",
            "target_speed",
            "throttle_command",
            "throttle_gain",
            "time",
            "transmission_ratio",
            "vehicle_mass",
            "vehicle_velocity",
            "wheel_angular_velocity",
            "wheel_radius",
            "yaw_rate",
        ],
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
