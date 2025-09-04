#!/usr/bin/env python3
"""
Automatic C++ Variable Detection System
Automatically detects atomic variables in C++ code and binary symbols.
"""

import re
import subprocess
import struct
import ctypes
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path

class AutoVariableDetector:
    """Automatically detect C++ variables and their types."""
    
    def __init__(self):
        self.variable_patterns = {
            # Pattern: (regex, expected_type, size_bytes)
            'atomic_int': (r'std::atomic<int>\s+(\w+)', 'int', 4),
            'atomic_float': (r'std::atomic<float>\s+(\w+)', 'float', 4), 
            'atomic_double': (r'std::atomic<double>\s+(\w+)', 'double', 8),
            'atomic_bool': (r'std::atomic<bool>\s+(\w+)', 'bool', 1),
            'int_var': (r'\bint\s+(\w+)', 'int', 4),
            'float_var': (r'\bfloat\s+(\w+)', 'float', 4),
            'double_var': (r'\bdouble\s+(\w+)', 'double', 8),
            'bool_var': (r'\bbool\s+(\w+)', 'bool', 1),
        }
    
    def extract_variables_from_source(self, cpp_code: str) -> List[Dict[str, Any]]:
        """Extract variable declarations from C++ source code."""
        detected_vars = []
        
        for pattern_name, (regex, var_type, size_bytes) in self.variable_patterns.items():
            matches = re.findall(regex, cpp_code)
            for var_name in matches:
                # Skip common keywords and function names
                if var_name.lower() in ['main', 'return', 'if', 'for', 'while', 'do']:
                    continue
                    
                detected_vars.append({
                    'name': var_name,
                    'type': var_type,
                    'size_bytes': size_bytes,
                    'pattern': pattern_name,
                    'is_atomic': 'atomic' in pattern_name
                })
        
        # Remove duplicates (same variable might match multiple patterns)
        unique_vars = {}
        for var in detected_vars:
            name = var['name']
            if name not in unique_vars:
                unique_vars[name] = var
            else:
                # Prefer atomic types over regular types
                if var['is_atomic'] and not unique_vars[name]['is_atomic']:
                    unique_vars[name] = var
        
        return list(unique_vars.values())
    
    def extract_variables_from_binary(self, binary_path: str) -> Dict[str, int]:
        """Extract variable symbols from compiled binary using nm."""
        symbol_table = {}
        
        try:
            # Use nm to get symbols
            result = subprocess.run(['nm', '-C', binary_path], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                return symbol_table
            
            # Parse nm output
            for line in result.stdout.split('\n'):
                if not line.strip():
                    continue
                    
                parts = line.split()
                if len(parts) >= 3:
                    addr_str, symbol_type, symbol_name = parts[0], parts[1], parts[2]
                    
                    # Look for data symbols (B, D, b, d)
                    if symbol_type.upper() in ['B', 'D']:
                        try:
                            addr = int(addr_str, 16)
                            symbol_table[symbol_name] = addr
                        except ValueError:
                            continue
            
            return symbol_table
            
        except Exception as e:
            print(f"Error extracting symbols from binary: {e}")
            return symbol_table
    
    def match_source_to_binary(self, source_vars: List[Dict], binary_symbols: Dict[str, int]) -> List[Dict[str, Any]]:
        """Match source code variables to binary symbols."""
        matched_vars = []
        
        for var_info in source_vars:
            var_name = var_info['name']
            
            # Look for exact match first
            if var_name in binary_symbols:
                var_info['symbol_address'] = binary_symbols[var_name]
                var_info['found_in_binary'] = True
                matched_vars.append(var_info)
                continue
            
            # Look for partial matches (sometimes symbols have prefixes/suffixes)
            found_match = False
            for symbol_name, addr in binary_symbols.items():
                if var_name in symbol_name:
                    var_info['symbol_address'] = addr
                    var_info['found_in_binary'] = True
                    var_info['symbol_name'] = symbol_name
                    matched_vars.append(var_info)
                    found_match = True
                    break
            
            if not found_match:
                var_info['found_in_binary'] = False
                matched_vars.append(var_info)
        
        return matched_vars
    
    def auto_detect_variables(self, cpp_code: str, binary_path: str) -> List[Dict[str, Any]]:
        """Automatically detect all monitorable variables in C++ code and binary."""
        print("🔍 Starting automatic variable detection...")
        
        # Step 1: Extract variables from source
        source_vars = self.extract_variables_from_source(cpp_code)
        print(f"📄 Found {len(source_vars)} variables in source code:")
        for var in source_vars:
            print(f"   - {var['name']} ({var['type']}) {'[atomic]' if var['is_atomic'] else ''}")
        
        # Step 2: Extract symbols from binary
        binary_symbols = self.extract_variables_from_binary(binary_path)
        print(f"🔧 Found {len(binary_symbols)} symbols in binary")
        
        # Step 3: Match source variables to binary symbols
        matched_vars = self.match_source_to_binary(source_vars, binary_symbols)
        
        # Filter to only variables found in binary
        monitorable_vars = [var for var in matched_vars if var['found_in_binary']]
        print(f"✅ {len(monitorable_vars)} variables available for monitoring:")
        
        for var in monitorable_vars:
            addr = var['symbol_address']
            print(f"   - {var['name']}: {var['type']} @ 0x{addr:x}")
        
        return monitorable_vars

class SmartMemoryReader:
    """Smart memory reader that adapts to variable types automatically."""
    
    def __init__(self, pid: int):
        self.pid = pid
        self.libc = ctypes.CDLL("libc.so.6")
        self.PTRACE_ATTACH = 16
        self.PTRACE_DETACH = 17 
        self.PTRACE_PEEKDATA = 2
        self.attached = False
    
    def attach(self) -> bool:
        """Attach to process."""
        try:
            result = self.libc.ptrace(self.PTRACE_ATTACH, self.pid, 0, 0)
            if result == 0:
                self.attached = True
                import time
                time.sleep(0.2)  # Give more time for attach
                
                # Continue the process after attaching
                self.libc.ptrace(self.PTRACE_CONT := 7, self.pid, 0, 0)
                return True
        except Exception as e:
            print(f"Failed to attach to PID {self.pid}: {e}")
        return False
    
    def detach(self):
        """Detach from process."""
        if self.attached:
            try:
                self.libc.ptrace(self.PTRACE_DETACH, self.pid, 0, 0)
                self.attached = False
            except:
                pass
    
    def read_variable_value(self, var_info: Dict[str, Any]) -> Optional[Union[int, float, bool]]:
        """Read variable value based on its detected type."""
        if not self.attached:
            return None
        
        try:
            addr = var_info['symbol_address']
            var_type = var_info['type']
            size_bytes = var_info['size_bytes']
            
            # Read memory data
            data = self.libc.ptrace(self.PTRACE_PEEKDATA, self.pid, addr, 0)
            if data == -1:
                return None
            
            # Parse based on detected type
            if var_type == 'int':
                return ctypes.c_int32(data & 0xFFFFFFFF).value
            
            elif var_type == 'float':
                # Extract 4 bytes and interpret as float
                float_bytes = struct.pack('<Q', data)[:4]
                float_val = struct.unpack('<f', float_bytes)[0]
                
                # Sanity check for reasonable values
                import math
                if math.isnan(float_val) or math.isinf(float_val) or abs(float_val) > 1e8:
                    return 0.0  # Return safe default
                return float_val
            
            elif var_type == 'double':
                # For double, we might need to read 8 bytes
                double_bytes = struct.pack('<Q', data)
                double_val = struct.unpack('<d', double_bytes)[0]
                
                import math
                if math.isnan(double_val) or math.isinf(double_val) or abs(double_val) > 1e15:
                    return 0.0
                return double_val
            
            elif var_type == 'bool':
                return bool(data & 0x1)
            
            else:
                # Default to int
                return ctypes.c_int32(data & 0xFFFFFFFF).value
        
        except Exception as e:
            print(f"Error reading {var_info['name']}: {e}")
            return None
    
    def read_all_variables(self, var_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Read all variables and return name->value mapping."""
        results = {}
        
        for var_info in var_list:
            if var_info['found_in_binary']:
                value = self.read_variable_value(var_info)
                if value is not None:
                    results[var_info['name']] = value
        
        return results

def test_auto_detection():
    """Test the automatic variable detection system."""
    print("=== Testing Automatic Variable Detection ===\n")
    
    # Test with current C++ code
    app_dir = Path("/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/kuksa-syncer/app")
    cpp_file = app_dir / "main.cpp"
    binary_file = app_dir / "main_bin"
    
    if not cpp_file.exists():
        print("❌ C++ source file not found")
        return False
    
    if not binary_file.exists():
        print("❌ Binary file not found") 
        return False
    
    # Read C++ source
    with open(cpp_file, 'r') as f:
        cpp_code = f.read()
    
    # Auto-detect variables
    detector = AutoVariableDetector()
    monitorable_vars = detector.auto_detect_variables(cpp_code, str(binary_file))
    
    if len(monitorable_vars) == 0:
        print("❌ No monitorable variables found")
        return False
    
    print(f"\n✅ Auto-detection successful! Found {len(monitorable_vars)} monitorable variables")
    return True

if __name__ == "__main__":
    test_auto_detection()