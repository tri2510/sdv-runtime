from __future__ import annotations

from pathlib import Path

from universal_auto_detector import UniversalAutoDetector


def test_universal_detector_finds_expected_globals(structured_project_dir: Path, structured_project_binary: Path) -> None:
    detector = UniversalAutoDetector()

    monitorable_vars, binary_path = detector.auto_detect_project_variables(structured_project_dir)

    assert binary_path == structured_project_binary

    names = {var["name"] for var in monitorable_vars if var.get("found_in_binary")}

    # Key telemetry variables should always be present once the project is built.
    assert {"actual_speed", "battery_voltage", "engine_rpm"}.issubset(names)

    # Sanity check that we aren't returning an empty list when symbols are missing.
    assert len(names) >= 10
