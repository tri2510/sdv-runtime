#!/usr/bin/env python3
"""
Automatic C++ Variable Detection System
Automatically detects atomic variables in C++ code and binary symbols.
"""

import re
import subprocess
import struct
import ctypes
import os
import time
import signal
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path

class AutoVariableDetector:
    """Automatically detect C++ variables and their types."""
    
    def __init__(self):
        # SDV minimal type set - only basic types without _t suffix
        self.variable_patterns = {
            # SDV atomic types
            'atomic_int': (r'std::atomic<int>\s+(\w+)', 'int', 4),
            'atomic_char': (r'std::atomic<char>\s+(\w+)', 'char', 1),
            'atomic_float': (r'std::atomic<float>\s+(\w+)', 'float', 4),
            'atomic_double': (r'std::atomic<double>\s+(\w+)', 'double', 8),
            'atomic_bool': (r'std::atomic<bool>\s+(\w+)', 'bool', 1),

            # SDV regular types
            'int_var': (r'\bint\s+(\w+)', 'int', 4),
            'char_var': (r'\bchar\s+(\w+)', 'char', 1),
            'float_var': (r'\bfloat\s+(\w+)', 'float', 4),
            'double_var': (r'\bdouble\s+(\w+)', 'double', 8),
            'bool_var': (r'\bbool\s+(\w+)', 'bool', 1),
        }
    
    def extract_variables_from_source(self, cpp_code: str) -> List[Dict[str, Any]]:
        """Extract variable declarations from C++ source code."""
        detected_vars = []
        
        for pattern_name, (regex, var_type, size_bytes) in self.variable_patterns.items():
            matches = re.findall(regex, cpp_code)
            for match in matches:
                # All patterns now return just variable name (simplified)
                var_name = match if isinstance(match, str) else match
                actual_type = var_type
                actual_size = size_bytes

                # Skip common keywords and function names
                if var_name.lower() in ['main', 'return', 'if', 'for', 'while', 'do']:
                    continue

                detected_vars.append({
                    'name': var_name,
                    'type': actual_type,
                    'size_bytes': actual_size,
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

                            # Also store simple name for namespaced variables (e.g., FCW::front_distance -> front_distance)
                            if '::' in symbol_name:
                                simple_name = symbol_name.split('::')[-1]
                                symbol_table[simple_name] = addr
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
            
            # Look for structured matches (namespaced or static symbols)
            for symbol_name, addr in binary_symbols.items():
                if self._symbol_matches(var_name, symbol_name):
                    var_info['symbol_address'] = addr
                    var_info['found_in_binary'] = True
                    var_info['symbol_name'] = symbol_name
                    matched_vars.append(var_info)
                    break
            else:
                var_info['found_in_binary'] = False
                matched_vars.append(var_info)
        
        return matched_vars
    
    @staticmethod
    def _symbol_matches(var_name: str, symbol_name: str) -> bool:
        if symbol_name == var_name:
            return True
        if symbol_name.endswith(f"::{var_name}"):
            return True
        if symbol_name.endswith(f".{var_name}"):
            return True
        return False
    
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
        self.base_address = None
    
    def attach(self) -> bool:
        """Attach to process."""
        try:
            result = self.libc.ptrace(self.PTRACE_ATTACH, self.pid, 0, 0)
            if result == 0:
                self.attached = True
                import time
                time.sleep(0.2)  # Give more time for attach
                
                # Get process base address while process is stopped
                self.base_address = self.get_process_base_address()
                
                # Continue the process after getting base address
                PTRACE_CONT = 7
                self.libc.ptrace(PTRACE_CONT, self.pid, 0, 0)
                
                return True
        except Exception as e:
            print(f"Failed to attach to PID {self.pid}: {e}")
        return False
    
    def get_data_section_address(self) -> Optional[int]:
        """Get the actual memory address where the data section is loaded."""
        try:
            with open(f'/proc/{self.pid}/maps', 'r') as f:
                lines = f.readlines()
                print(f"   📄 Looking for data section in {len(lines)} memory map entries")
                
                # First pass: look for the main executable binary name in maps
                binary_name = None
                for line in lines:
                    if 'r-xp' in line and '/' in line:  # Executable section with path
                        parts = line.split()
                        if len(parts) >= 6:
                            path = parts[5]
                            if 'main_bin' in path or 'autonomous_vehicle_system' in path or 'app' in path:
                                binary_name = Path(path).name
                                break
                
                print(f"   🔍 Detected binary name: {binary_name}")
                
                # Second pass: find data section for this binary
                for i, line in enumerate(lines):
                    if 'rw-p' in line and (binary_name and binary_name in line):
                        parts = line.split()
                        if len(parts) >= 6:
                            addr_range = parts[0]
                            permissions = parts[1]
                            file_offset = parts[2]
                            start_addr = addr_range.split('-')[0]
                            data_addr = int(start_addr, 16)
                            
                            print(f"   📍 Data section: 0x{data_addr:x} ({permissions}) file_offset={file_offset}")
                            
                            # Dynamically detect ELF data section start address using readelf
                            elf_data_start = self._get_elf_data_start(binary_name)
                            if not elf_data_start:
                                elf_data_start = 0x4000  # Default fallback for simple g++ binaries
                            
                            print(f"   🏠 Data section base: 0x{data_addr:x}, ELF data starts at 0x{elf_data_start:x}")
                            return data_addr - elf_data_start  # This will be our "base" for calculations
                            
        except Exception as e:
            print(f"Error getting data section address: {e}")
        return None
    
    def _get_elf_data_start(self, binary_name: str) -> Optional[int]:
        """Get ELF data section start address using readelf."""
        try:
            # Find the binary path from the running process maps
            with open(f'/proc/{self.pid}/maps', 'r') as f:
                for line in f:
                    if binary_name in line and 'r-xp' in line:
                        parts = line.split()
                        if len(parts) >= 6:
                            binary_path = parts[5]
                            break
                else:
                    print(f"   ❌ Could not find binary path for {binary_name}")
                    return None
            
            # Use readelf to get data section address
            result = subprocess.run(['readelf', '-S', binary_path], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if '.data' in line and 'PROGBITS' in line:
                        parts = line.split()
                        for part in parts:
                            if part.startswith('00000000'):  # ELF address format
                                addr = int(part, 16)
                                print(f"   🔧 Detected ELF .data start: 0x{addr:x}")
                                return addr
            
            print(f"   ❌ Could not detect ELF data start for {binary_path}")
            return None
            
        except Exception as e:
            print(f"   ❌ Error detecting ELF data start: {e}")
            return None
    
    def get_process_base_address(self) -> Optional[int]:
        """Get base address for variable calculations."""
        return self.get_data_section_address()
    
    def detach(self):
        """Detach from process."""
        if self.attached:
            try:
                self.libc.ptrace(self.PTRACE_DETACH, self.pid, 0, 0)
                self.attached = False
            except:
                pass
    
    def read_variable_value(self, var_info: Dict[str, Any]) -> Optional[Union[int, float, bool]]:
        """Read variable value using the WORKING /proc/pid/mem approach first."""
        if not self.attached or not self.base_address:
            return None
        
        try:
            symbol_addr = var_info['symbol_address'] 
            var_type = var_info['type']
            size_bytes = var_info['size_bytes']
            
            # Calculate actual memory address: base + symbol offset
            actual_addr = self.base_address + symbol_addr
            
            # Method 1: Try /proc/pid/mem FIRST (the original working approach)
            try:
                with open(f'/proc/{self.pid}/mem', 'rb') as mem_file:
                    mem_file.seek(actual_addr)
                    
                    if var_type == 'int':
                        data = mem_file.read(4)
                        if len(data) == 4:
                            return struct.unpack('<i', data)[0]
                    elif var_type == 'float':
                        data = mem_file.read(4)
                        if len(data) == 4:
                            value = struct.unpack('<f', data)[0]
                            # Check for reasonable float values
                            import math
                            if not (math.isnan(value) or math.isinf(value)):
                                return value
                    elif var_type == 'bool':
                        data = mem_file.read(1)
                        if len(data) == 1:
                            return bool(data[0])
                            
            except (OSError, IOError):
                # Method 2: Fall back to ptrace ONLY if /proc/mem fails
                try:
                    # Temporarily stop the process to read memory safely
                    os.kill(self.pid, signal.SIGSTOP)
                    time.sleep(0.01)  # Brief pause for stop to take effect
                    
                    # Read memory data while process is stopped
                    data = self.libc.ptrace(self.PTRACE_PEEKDATA, self.pid, actual_addr, 0)
                    
                    # Continue the process immediately
                    os.kill(self.pid, signal.SIGCONT)
                    
                    if data == -1:
                        return None
                    
                    # Parse based on detected type using ptrace data
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
                    elif var_type == 'bool':
                        return bool(data & 0xFF)
                        
                except Exception as ptrace_error:
                    print(f"Ptrace fallback failed for {var_info['name']}: {ptrace_error}")
                    return None
            
            # If we get here, both methods failed
            return None
        
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
    
    # Test with SDV types test program
    base_dir = Path("/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork")
    cpp_file = base_dir / "test_sdv_types.cpp"
    binary_file = base_dir / "test_sdv_types"
    
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
