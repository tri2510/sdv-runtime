#!/usr/bin/env python3
"""Validates direct ptrace reads against the support test binary."""

import ctypes
import os
import signal
import subprocess
import time
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from support.build_support import (
    ensure_test_simple_binary,
    resolve_runtime_address,
    TEST_SIMPLE_BINARY,
)


def test_simple_memory_read() -> None:
    """Attach to the helper binary and confirm ptrace can read globals."""

    binary_path = ensure_test_simple_binary()

    print("=== Simple Memory Read Test ===")
    print(f"Binary: {binary_path}")

    process = subprocess.Popen(
        [str(binary_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print(f"✅ Process started with PID {process.pid}")

    time.sleep(1)
    if process.poll() is not None:
        raise RuntimeError(f"test_simple exited early with {process.returncode}")

    libc = ctypes.CDLL("libc.so.6")
    libc.__errno_location.restype = ctypes.POINTER(ctypes.c_int)

    PTRACE_ATTACH = 16
    PTRACE_DETACH = 17
    PTRACE_PEEKDATA = 2

    if libc.ptrace(PTRACE_ATTACH, process.pid, 0, 0) == -1:
        errno_val = libc.__errno_location().contents.value
        process.terminate()
        raise RuntimeError(f"ptrace attach failed: {os.strerror(errno_val)}")

    os.waitpid(process.pid, 0)

    time.sleep(0.5)

    try:
        counter_addr = resolve_runtime_address(process.pid, binary_path, "test_counter")
        value_addr = resolve_runtime_address(process.pid, binary_path, "test_value")
    except Exception:
        libc.ptrace(PTRACE_DETACH, process.pid, 0, 0)
        process.terminate()
        process.wait()
        raise

    print(f"🔎 test_counter @ 0x{counter_addr:x}")
    data = libc.ptrace(PTRACE_PEEKDATA, process.pid, counter_addr, 0)
    if data == -1:
        errno_val = libc.__errno_location().contents.value
        raise RuntimeError(f"Failed to read test_counter: {os.strerror(errno_val)}")
    int_val = ctypes.c_int32(data & 0xFFFFFFFF).value
    print(f"   ➤ Value: {int_val}")

    print(f"🔎 test_value @ 0x{value_addr:x}")
    data = libc.ptrace(PTRACE_PEEKDATA, process.pid, value_addr, 0)
    if data == -1:
        errno_val = libc.__errno_location().contents.value
        raise RuntimeError(f"Failed to read test_value: {os.strerror(errno_val)}")

    import struct

    float_bytes = struct.pack("<Q", data)[:4]
    float_val = struct.unpack("<f", float_bytes)[0]
    print(f"   ➤ Value: {float_val}")

    libc.ptrace(PTRACE_DETACH, process.pid, 0, 0)

    process.send_signal(signal.SIGTERM)
    process.wait(timeout=2)
    print("✅ ptrace reads completed successfully")


if __name__ == "__main__":
    test_simple_memory_read()
