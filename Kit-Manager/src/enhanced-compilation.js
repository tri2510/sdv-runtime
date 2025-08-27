// Copyright (c) 2025 Eclipse Foundation.
// 
// This program and the accompanying materials are made available under the
// terms of the MIT License which is available at
// https://opensource.org/licenses/MIT.
//
// SPDX-License-Identifier: MIT

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

/**
 * Enhanced C++ compilation features
 */

// Library building support
async function createLibraryTemplate(dest, libraryType) {
    await fs.promises.mkdir(dest, { recursive: true });
    await fs.promises.mkdir(path.join(dest, 'lib'), { recursive: true });
    await fs.promises.mkdir(path.join(dest, 'lib/src'), { recursive: true });
    await fs.promises.mkdir(path.join(dest, 'lib/include'), { recursive: true });
    await fs.promises.mkdir(path.join(dest, 'build'), { recursive: true });
    
    const rootCMake = `cmake_minimum_required(VERSION 3.16)
project(UserLibrary CXX)

set(CMAKE_CXX_STANDARD 17)
find_package(Threads REQUIRED)

add_subdirectory(lib)
`;
    
    await fs.promises.writeFile(path.join(dest, 'CMakeLists.txt'), rootCMake);
}

function generateLibraryCMake(libraryType, config = {}) {
    const { cpp_standard = '17', compiler_flags = '', target_name = 'user_lib' } = config;
    
    const baseConfig = `cmake_minimum_required(VERSION 3.16)
set(CMAKE_CXX_STANDARD ${cpp_standard})
set(CMAKE_CXX_FLAGS "\${CMAKE_CXX_FLAGS} ${compiler_flags}")

file(GLOB_RECURSE SOURCES "src/*.cpp")
file(GLOB_RECURSE HEADERS "include/*.h" "include/*.hpp")
`;
    
    switch (libraryType) {
        case 'static':
            return baseConfig + `
add_library(${target_name} STATIC \${SOURCES})
target_include_directories(${target_name} PUBLIC include)
target_link_libraries(${target_name} Threads::Threads)
`;
        case 'shared':
            return baseConfig + `
add_library(${target_name} SHARED \${SOURCES})
target_include_directories(${target_name} PUBLIC include)
target_link_libraries(${target_name} Threads::Threads)
`;
        case 'header_only':
            return `cmake_minimum_required(VERSION 3.16)
add_library(${target_name} INTERFACE)
target_include_directories(${target_name} INTERFACE include)
`;
        default:
            throw new Error(`Unsupported library type: ${libraryType}`);
    }
}

// Enhanced executable CMake generation
function generateEnhancedExecutableCMake(config = {}) {
    const {
        cpp_standard = '17',
        build_type = 'Debug',
        compiler = 'gcc',
        compiler_flags = '',
        target_name = 'app',
        system_packages = [],
        conan_packages = []
    } = config;

    let cmakeContent = `cmake_minimum_required(VERSION 3.16)
set(CMAKE_CXX_STANDARD ${cpp_standard})
set(CMAKE_BUILD_TYPE ${build_type})
set(CMAKE_CXX_FLAGS "\${CMAKE_CXX_FLAGS} ${compiler_flags}")

# Find system packages
find_package(Threads REQUIRED)
`;

    // Add system package finding
    const packageMap = {
        'libboost-dev': 'find_package(Boost REQUIRED COMPONENTS system filesystem)\nset(SYSTEM_LIBS \${SYSTEM_LIBS} Boost::system Boost::filesystem)',
        'libssl-dev': 'find_package(OpenSSL REQUIRED)\nset(SYSTEM_LIBS \${SYSTEM_LIBS} OpenSSL::SSL OpenSSL::Crypto)',
        'libcurl4-dev': 'find_package(CURL REQUIRED)\nset(SYSTEM_LIBS \${SYSTEM_LIBS} CURL::libcurl)',
        'libopencv-dev': 'find_package(OpenCV REQUIRED)\nset(SYSTEM_LIBS \${SYSTEM_LIBS} \${OpenCV_LIBS})',
        'libeigen3-dev': 'find_package(Eigen3 REQUIRED)\nset(SYSTEM_LIBS \${SYSTEM_LIBS} Eigen3::Eigen)'
    };

    system_packages.forEach(pkg => {
        if (packageMap[pkg]) {
            cmakeContent += packageMap[pkg] + '\n';
        }
    });

    // Add Conan integration if packages specified
    if (conan_packages.length > 0) {
        cmakeContent += `
# Conan integration
include(\${CMAKE_BINARY_DIR}/conan_toolchain.cmake)
include(\${CMAKE_BINARY_DIR}/conandeps.cmake)
`;
    }

    cmakeContent += `
# Source files
file(GLOB_RECURSE CPP_SOURCES "*.cpp")

add_executable(\${TARGET_NAME}
    \${CPP_SOURCES}
)

target_include_directories(\${TARGET_NAME} PRIVATE
    \${CMAKE_CURRENT_SOURCE_DIR}
    \${CMAKE_CURRENT_SOURCE_DIR}/include
    \${CMAKE_CURRENT_SOURCE_DIR}/../include
)

# Auto-detect header directories
file(GLOB_RECURSE HEADER_FILES "*.h" "*.hpp")
foreach(HEADER_FILE \${HEADER_FILES})
    get_filename_component(HEADER_DIR \${HEADER_FILE} DIRECTORY)
    target_include_directories(\${TARGET_NAME} PRIVATE \${HEADER_DIR})
endforeach()

target_link_libraries(\${TARGET_NAME}
    Threads::Threads
    \${SYSTEM_LIBS}
`;

    // Add Conan libraries
    if (conan_packages.length > 0) {
        conan_packages.forEach(pkg => {
            const libName = pkg.split('/')[0];
            cmakeContent += `    \${${libName}_LIBRARIES}\n`;
        });
    }

    cmakeContent += ')';

    return cmakeContent;
}

// Session package installation
async function installSessionPackages(packages, socket) {
    return new Promise((resolve, reject) => {
        const apt = spawn('apt-get', ['update', '&&', 'apt-get', 'install', '-y', ...packages], {
            shell: true
        });

        apt.stdout.on('data', (data) => {
            if (socket) {
                socket.emit('package_install_reply', {
                    status: 'installing',
                    result: data.toString(),
                    isDone: false
                });
            }
        });

        apt.stderr.on('data', (data) => {
            if (socket) {
                socket.emit('package_install_reply', {
                    status: 'installing',
                    result: data.toString(),
                    isDone: false
                });
            }
        });

        apt.on('close', (code) => {
            const success = code === 0;
            if (socket) {
                socket.emit('package_install_reply', {
                    status: success ? 'installed' : 'failed',
                    result: `Package installation ${success ? 'completed' : 'failed'} with code ${code}\r\n`,
                    isDone: true,
                    code: code
                });
            }
            
            if (success) {
                resolve(code);
            } else {
                reject(new Error(`Package installation failed with code ${code}`));
            }
        });

        apt.on('error', (err) => {
            if (socket) {
                socket.emit('package_install_reply', {
                    status: 'failed',
                    result: `Error: ${err.message}\r\n`,
                    isDone: true
                });
            }
            reject(err);
        });
    });
}

// Conan package management
async function installConanPackages(packages, workDir, socket) {
    const conanfile = `from conan import ConanFile
from conan.tools.cmake import cmake_deps, CMakeToolchain

class ProjectConan(ConanFile):
    requires = ${JSON.stringify(packages)}
    generators = "CMakeDeps", "CMakeToolchain"
    settings = "os", "compiler", "build_type", "arch"
    
    def configure(self):
        self.settings.compiler.cppstd = "17"
`;

    await fs.promises.writeFile(path.join(workDir, 'conanfile.py'), conanfile);

    return new Promise((resolve, reject) => {
        const conan = spawn('conan', ['install', '.', '--build=missing'], { 
            cwd: workDir 
        });

        conan.stdout.on('data', (data) => {
            if (socket) {
                socket.emit('conan_install_reply', {
                    status: 'installing',
                    result: data.toString(),
                    isDone: false
                });
            }
        });

        conan.stderr.on('data', (data) => {
            if (socket) {
                socket.emit('conan_install_reply', {
                    status: 'installing',
                    result: data.toString(),
                    isDone: false
                });
            }
        });

        conan.on('close', (code) => {
            const success = code === 0;
            if (socket) {
                socket.emit('conan_install_reply', {
                    status: success ? 'completed' : 'failed',
                    result: `Conan install ${success ? 'completed' : 'failed'} with code ${code}\r\n`,
                    isDone: true,
                    code: code
                });
            }
            
            if (success) {
                resolve(code);
            } else {
                reject(new Error(`Conan installation failed with code ${code}`));
            }
        });

        conan.on('error', (err) => {
            if (socket) {
                socket.emit('conan_install_reply', {
                    status: 'failed',
                    result: `Error: ${err.message}\r\n`,
                    isDone: true
                });
            }
            reject(err);
        });
    });
}

// Write tree structure with enhanced support
async function writeTreeStructureEnhanced(items, baseDir, socket) {
    for (const item of items) {
        if (item.type === 'file') {
            const filePath = path.join(baseDir, item.name);
            const fileDir = path.dirname(filePath);
            await fs.promises.mkdir(fileDir, { recursive: true });
            await fs.promises.writeFile(filePath, item.content, 'utf8');
            
            if (socket) {
                await socket.emit("compile_cpp_reply", {
                    "status": "file-written",
                    "result": `Written file: ${item.name}\r\n`,
                    "cmd": "compile_cpp",
                    "data": "",
                    "isDone": false,
                    "code": 0
                });
            }
        } else if (item.type === 'folder' && item.items) {
            const folderPath = path.join(baseDir, item.name);
            await fs.promises.mkdir(folderPath, { recursive: true });
            await writeTreeStructureEnhanced(item.items, folderPath, socket);
        }
    }
}

module.exports = {
    createLibraryTemplate,
    generateLibraryCMake,
    generateEnhancedExecutableCMake,
    installSessionPackages,
    installConanPackages,
    writeTreeStructureEnhanced
};