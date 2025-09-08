#!/usr/bin/env python3
"""
Direct memory access using ptrace system calls.
This bypasses /proc/pid/mem restrictions and provides reliable memory reading.
"""

import ctypes
import ctypes.util
import os
import signal
import struct
import subprocess
from typing import Dict, Optional, Any, List

# ptrace constants
PTRACE_ATTACH = 16
PTRACE_DETACH = 17
PTRACE_PEEKDATA = 2
PTRACE_PEEKTEXT = 1

class PtraceMemoryReader:
    """Direct memory reader using ptrace system calls."""
    
    def __init__(self, pid: int):
        self.pid = pid
        self.attached = False
        
        # Load libc
        libc_name = ctypes.util.find_library("c")
        self.libc = ctypes.CDLL(libc_name)
        
        # Set up ptrace function
        self.libc.ptrace.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
        self.libc.ptrace.restype = ctypes.c_long
        
    def attach(self) -> bool:
        """Attach to the target process."""
        try:
            result = self.libc.ptrace(PTRACE_ATTACH, self.pid, None, None)
            if result == -1:
                print(f"Failed to attach to PID {self.pid}")
                return False
            
            # Wait for process to stop
            os.waitpid(self.pid, 0)
            self.attached = True
            print(f"Successfully attached to PID {self.pid}")
            
            # Resume the process so it can continue running
            PTRACE_CONT = 7
            self.libc.ptrace(PTRACE_CONT, self.pid, None, None)
            print(f"Process PID {self.pid} resumed and running")
            
            return True
            
        except Exception as e:
            print(f"Attach failed: {e}")
            return False
    
    def detach(self):
        """Detach from the target process."""
        if self.attached:
            self.libc.ptrace(PTRACE_DETACH, self.pid, None, None)
            self.attached = False
            print(f"Detached from PID {self.pid}")
    
    def read_memory(self, address: int, size: int) -> Optional[bytes]:
        """Read memory from the target process."""
        if not self.attached:
            return None
        
        try:
            # Check if process is still alive before reading
            try:
                os.kill(self.pid, 0)  # Signal 0 checks if process exists
            except OSError:
                print(f"Process {self.pid} no longer exists")
                return None
            
            # Temporarily stop the process for memory reading - more gentle approach
            try:
                os.kill(self.pid, signal.SIGSTOP)
                # Wait for stop with timeout
                pid, status = os.waitpid(self.pid, os.WNOHANG)
                if pid == 0:
                    # Process didn't stop immediately, wait a bit more
                    import time
                    time.sleep(0.001)  # 1ms
                    pid, status = os.waitpid(self.pid, os.WNOHANG)
            except ProcessLookupError:
                print(f"Process {self.pid} died during SIGSTOP")
                return None
            
            data = b''
            words_to_read = (size + 7) // 8  # Read in 8-byte chunks
            
            for i in range(words_to_read):
                addr = address + (i * 8)
                
                # Clear errno before ptrace call
                ctypes.set_errno(0)
                word = self.libc.ptrace(PTRACE_PEEKDATA, self.pid, addr, None)
                
                if word == -1:
                    # Check if it's a real error or just -1 data
                    errno = ctypes.get_errno()
                    if errno != 0:
                        print(f"ptrace error at 0x{addr:x}: errno {errno}")
                        break
                
                # Convert to bytes (little endian)  
                word_bytes = struct.pack('<Q', word & 0xFFFFFFFFFFFFFFFF)
                data += word_bytes
            
            # Resume the process - critical to always do this
            PTRACE_CONT = 7
            result = self.libc.ptrace(PTRACE_CONT, self.pid, None, None)
            if result == -1:
                print(f"Warning: Failed to resume process {self.pid}")
            
            # Return only the requested number of bytes
            return data[:size] if data else None
            
        except Exception as e:
            print(f"Memory read exception: {e}")
            # Make sure to resume process even if there's an error
            try:
                PTRACE_CONT = 7
                self.libc.ptrace(PTRACE_CONT, self.pid, None, None)
            except:
                pass
            return None
    
    def read_int32(self, address: int) -> Optional[int]:
        """Read a 32-bit integer from memory, handling atomic<int>."""
        # std::atomic<int> stores the value directly at the address
        data = self.read_memory(address, 4)
        if data and len(data) >= 4:
            try:
                value = struct.unpack('<i', data[:4])[0]
                return value
            except:
                return None
        return None
    
    def read_float(self, address: int) -> Optional[float]:
        """Read a 32-bit float from memory, handling atomic<float>."""
        # std::atomic<float> stores the value directly at the address  
        data = self.read_memory(address, 4)
        if data and len(data) >= 4:
            try:
                value = struct.unpack('<f', data[:4])[0]
                # Check for NaN or infinite values
                import math
                if math.isnan(value) or math.isinf(value):
                    print(f"Warning: Invalid float value at 0x{address:x}: {value}")
                    return None
                # Round to reasonable precision for display
                return round(value, 2)
            except Exception as e:
                print(f"Float read error at 0x{address:x}: {e}")
                return None
        return None
    
    def read_double(self, address: int) -> Optional[float]:
        """Read a 64-bit double from memory."""
        data = self.read_memory(address, 8)
        if data and len(data) >= 8:
            return struct.unpack('<d', data[:8])[0]
        return None
    
    def read_bool(self, address: int) -> Optional[bool]:
        """Read a boolean from memory, handling atomic<bool>."""
        # std::atomic<bool> is typically 1 byte
        data = self.read_memory(address, 1)
        if data and len(data) >= 1:
            return data[0] != 0
        return None

class MemoryVariableMonitor:
    """High-level variable monitoring using ptrace."""
    
    def __init__(self, binary_path: str):
        self.binary_path = binary_path
        self.symbol_table = {}
        self.process = None
        self.reader = None
        self.base_address = None
        
    def set_symbol_mappings(self, variable_mappings: Dict[str, int]):
        """Set symbol mappings from auto-detection system."""
        print(f"🔗 Setting {len(variable_mappings)} symbol mappings from auto-detection")
        for var_name, address in variable_mappings.items():
            self.symbol_table[var_name] = address
            print(f"  📍 {var_name}: 0x{address:x}")
    
    def build_symbol_table(self):
        """Build symbol table from binary."""
        try:
            result = subprocess.run(['nm', self.binary_path], capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                parts = line.split()
                if len(parts) >= 3 and parts[1] in ['D', 'B', 'd', 'b']:  # Data symbols
                    address = int(parts[0], 16)
                    symbol_name = parts[2]
                    self.symbol_table[symbol_name] = address
                    
            print(f"Found {len(self.symbol_table)} symbols")
            
            # Show relevant variables
            relevant_vars = []
            for name, addr in self.symbol_table.items():
                # Show all data symbols (no hardcoded filtering)
                relevant_vars.append((name, addr))
                print(f"  {name}: 0x{addr:x}")
            
            print(f"Found {len(relevant_vars)} relevant monitoring variables")
                    
        except Exception as e:
            print(f"Symbol table build failed: {e}")
    
    def analyze_memory_layout(self) -> Dict[str, int]:
        """Analyze the complete memory layout to create smart address mapping."""
        if not self.process:
            return {}
        
        try:
            binary_name = os.path.basename(self.binary_path)
            print(f"🧠 SMART MEMORY MAPPING: Analyzing {binary_name}")
            
            memory_regions = {}
            with open(f'/proc/{self.process.pid}/maps', 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 6:
                        addr_range = parts[0]
                        permissions = parts[1] 
                        offset = parts[2]
                        path = parts[5] if len(parts) > 5 else ""
                        
                        # Look for our binary in memory maps
                        if binary_name in path or self.binary_path in path:
                            start_addr = int(addr_range.split('-')[0], 16)
                            end_addr = int(addr_range.split('-')[1], 16)
                            
                            # Categorize memory regions
                            if 'r-x' in permissions:
                                memory_regions['text'] = start_addr
                                print(f"📍 TEXT section: 0x{start_addr:x}-0x{end_addr:x}")
                            elif 'r--' in permissions:
                                memory_regions['rodata'] = start_addr  
                                print(f"📖 RODATA section: 0x{start_addr:x}-0x{end_addr:x}")
                            elif 'rw-' in permissions:
                                if 'data' not in memory_regions:
                                    memory_regions['data'] = start_addr
                                    print(f"📊 DATA section: 0x{start_addr:x}-0x{end_addr:x}")
                                else:
                                    memory_regions['bss'] = start_addr
                                    print(f"🗃️  BSS section: 0x{start_addr:x}-0x{end_addr:x}")
            
            print(f"✅ Memory layout analysis complete: {len(memory_regions)} regions found")
            return memory_regions
                        
        except Exception as e:
            print(f"Error analyzing memory layout: {e}")
        
        return {}

    def get_process_base_address(self) -> Optional[int]:
        """Get the ACTUAL runtime base address from process memory maps."""
        layout = self.analyze_memory_layout()
        self.memory_layout = layout
        
        # Prefer data section, fallback to text section
        if 'data' in layout:
            print(f"✅ Using DATA section base: 0x{layout['data']:x}")
            return layout['data']
        elif 'bss' in layout:
            print(f"✅ Using BSS section base: 0x{layout['bss']:x}")
            return layout['bss']
        elif 'text' in layout:
            print(f"⚠️  Using TEXT section base: 0x{layout['text']:x}")
            return layout['text']
        else:
            print(f"❌ No usable memory sections found")
            return None
    
    def start_process(self) -> bool:
        """Start the target process."""
        try:
            # Start process with stdout capture for reliable variable parsing
            self.process = subprocess.Popen([self.binary_path], 
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           text=True,
                                           bufsize=1,  # Line buffered
                                           universal_newlines=True)
            print(f"Started process PID {self.process.pid}")
            
            # CRITICAL: Wait for C++ global variable initialization
            import time
            print("⏳ Waiting for C++ global variable initialization...")
            time.sleep(3.0)  # Increased delay for proper variable initialization
            
            # Check if process is still alive after initialization
            if self.process.poll() is not None:
                print(f"❌ Process exited during initialization with code {self.process.returncode}")
                return False
            print(f"✅ Process {self.process.pid} initialized successfully")
            
            # Get the process base address from memory maps
            self.base_address = self.get_process_base_address()
            print(f"Process base address: 0x{self.base_address:x}" if self.base_address else "Base address not found")
            
            # Create ptrace reader as backup
            self.reader = PtraceMemoryReader(self.process.pid)
            ptrace_attached = self.reader.attach()
            
            print(f"Process started successfully, ptrace backup: {ptrace_attached}")
            return True
            
        except Exception as e:
            print(f"Process start failed: {e}")
            return False
    
    def read_int_from_proc_mem(self, address: int) -> Optional[int]:
        """Read int directly from /proc/pid/mem."""
        try:
            import struct
            # Try to read with os.pread for better permission handling
            try:
                import os
                fd = os.open(f'/proc/{self.process.pid}/mem', os.O_RDONLY)
                data = os.pread(fd, 4, address)
                os.close(fd)
                if len(data) == 4:
                    value = struct.unpack('i', data)[0]
                    return value
            except:
                # Fallback to regular file reading
                with open(f'/proc/{self.process.pid}/mem', 'rb') as mem_file:
                    mem_file.seek(address)
                    data = mem_file.read(4)  # 4 bytes for int
                    if len(data) == 4:
                        value = struct.unpack('i', data)[0]
                        return value
        except Exception as e:
            print(f"Direct /proc/mem read failed at 0x{address:x}: {e}")
        return None

    def read_float_from_proc_mem(self, address: int) -> Optional[float]:
        """Read float directly from /proc/pid/mem (more reliable than ptrace)."""
        try:
            import struct
            # Try to read with os.pread for better permission handling
            try:
                import os
                fd = os.open(f'/proc/{self.process.pid}/mem', os.O_RDONLY)
                data = os.pread(fd, 4, address)
                os.close(fd)
                if len(data) == 4:
                    value = struct.unpack('f', data)[0]
                    return value
            except:
                # Fallback to regular file reading
                with open(f'/proc/{self.process.pid}/mem', 'rb') as mem_file:
                    mem_file.seek(address)
                    data = mem_file.read(4)  # 4 bytes for float
                    if len(data) == 4:
                        value = struct.unpack('f', data)[0]
                        return value
        except Exception as e:
            print(f"Direct /proc/mem read failed at 0x{address:x}: {e}")
        return None

    def smart_calculate_runtime_address(self, var_name: str, static_address: int) -> List[int]:
        """Smart address calculation that adapts to any binary's memory layout."""
        candidate_addresses = []
        
        if not hasattr(self, 'memory_layout'):
            self.memory_layout = {}
        
        print(f"🧠 SMART CALC: {var_name} static=0x{static_address:x}")
        
        # Method 1: Use actual memory layout analysis
        if self.base_address and self.memory_layout:
            # Try data section mapping first
            if 'data' in self.memory_layout:
                data_base = self.memory_layout['data']
                # Try different static base calculations
                for static_base in [0x6000, 0x5000, 0x4000, 0x3000, 0x2000, 0x1000]:
                    if static_address >= static_base:
                        offset = static_address - static_base
                        runtime_addr = data_base + offset
                        candidate_addresses.append(runtime_addr)
                        print(f"   📊 DATA method (base=0x{static_base:x}): 0x{runtime_addr:x}")
                        break
            
            # Try BSS section mapping
            if 'bss' in self.memory_layout:
                bss_base = self.memory_layout['bss'] 
                for static_base in [0x6000, 0x5000, 0x4000]:
                    if static_address >= static_base:
                        offset = static_address - static_base
                        runtime_addr = bss_base + offset
                        candidate_addresses.append(runtime_addr)
                        print(f"   🗃️  BSS method (base=0x{static_base:x}): 0x{runtime_addr:x}")
                        break
            
            # Try text section + offset (for some binaries)
            if 'text' in self.memory_layout:
                text_base = self.memory_layout['text']
                runtime_addr = text_base + static_address
                candidate_addresses.append(runtime_addr)
                print(f"   📍 TEXT+offset method: 0x{runtime_addr:x}")
        
        # Method 2: Legacy calculation methods as fallback
        if self.base_address:
            # Classic method with different base addresses
            for static_base in [0x6000, 0x5000, 0x4000, 0x3000]:
                if static_address >= static_base:
                    offset = static_address - static_base
                    runtime_addr = self.base_address + offset
                    candidate_addresses.append(runtime_addr)
                    print(f"   🔧 Legacy method (base=0x{static_base:x}): 0x{runtime_addr:x}")
                    break
            
            # Alternative calculations
            alt_addresses = [
                self.base_address + static_address,  # Direct offset
                self.base_address + (static_address & 0xFFF),  # Only lower bits
                self.base_address + (static_address & 0x1FFF), # Lower 13 bits  
            ]
            candidate_addresses.extend(alt_addresses)
            print(f"   ⚡ Alternative methods: {[hex(a) for a in alt_addresses]}")
        
        # Method 3: Direct static address (no ASLR or PIE disabled)
        candidate_addresses.append(static_address)
        print(f"   📍 Static address: 0x{static_address:x}")
        
        # Remove duplicates while preserving order
        unique_addresses = []
        for addr in candidate_addresses:
            if addr not in unique_addresses:
                unique_addresses.append(addr)
        
        print(f"   ✅ Total candidates: {len(unique_addresses)}")
        return unique_addresses

    def read_variable(self, var_name: str, var_type: str) -> Optional[Any]:
        """Read a variable value with proper ASLR-aware address calculation."""
        if not self.reader:
            print(f"No ptrace reader available for {var_name}")
            return None
            
        if var_name not in self.symbol_table:
            print(f"Variable {var_name} not found in symbol table")
            return None
        
        static_address = self.symbol_table[var_name]
        
        # SMART ADDRESS CALCULATION: Generate all possible runtime addresses
        candidate_addresses = self.smart_calculate_runtime_address(var_name, static_address)
        
        # For float values, use direct /proc/pid/mem reading (more reliable)
        if var_type == 'float':
            print(f"🔄 Reading float {var_name} using SMART /proc/pid/mem method...")
            
            for i, address in enumerate(candidate_addresses):
                value = self.read_float_from_proc_mem(address)
                if value is not None and value == value:  # Not NaN
                    print(f"✅ SMART float read succeeded for {var_name}: {value} at 0x{address:x} (method #{i+1})")
                    return value
            
            print(f"❌ All SMART methods failed for float {var_name}")
            return None
        
        # For integer values, use direct /proc/pid/mem reading (more reliable than ptrace)
        if var_type == 'int':
            print(f"🔄 Reading int {var_name} using SMART /proc/pid/mem method...")
            
            for i, address in enumerate(candidate_addresses):
                value = self.read_int_from_proc_mem(address)
                if value is not None:
                    print(f"✅ SMART int read succeeded for {var_name}: {value} at 0x{address:x} (method #{i+1})")
                    return value
            
            print(f"❌ All SMART methods failed for int {var_name}")
            return None
        
        # For other types (double, bool), try smart addressing with ptrace
        print(f"🔄 Reading {var_type} {var_name} using SMART ptrace method...")
        
        for i, address in enumerate(candidate_addresses):
            try:
                if var_type == 'double':
                    value = self.reader.read_double(address)
                elif var_type == 'bool':
                    value = self.reader.read_bool(address)
                else:
                    value = self.reader.read_int32(address)  # Default
                
                if value is not None:
                    print(f"✅ SMART {var_type} read succeeded for {var_name}: {value} at 0x{address:x} (method #{i+1})")
                    return value
                    
            except Exception as e:
                print(f"   ⚠️  Method #{i+1} failed at 0x{address:x}: {e}")
                continue
        
        print(f"❌ All SMART methods failed for {var_type} {var_name}")
        return None
    
    def parse_stdout_variables(self) -> Dict[str, Any]:
        """Parse variables from stdout - more reliable than memory reading."""
        if not self.process or not self.process.stdout:
            return {}
        
        import select
        import sys
        
        # Check if there's data available to read (non-blocking)
        if hasattr(select, 'select'):
            ready, _, _ = select.select([self.process.stdout], [], [], 0)
            if not ready:
                return {}
        
        try:
            # Read available lines
            lines = []
            while True:
                line = self.process.stdout.readline()
                if not line:
                    break
                lines.append(line.strip())
                if len(lines) > 20:  # Limit to avoid blocking
                    break
            
            # Generic stdout parsing - no hardcoded variable patterns
            variables = {}
            # Note: Removed all hardcoded parsing patterns - rely on memory-based variable reading instead
            
            return variables
            
        except Exception as e:
            print(f"Stdout parsing error: {e}")
            return {}

    def monitor_variables(self, variables: Dict[str, str]) -> Dict[str, Any]:
        """Monitor multiple variables using pure memory reading."""
        # Pure ptrace memory reading approach (no stdout parsing)
        results = {}
        for var_name, var_type in variables.items():
            value = self.read_variable(var_name, var_type)
            if value is not None:
                results[var_name] = value
        
        if results:
            # Only print every 5th read to reduce spam
            if not hasattr(self, 'read_count'):
                self.read_count = 0
            self.read_count += 1
            if self.read_count % 5 == 0:
                print(f"[Read #{self.read_count}] Memory: {results}")
        else:
            if not hasattr(self, 'read_count'):
                self.read_count = 0
            self.read_count += 1
            if self.read_count % 10 == 0:
                print(f"[Read #{self.read_count}] Memory: No variables available")
                
        return results
    
    def cleanup(self):
        """Clean up resources."""
        if self.reader:
            self.reader.detach()
        if self.process:
            self.process.terminate()
            self.process.wait()

def test_ptrace_monitoring():
    """Test the ptrace-based monitoring."""
    binary_path = "/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/kuksa-syncer/app/main_bin"
    
    monitor = MemoryVariableMonitor(binary_path)
    monitor.build_symbol_table()
    
    if not monitor.start_process():
        print("Failed to start monitoring")
        return
    
    # Auto-detect variables to monitor (no hardcoded values)
    from universal_auto_detector import UniversalAutoDetector, create_variable_list_for_syncer
    from pathlib import Path
    
    detector = UniversalAutoDetector()
    project_dir = Path(binary_path).parent
    project_vars, _ = detector.auto_detect_project_variables(project_dir)
    
    variables = {}
    for var in project_vars:
        if var['found_in_binary']:
            variables[var['name']] = var['type']
    
    print(f"Auto-detected {len(variables)} variables: {list(variables.keys())}")
    
    print(f"\n=== Starting variable monitoring ===")
    
    try:
        for i in range(10):
            values = monitor.monitor_variables(variables)
            print(f"[{i+1}] Variables: {values}")
            
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        monitor.cleanup()

if __name__ == "__main__":
    test_ptrace_monitoring()