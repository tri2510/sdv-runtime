#!/usr/bin/env python3
"""
Universal Automatic C++ Variable Detection System
Fully automatic detection with no hardcoded values.
Works with any C++ project: cmake, makefile, or direct g++ builds.
"""

import re
import subprocess
import struct
import os
import time
import signal
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import glob

class UniversalAutoDetector:
    """Universal automatic C++ variable detection with zero hardcoded values."""
    
    def __init__(self):
        # Comprehensive atomic type patterns - covers ALL std::atomic types
        self.atomic_patterns = {
            # Basic atomic types
            r'std::atomic<int>\s+(\w+)': ('int', 4),
            r'std::atomic<float>\s+(\w+)': ('float', 4),
            r'std::atomic<double>\s+(\w+)': ('double', 8),
            r'std::atomic<bool>\s+(\w+)': ('bool', 1),
            r'std::atomic<char>\s+(\w+)': ('char', 1),
            
            # Extended integer types
            r'std::atomic<int8_t>\s+(\w+)': ('int8_t', 1),
            r'std::atomic<int16_t>\s+(\w+)': ('int16_t', 2),
            r'std::atomic<int32_t>\s+(\w+)': ('int32_t', 4),
            r'std::atomic<int64_t>\s+(\w+)': ('int64_t', 8),
            r'std::atomic<uint8_t>\s+(\w+)': ('uint8_t', 1),
            r'std::atomic<uint16_t>\s+(\w+)': ('uint16_t', 2),
            r'std::atomic<uint32_t>\s+(\w+)': ('uint32_t', 4),
            r'std::atomic<uint64_t>\s+(\w+)': ('uint64_t', 8),
            
            # Signed/unsigned variants
            r'std::atomic<signed\s+char>\s+(\w+)': ('signed_char', 1),
            r'std::atomic<unsigned\s+char>\s+(\w+)': ('unsigned_char', 1),
            r'std::atomic<signed\s+int>\s+(\w+)': ('signed_int', 4),
            r'std::atomic<unsigned\s+int>\s+(\w+)': ('unsigned_int', 4),
            r'std::atomic<short>\s+(\w+)': ('short', 2),
            r'std::atomic<unsigned\s+short>\s+(\w+)': ('unsigned_short', 2),
            r'std::atomic<long>\s+(\w+)': ('long', 8),
            r'std::atomic<unsigned\s+long>\s+(\w+)': ('unsigned_long', 8),
            r'std::atomic<long\s+long>\s+(\w+)': ('long_long', 8),
            r'std::atomic<unsigned\s+long\s+long>\s+(\w+)': ('unsigned_long_long', 8),
            
            # System types
            r'std::atomic<size_t>\s+(\w+)': ('size_t', 8),
            r'std::atomic<intptr_t>\s+(\w+)': ('intptr_t', 8),
            r'std::atomic<uintptr_t>\s+(\w+)': ('uintptr_t', 8),
            r'std::atomic<ptrdiff_t>\s+(\w+)': ('ptrdiff_t', 8),
            
            # Wide character types
            r'std::atomic<wchar_t>\s+(\w+)': ('wchar_t', 4),
            r'std::atomic<char16_t>\s+(\w+)': ('char16_t', 2),
            r'std::atomic<char32_t>\s+(\w+)': ('char32_t', 4),
        }
        
        # Also detect regular variables that could be monitored
        self.regular_patterns = {
            r'\bint\s+(\w+)(?:\s*=\s*[^;]+)?;': ('int', 4),
            r'\bfloat\s+(\w+)(?:\s*=\s*[^;]+)?;': ('float', 4),
            r'\bdouble\s+(\w+)(?:\s*=\s*[^;]+)?;': ('double', 8),
            r'\bbool\s+(\w+)(?:\s*=\s*[^;]+)?;': ('bool', 1),
            r'\bchar\s+(\w+)(?:\s*=\s*[^;]+)?;': ('char', 1),
        }
        
        # Skip these common keywords/identifiers
        self.skip_names = {
            'main', 'return', 'if', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
            'class', 'struct', 'namespace', 'using', 'typedef', 'template', 'public', 'private',
            'protected', 'const', 'static', 'extern', 'inline', 'virtual', 'override', 'final',
            'auto', 'decltype', 'nullptr', 'true', 'false', 'void', 'std', 'string', 'vector',
            'map', 'set', 'list', 'array', 'cout', 'cin', 'endl', 'flush', 'size', 'begin',
            'end', 'push_back', 'pop_back', 'insert', 'erase', 'clear', 'empty'
        }

    def find_all_source_files(self, project_dir: Path) -> List[Path]:
        """Find all C++ source files in the project."""
        source_files = []
        
        # Common C++ file extensions
        extensions = ['*.cpp', '*.cc', '*.cxx', '*.c++', '*.C', '*.h', '*.hpp', '*.hh', '*.hxx', '*.h++']
        
        for ext in extensions:
            # Search recursively for all source files
            pattern = str(project_dir / '**' / ext)
            files = glob.glob(pattern, recursive=True)
            source_files.extend([Path(f) for f in files])
        
        return source_files
    
    def extract_all_variables_from_sources(self, project_dir: Path) -> List[Dict[str, Any]]:
        """Extract ALL atomic and regular variables from ALL source files in project."""
        print(f"🔍 Scanning project directory: {project_dir}")
        
        source_files = self.find_all_source_files(project_dir)
        print(f"📄 Found {len(source_files)} source files")
        
        all_variables = []
        
        for source_file in source_files:
            try:
                with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                print(f"   📄 Processing: {source_file.name}")
                
                # Extract atomic variables
                for pattern, (var_type, size_bytes) in self.atomic_patterns.items():
                    matches = re.findall(pattern, content, re.MULTILINE)
                    for var_name in matches:
                        if var_name not in self.skip_names:
                            all_variables.append({
                                'name': var_name,
                                'type': var_type,
                                'size_bytes': size_bytes,
                                'is_atomic': True,
                                'source_file': str(source_file),
                                'pattern': pattern
                            })
                            print(f"      ⚛️  Found atomic: {var_name} ({var_type})")
                
                # Extract regular variables (as backup)
                for pattern, (var_type, size_bytes) in self.regular_patterns.items():
                    matches = re.findall(pattern, content, re.MULTILINE)
                    for var_name in matches:
                        if var_name not in self.skip_names:
                            # Only add if we don't already have it as atomic
                            existing_names = [v['name'] for v in all_variables]
                            if var_name not in existing_names:
                                all_variables.append({
                                    'name': var_name,
                                    'type': var_type,
                                    'size_bytes': size_bytes,
                                    'is_atomic': False,
                                    'source_file': str(source_file),
                                    'pattern': pattern
                                })
                                print(f"      📋 Found regular: {var_name} ({var_type})")
                
            except Exception as e:
                print(f"   ⚠️  Error reading {source_file}: {e}")
                continue
        
        # Remove duplicates, preferring atomic over regular
        unique_variables = {}
        for var in all_variables:
            name = var['name']
            if name not in unique_variables:
                unique_variables[name] = var
            else:
                # Prefer atomic variables
                if var['is_atomic'] and not unique_variables[name]['is_atomic']:
                    unique_variables[name] = var
        
        return list(unique_variables.values())
    
    def find_project_binary(self, project_dir: Path) -> Optional[Path]:
        """Find the compiled binary in the project - supports all build systems."""
        print(f"🔍 Looking for compiled binary in: {project_dir}")
        
        # Priority order for binary locations
        search_locations = [
            # CMake build directory
            project_dir / 'build',
            # Current directory
            project_dir,
            # Common output directories
            project_dir / 'bin',
            project_dir / 'output',
            project_dir / 'Debug',
            project_dir / 'Release',
        ]
        
        for location in search_locations:
            if not location.exists():
                continue
                
            print(f"   📂 Checking: {location}")
            
            # Look for executable files
            for file_path in location.iterdir():
                if file_path.is_file() and os.access(file_path, os.X_OK):
                    # Check if it's a reasonable binary (not script, minimum size)
                    if file_path.stat().st_size > 1000:  # At least 1KB
                        # Check if it's ELF binary (Unix/Linux)
                        try:
                            with open(file_path, 'rb') as f:
                                magic = f.read(4)
                                if magic == b'\x7fELF':  # ELF magic number
                                    print(f"   ✅ Found ELF binary: {file_path}")
                                    return file_path
                        except:
                            pass
        
        print("   ❌ No binary found")
        return None
    
    def extract_symbols_from_binary(self, binary_path: Path) -> Dict[str, int]:
        """Extract all symbols from binary using multiple tools."""
        print(f"🔧 Extracting symbols from: {binary_path}")
        symbol_table = {}
        
        # Try nm first (most reliable)
        try:
            result = subprocess.run(['nm', '-C', '-D', str(binary_path)], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if not line.strip():
                        continue
                    
                    parts = line.split()
                    if len(parts) >= 3:
                        addr_str, symbol_type, symbol_name = parts[0], parts[1], parts[2]
                        
                        # Look for data symbols (B=BSS, D=Data section, b=local BSS, d=local data)
                        if symbol_type.upper() in ['B', 'D', 'b', 'd']:
                            try:
                                addr = int(addr_str, 16)
                                symbol_table[symbol_name] = addr
                            except ValueError:
                                continue
            
            print(f"   📊 nm found {len(symbol_table)} data symbols")
        
        except Exception as e:
            print(f"   ⚠️  nm failed: {e}")
        
        # Try objdump as backup
        if len(symbol_table) < 5:  # If nm didn't find much, try objdump
            try:
                result = subprocess.run(['objdump', '-t', str(binary_path)], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if '.data' in line or '.bss' in line:
                            parts = line.split()
                            if len(parts) >= 6:
                                addr_str = parts[0]
                                symbol_name = parts[-1]
                                try:
                                    addr = int(addr_str, 16)
                                    symbol_table[symbol_name] = addr
                                except ValueError:
                                    continue
                
                print(f"   📊 objdump added {len(symbol_table)} total symbols")
            
            except Exception as e:
                print(f"   ⚠️  objdump failed: {e}")
        
        return symbol_table
    
    def match_variables_to_symbols(self, variables: List[Dict], symbols: Dict[str, int]) -> List[Dict]:
        """Match detected variables to binary symbols."""
        print(f"🔗 Matching {len(variables)} variables to {len(symbols)} symbols")
        
        matched_vars = []
        
        for var_info in variables:
            var_name = var_info['name']
            found = False
            
            # Direct match first
            if var_name in symbols:
                var_info['symbol_address'] = symbols[var_name]
                var_info['found_in_binary'] = True
                var_info['symbol_name'] = var_name
                matched_vars.append(var_info)
                print(f"   ✅ Direct match: {var_name} @ 0x{symbols[var_name]:x}")
                found = True
            else:
                for symbol_name, addr in symbols.items():
                    if self._symbol_matches(var_name, symbol_name):
                        var_info['symbol_address'] = addr
                        var_info['found_in_binary'] = True
                        var_info['symbol_name'] = symbol_name
                        matched_vars.append(var_info)
                        print(f"   ✅ Structured match: {var_name} -> {symbol_name} @ 0x{addr:x}")
                        found = True
                        break

                if not found:
                    var_info['found_in_binary'] = False
                    matched_vars.append(var_info)
                    print(f"   ❌ No match: {var_name}")
        
        monitorable = [v for v in matched_vars if v['found_in_binary']]
        print(f"🎯 Result: {len(monitorable)} variables ready for monitoring")
        
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
    
    def auto_detect_project_variables(self, project_dir: Path) -> Tuple[List[Dict], Optional[Path]]:
        """Fully automatic detection for any C++ project."""
        print(f"🚀 Starting UNIVERSAL auto-detection for: {project_dir}")
        
        # Step 1: Find all variables in source code
        variables = self.extract_all_variables_from_sources(project_dir)
        print(f"\n📋 Found {len(variables)} variables in source code:")
        for var in variables:
            atomic_marker = " [atomic]" if var['is_atomic'] else ""
            print(f"   - {var['name']} ({var['type']}){atomic_marker}")
        
        # Step 2: Find compiled binary
        binary_path = self.find_project_binary(project_dir)
        if not binary_path:
            print("❌ No binary found - project needs to be compiled first")
            return variables, None
        
        # Step 3: Extract symbols from binary
        symbols = self.extract_symbols_from_binary(binary_path)
        
        # Step 4: Match variables to symbols
        matched_vars = self.match_variables_to_symbols(variables, symbols)
        
        # Filter to monitorable variables
        monitorable_vars = [var for var in matched_vars if var['found_in_binary']]
        
        print(f"\n✅ DETECTION COMPLETE: {len(monitorable_vars)} variables ready for monitoring")
        for var in monitorable_vars:
            atomic_marker = " [atomic]" if var['is_atomic'] else ""
            print(f"   - {var['name']}: {var['type']} @ 0x{var['symbol_address']:x}{atomic_marker}")
        
        return monitorable_vars, binary_path

def create_variable_list_for_syncer(variables: List[Dict]) -> str:
    """Create comma-separated variable list for syncer.py."""
    var_names = [var['name'] for var in variables if var['found_in_binary']]
    return ','.join(var_names)

def test_universal_detection():
    """Test universal detection on cmake-multidir project."""
    print("=== TESTING UNIVERSAL AUTO-DETECTION ===\n")
    
    # Test with cmake-multidir
    project_dir = Path("/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp-projects/cmake-multidir")
    
    if not project_dir.exists():
        print(f"❌ Project directory not found: {project_dir}")
        return False
    
    detector = UniversalAutoDetector()
    variables, binary_path = detector.auto_detect_project_variables(project_dir)
    
    if binary_path and len(variables) > 0:
        # Create variable list for syncer
        var_list = create_variable_list_for_syncer(variables)
        print(f"\n🎯 Variable list for syncer: {var_list}")
        print(f"🎯 Binary path: {binary_path}")
        return True
    else:
        print("❌ Detection failed")
        return False

if __name__ == "__main__":
    test_universal_detection()
