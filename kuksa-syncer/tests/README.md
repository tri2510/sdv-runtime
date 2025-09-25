# Kuksa Syncer Test Suite

This folder holds the automated regression tests for the ptrace-enabled C++ runtime.

## What gets covered
- **Variable discovery** – `test_variable_detection.py` builds each example project and ensures all expected global signals are discoverable in the compiled binary.
- **Trace streaming** – `test_trace_vars_monitor.py` starts `start_cpp_trace_vars_monitoring` for each sample project and asserts that ptrace delivers values for the requested signals while filtering unknown names.
- **Python runtime guardrail** – `test_python_runtime.py` verifies the legacy `run_python_app` flow still spawns `subpiper` and tracks the runner.

## How to run
From the repository root, install the requirements (ideally inside a virtualenv) and execute:

```bash
pip install -r requirements.txt
./run_tests.py
```

`run_tests.py` pins pytest to the bundled suite and disables third-party plugins that have caused issues (for example, the old `pytest-sugar`). Extra pytest arguments can be forwarded, e.g. `./run_tests.py -k ptrace`.

If you prefer a direct invocation, set `PYTEST_ADDOPTS="-p no:pytest_sugar"` or upgrade/remove the plugin before calling `python3 -m pytest`.

## Sample builds
The fixtures rebuild each C++ sample as needed (CMake, Makefile, or shell script) and cache successful builds for subsequent tests. Expect the first run to take ~30–35 seconds because all seven binaries are compiled.

## Running the syncer without Kuksa
Some commands (for example `subscribe_apis`) normally contact the Kuksa databroker. When you only want the ptrace workflow, you can disable those calls by starting the syncer with:

```bash
export KUKSA_DISABLED=1
python -m kuksa-syncer.syncer
```

With `KUKSA_DISABLED=1`, the syncer short-circuits all databroker interactions and logs a “KUKSA integration disabled” message instead of repeatedly attempting to connect to `127.0.0.1:55555`.
