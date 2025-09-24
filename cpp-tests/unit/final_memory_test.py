#!/usr/bin/env python3
"""Comprehensive ptrace sanity check against the support binary."""

import ctypes
import os
import struct
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


def test_process_state() -> None:
    binary_path = ensure_test_simple_binary()
    process = subprocess.Popen([str(binary_path)])

    time.sleep(0.5)
    if process.poll() is not None:
        raise RuntimeError(f"Process exited early with {process.returncode}")

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

    with open(f"/proc/{process.pid}/stat", "r", encoding="utf-8") as stat_file:
        state = stat_file.read().split()[2]
        print(f"Process state after attach: {state}")

    counter_addr = resolve_runtime_address(process.pid, binary_path, "test_counter")
    value_addr = resolve_runtime_address(process.pid, binary_path, "test_value")

    data = libc.ptrace(PTRACE_PEEKDATA, process.pid, counter_addr, 0)
    if data == -1:
        errno_val = libc.__errno_location().contents.value
        raise RuntimeError(f"Failed to read counter: {os.strerror(errno_val)}")
    counter_val = ctypes.c_int32(data & 0xFFFFFFFF).value
    print(f"test_counter={counter_val}")

    data = libc.ptrace(PTRACE_PEEKDATA, process.pid, value_addr, 0)
    if data == -1:
        errno_val = libc.__errno_location().contents.value
        raise RuntimeError(f"Failed to read value: {os.strerror(errno_val)}")
    float_val = struct.unpack("<f", struct.pack("<Q", data)[:4])[0]
    print(f"test_value={float_val}")

    libc.ptrace(PTRACE_DETACH, process.pid, 0, 0)
    process.terminate()
    process.wait()


if __name__ == "__main__":
    test_process_state()
