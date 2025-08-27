# Enhanced C++ Compilation API Specification

## Overview

The SDV Runtime provides enhanced C++ compilation capabilities through WebSocket-based communication. This API extends the original compilation functionality with support for library building, package management, and advanced configuration options.

## Connection Details

- **Protocol**: WebSocket via Socket.IO
- **URL**: `http://localhost:3090`
- **Namespace**: Default (`/`)

## Endpoints Overview

| Endpoint | Description | Status |
|----------|-------------|---------|
| `compile_cpp` | Original compilation endpoint | ✅ Maintained for backward compatibility |
| `compile_cpp_library` | Build C++ libraries (static, shared, header-only) | 🆕 New |
| `install_session_packages` | Install apt packages temporarily | 🆕 New |
| `install_conan_packages` | Install Conan packages | 🆕 New |
| `compile_cpp_advanced` | Advanced compilation with dependencies | 🆕 New |

---

## 1. Library Compilation Endpoint

### `compile_cpp_library`

Build C++ libraries instead of executables.

#### Request Format

```javascript
socket.emit('compile_cpp_library', {
    app_name: 'my_library',           // Required: Library name
    library_type: 'static',          // Required: 'static', 'shared', 'header-only'
    config: {                        // Optional: Build configuration
        cpp_standard: '17',          // C++ standard: '11', '14', '17', '20', '23'
        compiler_flags: '-O2 -Wall', // Additional compiler flags
        build_type: 'Release'        // 'Debug', 'Release', 'RelWithDebInfo'
    },
    files: [                         // Required: Source files (tree structure)
        {
            type: 'file',
            name: 'library.cpp',
            content: '#include "library.h"\n...'
        },
        {
            type: 'file',
            name: 'library.h',
            content: '#pragma once\n...'
        }
    ]
});
```

#### Response Events

Listen for `compile_cpp_library_reply` events:

```javascript
socket.on('compile_cpp_library_reply', (data) => {
    console.log(`Status: ${data.status}`);
    console.log(`Result: ${data.result}`);
    
    if (data.isDone) {
        console.log(`Final code: ${data.code}`);
        // Library built successfully if code === 0
    }
});
```

#### Response Status Values

| Status | Description |
|--------|-------------|
| `compile-start` | Compilation process initiated |
| `file-written` | Source file written to container |
| `configure-stdout/stderr` | CMake configuration output |
| `build-stdout/stderr` | Build process output |
| `build-done` | Library compilation completed |
| `err_*` | Various error conditions |

#### Library Types

1. **Static Library** (`static`)
   - Produces `.a` file
   - Linked at compile time
   - Best for distribution

2. **Shared Library** (`shared`)
   - Produces `.so` file
   - Linked at runtime
   - Smaller executable size

3. **Header-only Library** (`header-only`)
   - Interface-only library
   - No compilation, just validation
   - Template libraries

#### Example: Building a Static Library

```javascript
const libraryRequest = {
    app_name: 'math_utils',
    library_type: 'static',
    config: {
        cpp_standard: '17',
        compiler_flags: '-O2 -Wall',
        build_type: 'Release'
    },
    files: [
        {
            type: 'file',
            name: 'math_utils.h',
            content: `#pragma once

class MathUtils {
public:
    static int add(int a, int b);
    static int multiply(int a, int b);
};`
        },
        {
            type: 'file',
            name: 'math_utils.cpp',
            content: `#include "math_utils.h"

int MathUtils::add(int a, int b) {
    return a + b;
}

int MathUtils::multiply(int a, int b) {
    return a * b;
}`
        }
    ]
};

socket.emit('compile_cpp_library', libraryRequest);
```

---

## 2. Session Package Installation

### `install_session_packages`

Install apt packages temporarily (session-only, non-persistent).

#### Request Format

```javascript
socket.emit('install_session_packages', {
    packages: ['libboost-dev', 'libssl-dev', 'libcurl4-openssl-dev']
});
```

#### Response Events

```javascript
socket.on('install_session_packages_reply', (data) => {
    console.log(`Status: ${data.status}`);
    
    if (data.isDone) {
        if (data.status === 'completed') {
            console.log('Packages installed successfully');
        } else {
            console.log('Package installation failed:', data.result);
        }
    }
});
```

#### Response Status Values

| Status | Description |
|--------|-------------|
| `updating` | Updating package lists |
| `installing` | Installing packages |
| `completed` | Installation completed successfully |
| `failed` | Installation failed |

#### Important Notes

- Packages are installed temporarily and will be lost when container restarts
- Use for development/testing purposes
- Consider using pre-configured Docker images for production
- Installation may take time depending on package size

---

## 3. Conan Package Management

### `install_conan_packages`

Install modern C++ packages using Conan package manager.

#### Request Format

```javascript
socket.emit('install_conan_packages', {
    packages: ['fmt/9.1.0', 'spdlog/1.11.0', 'nlohmann_json/3.11.2'],
    profile: 'default'  // Optional: Conan profile
});
```

#### Response Events

```javascript
socket.on('conan_install_reply', (data) => {
    console.log(`Conan status: ${data.status}`);
    
    if (data.isDone) {
        if (data.status === 'completed') {
            console.log('Conan packages installed');
        }
    }
});
```

#### Popular Conan Packages

| Package | Description | Version Example |
|---------|-------------|-----------------|
| `fmt/9.1.0` | Modern formatting library | `9.1.0` |
| `spdlog/1.11.0` | Fast logging library | `1.11.0` |
| `nlohmann_json/3.11.2` | JSON library | `3.11.2` |
| `boost/1.81.0` | Boost libraries | `1.81.0` |
| `gtest/1.13.0` | Google Test framework | `1.13.0` |

#### Requirements

- Conan must be installed in the Docker container
- Package versions should be specified
- May require additional configuration for some packages

---

## 4. Advanced Compilation

### `compile_cpp_advanced`

Compile C++ projects with advanced configuration and dependency management.

#### Request Format

```javascript
socket.emit('compile_cpp_advanced', {
    app_name: 'advanced_app',
    target_type: 'executable',       // 'executable', 'static', 'shared'
    dependencies: {
        system_packages: ['libboost-dev'],      // apt packages
        conan_packages: ['fmt/9.1.0']           // Conan packages
    },
    config: {
        cpp_standard: '20',
        build_type: 'Debug',
        compiler_flags: '-Wall -Wextra',
        cmake_options: ['-DWITH_TESTING=ON']
    },
    files: [
        // File tree structure
    ]
});
```

#### Configuration Options

| Option | Description | Valid Values |
|--------|-------------|--------------|
| `cpp_standard` | C++ standard version | `'11'`, `'14'`, `'17'`, `'20'`, `'23'` |
| `build_type` | CMake build type | `'Debug'`, `'Release'`, `'RelWithDebInfo'`, `'MinSizeRel'` |
| `compiler_flags` | Additional compiler flags | String of flags |
| `cmake_options` | Additional CMake options | Array of strings |

#### Example: Advanced Application

```javascript
const advancedRequest = {
    app_name: 'logging_app',
    target_type: 'executable',
    dependencies: {
        conan_packages: ['spdlog/1.11.0', 'fmt/9.1.0']
    },
    config: {
        cpp_standard: '20',
        build_type: 'Release',
        compiler_flags: '-O3 -march=native'
    },
    files: [
        {
            type: 'file',
            name: 'main.cpp',
            content: `#include <spdlog/spdlog.h>

int main() {
    spdlog::info("Hello from advanced compilation!");
    return 0;
}`
        }
    ]
};

socket.emit('compile_cpp_advanced', advancedRequest);
```

---

## 5. Backward Compatibility

### `compile_cpp` (Original Endpoint)

The original compilation endpoint remains fully functional and unchanged.

#### Request Format (Unchanged)

```javascript
socket.emit('compile_cpp', {
    app_name: 'hello_world',
    files: [
        {
            type: 'file',
            name: 'main.cpp',
            content: '#include <iostream>\n...'
        }
    ],
    run: true  // Optional: run after compilation
});
```

All existing frontend code using `compile_cpp` will continue to work without modifications.

---

## File Structure Format

All endpoints support the hierarchical tree structure format:

### Single File

```javascript
files: [
    {
        type: 'file',
        name: 'main.cpp',
        content: '...'
    }
]
```

### Multiple Files with Folders

```javascript
files: [
    {
        type: 'folder',
        name: 'src',
        items: [
            {
                type: 'file',
                name: 'main.cpp',
                content: '...'
            },
            {
                type: 'file',
                name: 'utils.h',
                content: '...'
            }
        ]
    },
    {
        type: 'folder',
        name: 'include',
        items: [
            {
                type: 'file',
                name: 'common.h',
                content: '...'
            }
        ]
    }
]
```

---

## Error Handling

### Common Error Patterns

```javascript
socket.on('[endpoint]_reply', (data) => {
    if (data.status.includes('err') || data.status.includes('failed')) {
        console.error('Compilation error:', data.result);
        
        // Handle specific error types
        if (data.status === 'err_cmake_configure') {
            // CMake configuration failed
        } else if (data.status === 'err_build') {
            // Build compilation failed
        }
    }
});
```

### Validation Errors

All endpoints validate input parameters and return descriptive error messages:

```javascript
// Example validation error response
{
    status: 'err_validation',
    result: 'packages array required and must not be empty',
    isDone: true,
    code: 1
}
```

---

## Implementation Examples

### Frontend Integration Example (React)

```javascript
import io from 'socket.io-client';

class CppCompilationService {
    constructor() {
        this.socket = io('http://localhost:3090');
        this.setupEventHandlers();
    }

    setupEventHandlers() {
        // Handle library compilation responses
        this.socket.on('compile_cpp_library_reply', (data) => {
            this.handleCompilationResponse('library', data);
        });

        // Handle package installation responses
        this.socket.on('install_session_packages_reply', (data) => {
            this.handlePackageResponse(data);
        });

        // Handle advanced compilation responses
        this.socket.on('compile_cpp_advanced_reply', (data) => {
            this.handleCompilationResponse('advanced', data);
        });
    }

    compileLibrary(libraryData) {
        return new Promise((resolve, reject) => {
            this.currentResolve = resolve;
            this.currentReject = reject;
            this.socket.emit('compile_cpp_library', libraryData);
        });
    }

    installPackages(packages) {
        return new Promise((resolve, reject) => {
            this.packageResolve = resolve;
            this.packageReject = reject;
            this.socket.emit('install_session_packages', { packages });
        });
    }

    handleCompilationResponse(type, data) {
        console.log(`${type} compilation:`, data.status);
        
        if (data.isDone) {
            if (data.code === 0) {
                this.currentResolve?.(data);
            } else {
                this.currentReject?.(data);
            }
        }
    }

    handlePackageResponse(data) {
        if (data.isDone) {
            if (data.status === 'completed') {
                this.packageResolve?.(data);
            } else {
                this.packageReject?.(data);
            }
        }
    }
}

// Usage example
const compiler = new CppCompilationService();

// Build a library
const libraryConfig = {
    app_name: 'my_math_lib',
    library_type: 'static',
    config: { cpp_standard: '17' },
    files: [/* file tree */]
};

compiler.compileLibrary(libraryConfig)
    .then(result => console.log('Library built successfully'))
    .catch(error => console.error('Library build failed'));
```

---

## Testing and Validation

### Running Tests

The implementation includes comprehensive tests:

```bash
# Run all enhanced feature tests
node test/run-enhanced-tests.js

# Run specific test suites
npx mocha test/10-enhanced-library-compilation/test.js
npx mocha test/11-session-package-installation/test.js
npx mocha test/13-conan-integration/test.js

# Validate features without container
node validate-enhanced-features.js
```

### Test Coverage

- ✅ Library compilation (static, shared, header-only)
- ✅ Session package installation
- ✅ Conan package management
- ✅ Advanced compilation configurations
- ✅ Backward compatibility
- ✅ Error handling and validation

---

## Deployment Notes

### Docker Configuration

The enhanced features work with the existing SDV Runtime Docker container. For optimal performance:

1. **Pre-configured Images**: Create Docker images with commonly used libraries pre-installed
2. **Session Packages**: Use for development and testing only
3. **Conan Integration**: Ensure Conan is installed in the container for package management

### Performance Considerations

- Library compilation is faster than executable compilation
- Package installation adds overhead to first compilation
- Conan packages are cached after first installation
- Use appropriate build types (`Release` for production, `Debug` for development)

### Security Notes

- Session packages are temporary and don't persist
- All compilation happens within the Docker container
- File system access is limited to the compilation workspace
- No network access during compilation unless explicitly configured

---

## Migration Guide

### Upgrading from Original API

Existing code using `compile_cpp` requires no changes. To leverage new features:

1. **For Library Building**: Replace `compile_cpp` with `compile_cpp_library`
2. **For Package Dependencies**: Use `install_session_packages` before compilation
3. **For Modern C++ Libraries**: Use `install_conan_packages` for dependencies
4. **For Advanced Configuration**: Use `compile_cpp_advanced` with configuration options

### Feature Adoption Strategy

1. **Phase 1**: Continue using existing `compile_cpp` for backward compatibility
2. **Phase 2**: Introduce library building for specific use cases
3. **Phase 3**: Add package management for development workflows
4. **Phase 4**: Migrate to `compile_cpp_advanced` for new projects

---

## Support and Troubleshooting

### Common Issues

1. **Connection Failed**: Ensure SDV Runtime container is running on port 3090
2. **Package Installation Timeout**: Some packages take time; increase timeout values
3. **Conan Not Found**: Verify Conan is installed in the Docker container
4. **Build Failures**: Check compiler flags and C++ standard compatibility

### Debug Information

Enable verbose logging by listening to all status messages and examining build output for detailed error information.

### Getting Help

Refer to the test files in `test/` directory for working examples of all endpoints and configurations.