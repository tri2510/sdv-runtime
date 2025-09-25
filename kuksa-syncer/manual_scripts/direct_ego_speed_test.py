#!/usr/bin/env python3
import subprocess
import time
import ctypes
import struct
import os
from pathlib import Path

# Start the cmake-multidir program
print("🚀 Starting cmake-multidir project...")
proc = subprocess.Popen(['/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp-projects/cmake-multidir/build/multidir_system'], 
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
pid = proc.pid
print(f"📍 PID: {pid}")

# Give it time to start
time.sleep(3)

# Try to read the ego_speed memory directly
print("🔍 Attempting direct memory read of ego_speed...")

try:
    # Open the process memory
    mem_file = f"/proc/{pid}/mem"
    maps_file = f"/proc/{pid}/maps"
    
    # Get the base address from maps
    with open(maps_file, 'r') as f:
        maps = f.read()
        
    # Find the executable mapping
    for line in maps.split('\n'):
        if 'multidir_system' in line and 'r-xp' in line:
            base_addr = int(line.split('-')[0], 16)
            print(f"📍 Base address: 0x{base_addr:x}")
            break
    
    # ego_speed symbol offset (from nm): 0x6160
    ego_speed_offset = 0x6160
    ego_speed_addr = base_addr + ego_speed_offset
    print(f"📍 ego_speed address: 0x{ego_speed_addr:x}")
    
    # Monitor for several cycles
    print("📊 Monitoring ego_speed values:")
    for i in range(10):
        try:
            with open(mem_file, 'rb') as mem:
                mem.seek(ego_speed_addr)
                data = mem.read(4)  # std::atomic<float> is 4 bytes
                
                if len(data) == 4:
                    value = struct.unpack('f', data)[0]
                    print(f"🎯 Sample {i+1}: ego_speed = {value:.1f} km/h")
                else:
                    print(f"⚠️  Sample {i+1}: Could not read memory")
                    
        except Exception as e:
            print(f"⚠️  Sample {i+1}: Memory read error: {e}")
            
        time.sleep(2)
    
    print("✅ Direct memory monitoring complete")
    
except Exception as e:
    print(f"❌ Error: {e}")
    
finally:
    # Cleanup
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except:
        proc.kill()
        
    print("🧹 Process terminated")
