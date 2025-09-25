from __future__ import annotations

from pathlib import Path

import pytest

from universal_auto_detector import UniversalAutoDetector

from conftest import SAMPLE_PROJECTS, SampleProject


@pytest.mark.parametrize("sample_key", sorted(SAMPLE_PROJECTS.keys()))
def test_universal_detector_finds_expected_globals(sample_key: str, ensure_sample_built) -> None:
    sample: SampleProject = SAMPLE_PROJECTS[sample_key]
    expected_binary = ensure_sample_built(sample)

    detector = UniversalAutoDetector()
    monitorable_vars, binary_path = detector.auto_detect_project_variables(sample.project_dir)

    assert binary_path == expected_binary

    names = {var["name"] for var in monitorable_vars if var.get("found_in_binary")}

    # Each sample advertises the key telemetry signals we expect.
    assert set(sample.expected_vars).issubset(names)
    assert len(names) >= len(sample.expected_vars)
