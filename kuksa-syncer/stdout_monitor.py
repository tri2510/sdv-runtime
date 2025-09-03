#!/usr/bin/env python3
"""
Alternative monitoring approach using stdout parsing - no memory protection issues.
"""

import asyncio
import json
import re
from pathlib import Path

async def monitor_cpp_stdout(binary_path, watch_vars, callback):
    """Monitor C++ application stdout for variable updates."""
    
    # Run the binary and monitor its output
    process = await asyncio.create_subprocess_exec(
        binary_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        text=True
    )
    
    print(f"Started process PID {process.pid}, monitoring stdout...")
    
    variables = {}
    var_pattern = r'(\w+):\s*([\d.-]+)'  # Matches "variable: value"
    json_pattern = r'\{.*"variables".*\}'  # Matches JSON with variables
    
    try:
        while True:
            line = await process.stdout.readline()
            if not line:
                break
                
            line = line.strip()
            print(f"Output: {line}")
            
            # Method 1: Look for JSON format
            if "variables" in line and "{" in line:
                try:
                    data = json.loads(line)
                    if "variables" in data:
                        variables.update(data["variables"])
                        if callback:
                            await callback(variables.copy())
                except json.JSONDecodeError:
                    pass
            
            # Method 2: Look for "variable: value" format
            matches = re.findall(var_pattern, line)
            for var_name, value_str in matches:
                if var_name in watch_vars:
                    try:
                        # Auto-detect type
                        if '.' in value_str:
                            variables[var_name] = float(value_str)
                        else:
                            variables[var_name] = int(value_str)
                    except ValueError:
                        variables[var_name] = value_str
            
            # Send update if we have variables
            if variables and callback:
                await callback(variables.copy())
                
    except Exception as e:
        print(f"Stdout monitoring error: {e}")
    finally:
        if process.returncode is None:
            process.terminate()
            await process.wait()

# Test function
async def test_stdout_monitor():
    binary_path = "/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/kuksa-syncer/app/main_bin"
    watch_vars = ["ego_speed", "collision_risk", "current_lane"]
    
    async def print_variables(vars_dict):
        print(f"Variables updated: {vars_dict}")
    
    await monitor_cpp_stdout(binary_path, watch_vars, print_variables)

if __name__ == "__main__":
    asyncio.run(test_stdout_monitor())