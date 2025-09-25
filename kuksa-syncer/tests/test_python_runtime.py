from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Dict, List

import pytest

import syncer


@dataclass
class RecordedEmit:
    event: str
    data: Dict[str, Any]


class StubbedSio:
    def __init__(self) -> None:
        self.events: List[RecordedEmit] = []

    async def emit(self, event: str, data: Dict[str, Any]) -> None:
        self.events.append(RecordedEmit(event=event, data=data))


class DummyProcess:
    def __init__(self, cmd: str) -> None:
        self.cmd = cmd


@pytest.mark.asyncio
async def test_run_python_app_spawns_subpiper(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    stub_sio = StubbedSio()
    monkeypatch.setattr(syncer, "sio", stub_sio)
    monkeypatch.setattr(syncer, "CLIENT_ID", "Runtime-Test", raising=False)

    # keep lsOfRunner isolated for this test
    local_runner: List[Dict[str, Any]] = []
    monkeypatch.setattr(syncer, "lsOfRunner", local_runner, raising=False)

    captured = {}

    def fake_subpiper(*, master_id: str, cmd: str, stdout_callback, stderr_callback, finished_callback):
        captured["master_id"] = master_id
        captured["cmd"] = cmd
        captured["stdout_callback"] = stdout_callback
        captured["stderr_callback"] = stderr_callback
        captured["finished_callback"] = finished_callback
        return DummyProcess(cmd)

    monkeypatch.setattr(syncer, "subpiper", fake_subpiper)

    # write generated script in temporary workspace to avoid polluting repo root
    monkeypatch.chdir(tmp_path)

    request = {
        "cmd": "run_python_app",
        "request_from": "kit-client",
        "data": {
            "code": "print('hello from runtime')\n",
            "name": "Sample Python App",
        },
        "usedAPIs": [],
    }

    result = await syncer.messageToKit(request)
    assert result == 0

    # The generated script should exist and contain the provided payload
    script_path = tmp_path / "main.py"
    assert script_path.exists()
    assert script_path.read_text() == "print('hello from runtime')\n"

    # subpiper must be invoked with the correct interpreter command
    assert captured["master_id"] == "kit-client"
    assert captured["cmd"] == "python -u main.py"

    # runner bookkeeping should include our new entry
    assert len(local_runner) == 1
    entry = local_runner[0]
    assert entry["appName"] == "Sample Python App"
    assert entry["request_from"] == "kit-client"
    assert isinstance(entry["runner"], DummyProcess)

    # run_python_app should launch silently (no immediate error replies)
    assert not stub_sio.events
