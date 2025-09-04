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
from typing import Dict, Optional, Any

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
            # Temporarily stop the process for memory reading
            import signal
            os.kill(self.pid, signal.SIGSTOP)
            os.waitpid(self.pid, 0)
            
            data = b''
            words_to_read = (size + 7) // 8  # Read in 8-byte chunks
            
            for i in range(words_to_read):
                addr = address + (i * 8)
                word = self.libc.ptrace(PTRACE_PEEKDATA, self.pid, addr, None)
                
                if word == -1:
                    # Check if it's a real error or just -1 data
                    errno = ctypes.get_errno()
                    if errno != 0:
                        break
                
                # Convert to bytes (little endian)
                word_bytes = struct.pack('<Q', word & 0xFFFFFFFFFFFFFFFF)
                data += word_bytes
            
            # Resume the process
            PTRACE_CONT = 7
            self.libc.ptrace(PTRACE_CONT, self.pid, None, None)
            
            # Return only the requested number of bytes
            return data[:size] if data else None
            
        except Exception as e:
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
                    return None
                return value
            except:
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
                if any(var in name for var in ['ego_speed', 'collision_risk', 'current_lane', 'steering_angle', 'warning_active', 'brake_pressure']):
                    relevant_vars.append((name, addr))
                    print(f"  {name}: 0x{addr:x}")
            
            print(f"Found {len(relevant_vars)} relevant monitoring variables")
                    
        except Exception as e:
            print(f"Symbol table build failed: {e}")
    
    def get_process_base_address(self) -> Optional[int]:
        """Get the base address of the process from memory maps."""
        if not self.process:
            return None
        
        try:
            with open(f'/proc/{self.process.pid}/maps', 'r') as f:
                for line in f:
                    if 'main_bin' in line and 'r--p' in line:  # Look for read-only executable mapping
                        addr_range = line.split()[0]
                        start_addr = addr_range.split('-')[0]
                        return int(start_addr, 16)
        except Exception as e:
            print(f"Error reading process memory maps: {e}")
        
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
            
            # Give it time to initialize
            import time
            time.sleep(1)
            
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
    
    def read_variable(self, var_name: str, var_type: str) -> Optional[Any]:
        """Read a variable value."""
        if not self.reader:
            print(f"No ptrace reader available for {var_name}")
            return None
            
        if var_name not in self.symbol_table:
            print(f"Variable {var_name} not found in symbol table")
            return None
        
        static_address = self.symbol_table[var_name]
        
        # Adjust address using process base address
        if self.base_address:
            adjusted_address = self.base_address + static_address
        else:
            adjusted_address = static_address
        
        try:
            if var_type == 'int':
                value = self.reader.read_int32(adjusted_address)
            elif var_type == 'float':
                value = self.reader.read_float(adjusted_address)
            elif var_type == 'double':
                value = self.reader.read_double(adjusted_address)
            elif var_type == 'bool':
                value = self.reader.read_bool(adjusted_address)
            else:
                value = self.reader.read_int32(adjusted_address)  # Default
            
            return value
                
        except Exception as e:
            print(f"Variable read failed for {var_name}: {e}")
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
            
            # Parse the latest status block
            variables = {}
            for line in lines:
                if "Ego Speed:" in line:
                    try:
                        speed_str = line.split("Ego Speed:")[1].split("km/h")[0].strip()
                        variables['ego_speed'] = float(speed_str)
                    except:
                        pass
                elif "Collision Risk:" in line:
                    try:
                        risk_str = line.split("Collision Risk:")[1].split("%")[0].strip()
                        variables['collision_risk'] = int(risk_str)
                    except:
                        pass
                elif "Current Lane:" in line:
                    try:
                        lane_str = line.split("Current Lane:")[1].split("(")[0].strip()
                        variables['current_lane'] = int(lane_str)
                    except:
                        pass
                elif "Warning Active:" in line:
                    try:
                        warning_str = line.split("Warning Active:")[1].strip()
                        variables['warning_active'] = "YES" in warning_str
                    except:
                        pass
                elif "Brake Pressure:" in line:
                    try:
                        brake_str = line.split("Brake Pressure:")[1].split("%")[0].strip()
                        variables['brake_pressure'] = float(brake_str)
                    except:
                        pass
            
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
    
    # Define variables to monitor
    variables = {
        'ego_speed': 'float',
        'collision_risk': 'int',
        'current_lane': 'int',
        'warning_active': 'bool',
        'brake_pressure': 'float'
    }
    
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