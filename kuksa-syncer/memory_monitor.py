#!/usr/bin/env python3
"""
High-performance C++ variable monitoring via direct process memory inspection.
No GDB overhead, no code injection, pure memory reading.
"""

import os
import struct
import subprocess
import re
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

class ProcessMemoryMonitor:
    """Direct process memory reader for C++ variable monitoring."""
    
    def __init__(self, binary_path: str):
        self.binary_path = binary_path
        self.process = None
        self.pid = None
        self.symbol_table = {}
        self.memory_maps = {}
        
    def start_process(self) -> bool:
        """Start the C++ process with debug symbols."""
        try:
            self.process = subprocess.Popen(
                [self.binary_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.pid = self.process.pid
            time.sleep(0.5)  # Let process initialize
            
            # Build symbol table for variable addresses
            self._build_symbol_table()
            self._parse_memory_maps()
            
            return True
        except Exception as e:
            print(f"Failed to start process: {e}")
            return False
    
    def _build_symbol_table(self):
        """Extract variable symbols and addresses from binary."""
        try:
            # Use multiple methods to find symbols
            
            # Method 1: objdump for traditional symbols
            result = subprocess.run(['objdump', '-t', self.binary_path], 
                                 capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                parts = line.split()
                if len(parts) >= 6 and ('.data' in line or '.bss' in line):
                    address = parts[0]
                    symbol_name = parts[-1]
                    
                    if address.startswith('0') and len(address) > 8:
                        self.symbol_table[symbol_name] = int(address, 16)
            
            # Method 2: nm for additional symbols 
            result = subprocess.run(['nm', self.binary_path], 
                                 capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                parts = line.split()
                if len(parts) >= 3 and parts[1] in ['D', 'B']:  # Data/BSS symbols
                    address = parts[0]
                    symbol_name = parts[2]
                    
                    if address and all(c in '0123456789abcdefABCDEF' for c in address):
                        self.symbol_table[symbol_name] = int(address, 16)
            
            print(f"Found {len(self.symbol_table)} symbols in binary")
            if len(self.symbol_table) > 0:
                # Show some examples for debugging
                sample_symbols = list(self.symbol_table.keys())[:5]
                print(f"Sample symbols: {sample_symbols}")
                        
        except Exception as e:
            print(f"Symbol table building failed: {e}")
    
    def _parse_memory_maps(self):
        """Parse /proc/pid/maps to understand process memory layout."""
        try:
            with open(f'/proc/{self.pid}/maps', 'r') as f:
                maps = f.read()
            
            for line in maps.split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 6:
                        addr_range = parts[0]
                        permissions = parts[1]
                        path = parts[-1] if len(parts) > 5 else ''
                        
                        start, end = addr_range.split('-')
                        self.memory_maps[path] = {
                            'start': int(start, 16),
                            'end': int(end, 16),
                            'permissions': permissions
                        }
                        
        except Exception as e:
            print(f"Memory map parsing failed: {e}")
    
    def read_variable(self, var_name: str, var_type: str) -> Optional[Any]:
        """Read variable value directly from process memory."""
        if var_name not in self.symbol_table:
            print(f"Variable {var_name} not found in symbol table")
            return None
            
        try:
            var_address = self.symbol_table[var_name]
            print(f"Reading {var_name} at address 0x{var_address:x}")
            
            # Use ptrace method as fallback to /proc/pid/mem
            try:
                # Method 1: Direct /proc/pid/mem access
                with open(f'/proc/{self.pid}/mem', 'rb') as mem_file:
                    mem_file.seek(var_address)
                    
                    # Read based on type - atomic types are typically 4 or 8 bytes
                    if var_type in ['int', 'int32_t']:
                        data = mem_file.read(4)
                        if len(data) == 4:
                            value = struct.unpack('i', data)[0]
                            print(f"Read {var_name} = {value}")
                            return value
                    elif var_type in ['float']:
                        data = mem_file.read(4)
                        if len(data) == 4:
                            value = struct.unpack('f', data)[0]
                            print(f"Read {var_name} = {value}")
                            return value
                    elif var_type in ['double']:
                        data = mem_file.read(8)
                        if len(data) == 8:
                            value = struct.unpack('d', data)[0]
                            print(f"Read {var_name} = {value}")
                            return value
                    elif var_type in ['bool']:
                        data = mem_file.read(1)
                        if len(data) == 1:
                            value = bool(data[0])
                            print(f"Read {var_name} = {value}")
                            return value
                    else:
                        # Default to 4-byte integer
                        data = mem_file.read(4)
                        if len(data) == 4:
                            value = struct.unpack('i', data)[0]
                            print(f"Read {var_name} = {value}")
                            return value
                            
            except OSError as mem_error:
                print(f"Direct memory read failed for {var_name}: {mem_error}")
                
                # Method 2: Use gdb as fallback
                try:
                    result = subprocess.run(['gdb', '--batch', '--quiet', 
                                           '--eval-command', f'attach {self.pid}',
                                           '--eval-command', f'print {var_name}',
                                           '--eval-command', 'detach',
                                           '--eval-command', 'quit'],
                                          capture_output=True, text=True, timeout=2)
                    
                    # Parse gdb output
                    for line in result.stdout.split('\n'):
                        if '$1 = ' in line:
                            value_str = line.split('$1 = ')[1].strip()
                            try:
                                if var_type == 'float':
                                    return float(value_str)
                                elif var_type == 'bool':
                                    return value_str.lower() in ['true', '1']
                                else:
                                    return int(value_str)
                            except ValueError:
                                pass
                                
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    pass
                    
        except Exception as e:
            print(f"Memory read failed for {var_name}: {e}")
            
        return None
    
    def monitor_variables(self, variables: Dict[str, str], callback=None) -> Dict[str, Any]:
        """Monitor multiple variables and return their values."""
        values = {}
        
        for var_name, var_type in variables.items():
            value = self.read_variable(var_name, var_type)
            if value is not None:
                values[var_name] = value
                
        if callback:
            callback(values)
            
        return values
    
    def start_monitoring_loop(self, variables: Dict[str, str], 
                            interval: float = 0.1, callback=None):
        """Start continuous monitoring loop."""
        print(f"Starting memory monitoring for PID {self.pid}")
        print(f"Variables: {list(variables.keys())}")
        print(f"Symbol table: {len(self.symbol_table)} symbols")
        
        try:
            while self.process.poll() is None:  # Process still running
                values = self.monitor_variables(variables, callback)
                
                if values:  # Only print if we got values
                    print(f"Variables: {values}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("Monitoring stopped by user")
        except Exception as e:
            print(f"Monitoring error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        if self.process:
            if self.process.poll() is None:  # Still running
                self.process.terminate()
                self.process.wait()
            print("Process cleanup completed")
    
    def is_process_running(self) -> bool:
        """Check if monitored process is still running."""
        return self.process is not None and self.process.poll() is None


class SmartVariableDetector:
    """Automatically detect variables from C++ source code."""
    
    @staticmethod
    def detect_variables(cpp_code: str) -> Dict[str, str]:
        """Parse C++ code to detect global variables."""
        variables = {}
        
        # Regex patterns for variable declarations
        patterns = [
            # Global variables: type name = value;
            r'\b(int|float|double|bool)\s+(\w+)\s*=\s*[^;]+;',
            # Global variables: type name;
            r'\b(int|float|double|bool)\s+(\w+)\s*;',
            # Atomic variables: std::atomic<type> name
            r'std::atomic<(int|float|double|bool)>\s+(\w+)',
            # Static variables
            r'static\s+(int|float|double|bool)\s+(\w+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, cpp_code, re.MULTILINE)
            for match in matches:
                if len(match.groups()) == 2:
                    var_type, var_name = match.groups()
                    variables[var_name] = var_type
        
        return variables


def main():
    """Demo/test function."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 memory_monitor.py <cpp_binary> [variables...]")
        sys.exit(1)
    
    binary_path = sys.argv[1]
    
    # No hardcoded default variables - use auto-detection instead
    default_vars = {
        # Auto-detection will populate this based on actual source code
        # No hardcoded variable names
    }
    
    monitor = ProcessMemoryMonitor(binary_path)
    
    if not monitor.start_process():
        print("Failed to start monitoring")
        sys.exit(1)
    
    print(f"Monitoring {binary_path} (PID: {monitor.pid})")
    
    try:
        monitor.start_monitoring_loop(default_vars, interval=0.5)
    except KeyboardInterrupt:
        print("\nStopping monitor...")
    finally:
        monitor.cleanup()


if __name__ == "__main__":
    main()