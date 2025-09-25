from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import pytest

import cpp_memory_debugger

from conftest import SAMPLE_PROJECTS, SampleProject


@dataclass
class CapturedEvent:
    event: str
    data: Dict[str, Any]


class MockSocketIO:
    def __init__(self) -> None:
        self.events: List[CapturedEvent] = []

    async def emit(self, event: str, data: Dict[str, Any]) -> None:
        self.events.append(CapturedEvent(event=event, data=data))


@pytest.mark.asyncio
@pytest.mark.parametrize("sample_key", sorted(SAMPLE_PROJECTS.keys()))
async def test_ptrace_trace_vars_filters_missing_variables(sample_key: str, ensure_sample_built) -> None:
    sample: SampleProject = SAMPLE_PROJECTS[sample_key]
    ensure_sample_built(sample)

    focus_vars = sample.expected_vars[: min(len(sample.expected_vars), 3)]
    requested_vars = focus_vars + ["__nonexistent__"]

    socket = MockSocketIO()

    await cpp_memory_debugger.start_cpp_trace_vars_monitoring(
        data={
            "cmd": "trace_vars",
            "request_from": f"pytest-{sample.key}",
            "project_type": sample.project_type,
            "project_path": str(sample.project_dir),
            "binary_name": sample.binary_relative.name,
            "trace_vars": requested_vars,
            "duration": 1,
            "skip_build": True,
            "verbose": False,
        },
        request_from=f"pytest-{sample.key}",
        socketio=socket,
    )

    trace_payloads: List[Dict[str, Any]] = [
        event.data
        for event in socket.events
        if event.event == "messageToKit-kitReply" and event.data.get("cmd") == "trace_vars"
    ]

    assert trace_payloads, f"expected at least one trace_vars update for {sample.key}"

    for payload in trace_payloads:
        variables = payload.get("data", {})
        assert set(focus_vars).issubset(variables.keys())
        assert "__nonexistent__" not in variables
        for key in focus_vars:
            value = variables[key]
            assert isinstance(value, (int, float)), f"{key} should be numeric"

    completed = any(
        event.event == "messageToKit-kitReply"
        and event.data.get("cmd") == "run_cpp_app"
        and "completed" in (event.data.get("data") or "").lower()
        for event in socket.events
    )
    assert completed, f"trace_vars session did not report completion for {sample.key}"
