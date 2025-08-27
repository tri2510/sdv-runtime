// Copyright (c) 2025 Eclipse Foundation.
// 
// This program and the accompanying materials are made available under the
// terms of the MIT License which is available at
// https://opensource.org/licenses/MIT.
//
// SPDX-License-Identifier: MIT

const { io } = require('socket.io-client');
const { expect } = require('chai');
const config = require('../utils/test-config');

describe('Enhanced Library Compilation', function() {
    this.timeout(30000);
    
    let socket;
    let messages = [];

    before(function(done) {
        socket = io(config.SOCKET_URL);
        socket.on('connect', () => {
            console.log('Connected to Kit Manager for library compilation test');
            done();
        });
    });

    after(function() {
        if (socket) socket.disconnect();
    });

    beforeEach(function() {
        messages = [];
    });

    describe('Static Library Compilation', function() {
        it('should compile a static library successfully', function(done) {
            const testData = {
                app_name: 'test_static_lib',
                library_type: 'static',
                files: [
                    {
                        type: 'file',
                        name: 'include/math_utils.h',
                        content: `#pragma once

namespace math_utils {
    int add(int a, int b);
    int multiply(int a, int b);
}
`
                    },
                    {
                        type: 'file',
                        name: 'src/math_utils.cpp',
                        content: `#include "math_utils.h"

namespace math_utils {
    int add(int a, int b) {
        return a + b;
    }
    
    int multiply(int a, int b) {
        return a * b;
    }
}
`
                    }
                ],
                config: {
                    cpp_standard: '17',
                    compiler_flags: '-O2 -Wall'
                }
            };

            socket.on('compile_cpp_library_reply', (data) => {
                messages.push(data);
                console.log(`Library compilation: ${data.status} - ${data.result}`);
                
                if (data.isDone) {
                    expect(data.code).to.equal(0);
                    expect(data.status).to.equal('build-done');
                    expect(data.result).to.include('static library build completed');
                    
                    // Check that we got all expected stages
                    const statuses = messages.map(m => m.status);
                    expect(statuses).to.include('compile-start');
                    expect(statuses).to.include('file-written');
                    expect(statuses).to.include('configure-stdout');
                    expect(statuses).to.include('build-done');
                    
                    done();
                }
            });

            socket.emit('compile_cpp_library', testData);
        });
    });

    describe('Shared Library Compilation', function() {
        it('should compile a shared library successfully', function(done) {
            const testData = {
                app_name: 'test_shared_lib',
                library_type: 'shared',
                files: [
                    {
                        type: 'file',
                        name: 'include/string_utils.h',
                        content: `#pragma once
#include <string>

namespace string_utils {
    std::string to_upper(const std::string& str);
    std::string reverse(const std::string& str);
}
`
                    },
                    {
                        type: 'file',
                        name: 'src/string_utils.cpp',
                        content: `#include "string_utils.h"
#include <algorithm>

namespace string_utils {
    std::string to_upper(const std::string& str) {
        std::string result = str;
        std::transform(result.begin(), result.end(), result.begin(), ::toupper);
        return result;
    }
    
    std::string reverse(const std::string& str) {
        std::string result = str;
        std::reverse(result.begin(), result.end());
        return result;
    }
}
`
                    }
                ]
            };

            socket.on('compile_cpp_library_reply', (data) => {
                messages.push(data);
                console.log(`Shared library compilation: ${data.status} - ${data.result}`);
                
                if (data.isDone) {
                    expect(data.code).to.equal(0);
                    expect(data.status).to.equal('build-done');
                    expect(data.result).to.include('shared library build completed');
                    done();
                }
            });

            socket.emit('compile_cpp_library', testData);
        });
    });

    describe('Header-Only Library', function() {
        it('should handle header-only library compilation', function(done) {
            const testData = {
                app_name: 'test_header_only_lib',
                library_type: 'header_only',
                files: [
                    {
                        type: 'file',
                        name: 'include/template_utils.h',
                        content: `#pragma once
#include <vector>
#include <algorithm>

template<typename T>
class TemplateUtils {
public:
    static T max_element(const std::vector<T>& vec) {
        return *std::max_element(vec.begin(), vec.end());
    }
    
    static std::vector<T> sort_ascending(std::vector<T> vec) {
        std::sort(vec.begin(), vec.end());
        return vec;
    }
};
`
                    }
                ]
            };

            socket.on('compile_cpp_library_reply', (data) => {
                messages.push(data);
                console.log(`Header-only library compilation: ${data.status} - ${data.result}`);
                
                if (data.isDone) {
                    expect(data.code).to.equal(0);
                    expect(data.status).to.equal('build-done');
                    expect(data.result).to.include('header_only library build completed');
                    done();
                }
            });

            socket.emit('compile_cpp_library', testData);
        });
    });

    describe('Error Handling', function() {
        it('should handle invalid library type', function(done) {
            const testData = {
                app_name: 'test_invalid_lib',
                library_type: 'invalid_type',
                files: []
            };

            socket.on('compile_cpp_library_reply', (data) => {
                if (data.isDone) {
                    expect(data.code).to.equal(1);
                    expect(data.status).to.include('err');
                    done();
                }
            });

            socket.emit('compile_cpp_library', testData);
        });

        it('should handle missing required fields', function(done) {
            const testData = {
                app_name: 'test_missing_fields'
                // Missing library_type and files
            };

            socket.on('compile_cpp_library_reply', (data) => {
                if (data.isDone) {
                    expect(data.code).to.equal(1);
                    expect(data.status).to.equal('err: invalid');
                    expect(data.result).to.include('Required: app_name, library_type');
                    done();
                }
            });

            socket.emit('compile_cpp_library', testData);
        });
    });
});