#!/usr/bin/env python3
"""Exercise the periodic memory reporting against a dummy Kit server client."""

import asyncio
import subprocess
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'kuksa-syncer'))

import cpp_memory_debugger as debugger
from support.build_support import restore_app_fixture


class DummySocket:
    def __init__(self) -> None:
        self.events = []

    async def emit(self, event: str, payload):  # noqa: ANN001 - compat with socket.io
        self.events.append((event, payload))


async def run_monitor() -> tuple[list[tuple[str, dict]], list[tuple[str, bool]]]:
    app_dir = restore_app_fixture()
    subprocess.run(["bash", "build.sh"], cwd=app_dir, check=True)

    socket = DummySocket()
    replies: list[tuple[str, bool]] = []

    async def send_reply(content: str, is_error: bool = False):
        replies.append((content, is_error))

    monitor_task = asyncio.create_task(
        debugger.periodic_memory_var_report(
            socket,
            "test-kit",
            "status_reg1_raw,ignition",
            send_reply_func=send_reply,
        )
    )

    await asyncio.sleep(1.5)
    debugger.cleanup_memory_monitor()
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass

    return socket.events, replies


def test_syncer_message_flow() -> None:
    events, replies = asyncio.run(run_monitor())

    trace_events = [payload for event, payload in events if event == "messageToKit-kitReply"]
    assert trace_events, "No Kit server events captured"

    trace_payloads = [payload for payload in trace_events if payload.get("cmd") == "trace_vars"]
    assert trace_payloads, "No trace_vars payloads produced"
    sample_payload = trace_payloads[0]
    assert set(sample_payload.get("data", {}).keys()), "trace_vars data missing"

    stdout_lines = [text for text, is_error in replies if not is_error]
    assert stdout_lines, "No stdout forwarded to Kit server replies"


if __name__ == "__main__":
    test_syncer_message_flow()
