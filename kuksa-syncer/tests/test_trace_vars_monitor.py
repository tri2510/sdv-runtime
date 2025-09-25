from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import pytest

import cpp_memory_debugger


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
async def test_ptrace_trace_vars_filters_missing_variables(structured_project_dir, structured_project_binary):
    request = {
        "cmd": "trace_vars",
        "request_from": "pytest-suite",
        "project_type": "cmake",
        "project_path": str(structured_project_dir),
        "binary_name": "vehicle_systems",
        "trace_vars": ["actual_speed", "battery_voltage", "non_existent_var"],
        "duration": 1,
        "skip_build": True,
        "verbose": False,
    }

    socket = MockSocketIO()

    await cpp_memory_debugger.start_cpp_trace_vars_monitoring(
        data=request,
        request_from="pytest-suite",
        socketio=socket,
    )

    trace_payloads: List[Dict[str, Any]] = [
        event.data
        for event in socket.events
        if event.event == "messageToKit-kitReply" and event.data.get("cmd") == "trace_vars"
    ]

    assert trace_payloads, "expected at least one trace_vars update"

    # Every payload should include only the variables that were successfully resolved.
    for payload in trace_payloads:
        variables = payload.get("data", {})
        assert set(variables.keys()).issuperset({"actual_speed", "battery_voltage"})
        assert "non_existent_var" not in variables
        for key in ("actual_speed", "battery_voltage"):
            value = variables[key]
            assert isinstance(value, (int, float))

    # Ensure the session completed cleanly (monitor reports a completion message at the end).
    completed = any(
        event.event == "messageToKit-kitReply"
        and event.data.get("cmd") == "run_cpp_app"
        and "completed" in (event.data.get("data") or "").lower()
        for event in socket.events
    )
    assert completed, "trace_vars session did not report completion"
