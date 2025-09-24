#!/usr/bin/env python3
"""Utility helpers to build and manage support binaries for ptrace tests."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

SUPPORT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SUPPORT_DIR.parent.parent
APP_DIR = REPO_ROOT / "kuksa-syncer" / "app"
BIN_DIR = SUPPORT_DIR / "bin"

EMBEDDED_STYLE_DIR = REPO_ROOT / "cpp-projects" / "05-embedded-style"

TEST_SIMPLE_SOURCE = SUPPORT_DIR / "test_simple.cpp"
TEST_SIMPLE_BINARY = APP_DIR / "test_simple"

PTRACE_TEST_SOURCE = SUPPORT_DIR / "ptrace_test_app.cpp"
PTRACE_TEST_BINARY = BIN_DIR / "test_app"


def _compile(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "g++",
        "-g",
        "-O0",
        "-std=c++17",
        "-pthread",
        "-no-pie",
        "-o",
        str(output),
        str(source),
    ]
    subprocess.run(cmd, check=True, cwd=str(source.parent))
    output.chmod(output.stat().st_mode | 0o111)


def ensure_test_simple_binary() -> Path:
    """Ensure the simple ptrace test binary exists and is up to date."""
    if not TEST_SIMPLE_BINARY.exists() or TEST_SIMPLE_BINARY.stat().st_mtime < TEST_SIMPLE_SOURCE.stat().st_mtime:
        _compile(TEST_SIMPLE_SOURCE, TEST_SIMPLE_BINARY)
    return TEST_SIMPLE_BINARY


def ensure_ptrace_test_binary() -> Path:
    """Ensure the ptrace monitoring test binary exists and is up to date."""
    target = PTRACE_TEST_BINARY
    if not target.exists() or target.stat().st_mtime < PTRACE_TEST_SOURCE.stat().st_mtime:
        _compile(PTRACE_TEST_SOURCE, target)
    return target


def resolve_symbol_address(binary_path: Path, symbol: str) -> int:
    """Return the virtual address of a symbol using nm."""
    result = subprocess.run(
        ["nm", "--defined-only", str(binary_path)],
        check=True,
        text=True,
        capture_output=True,
    )
    for line in result.stdout.splitlines():
        parts = line.strip().split()
        if len(parts) >= 3 and parts[-1] == symbol:
            return int(parts[0], 16)
    raise RuntimeError(f"Symbol {symbol} not found in {binary_path}")


def resolve_runtime_address(pid: int, binary_path: Path, symbol: str) -> int:
    """Translate a symbol virtual address to the runtime address for a running process."""
    symbol_addr = resolve_symbol_address(binary_path, symbol)
    binary_path = binary_path.resolve()

    if not _is_pie(binary_path):
        return symbol_addr

    base_addr = _module_base_address(pid, binary_path)
    return base_addr + symbol_addr


def _is_pie(binary_path: Path) -> bool:
    result = subprocess.run(
        ["readelf", "-h", str(binary_path)],
        check=True,
        text=True,
        capture_output=True,
    )
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("Type:"):
            return "DYN" in line
    return False


def _module_base_address(pid: int, binary_path: Path) -> int:
    with open(f"/proc/{pid}/maps", "r", encoding="utf-8") as maps_file:
        for line in maps_file:
            parts = line.strip().split()
            if len(parts) < 6:
                continue

            path_str = parts[-1]
            try:
                mapped_path = Path(path_str).resolve()
            except FileNotFoundError:
                continue

            if mapped_path != binary_path.resolve():
                continue

            perms = parts[1]
            offset = int(parts[2], 16)
            if "r" in perms and offset == 0:
                start_str, _ = parts[0].split("-")
                return int(start_str, 16)

    raise RuntimeError(f"Module base not found for {binary_path}")


def restore_app_fixture() -> Path:
    """Repopulate kuksa-syncer/app with the embedded style sample project."""
    if not EMBEDDED_STYLE_DIR.exists():
        raise RuntimeError("Embedded style project directory missing")

    APP_DIR.mkdir(parents=True, exist_ok=True)

    for item in list(APP_DIR.iterdir()):
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    for filename in ("build.sh", "embedded_ecu_system.cpp"):
        shutil.copy(EMBEDDED_STYLE_DIR / filename, APP_DIR / filename)

    origin = APP_DIR / "embedded_ecu_system.cpp.origin"
    shutil.copy(EMBEDDED_STYLE_DIR / "embedded_ecu_system.cpp", origin)

    return APP_DIR


__all__ = [
    "ensure_test_simple_binary",
    "ensure_ptrace_test_binary",
    "resolve_symbol_address",
    "resolve_runtime_address",
    "restore_app_fixture",
    "TEST_SIMPLE_BINARY",
    "PTRACE_TEST_BINARY",
]
