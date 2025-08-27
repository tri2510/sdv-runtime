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

describe('Advanced C++ Compilation', function() {
    this.timeout(60000);
    
    let socket;
    let messages = [];

    before(function(done) {
        socket = io(config.SOCKET_URL);
        socket.on('connect', () => {
            console.log('Connected to Kit Manager for advanced compilation test');
            done();
        });
    });

    after(function() {
        if (socket) socket.disconnect();
    });

    beforeEach(function() {
        messages = [];
    });

    describe('Enhanced Executable Compilation', function() {
        it('should compile with custom C++ standard and compiler flags', function(done) {
            const testData = {
                app_name: 'test_advanced_executable',
                target_type: 'executable',
                config: {
                    cpp_standard: '20',
                    build_type: 'Release',
                    compiler_flags: '-O3 -Wall -Wextra'
                },
                files: [
                    {
                        type: 'file',
                        name: 'main.cpp',
                        content: `#include <iostream>
#include <vector>
#include <ranges>

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    
    // C++20 ranges
    auto even_numbers = numbers 
        | std::views::filter([](int n) { return n % 2 == 0; });
    
    std::cout << "Even numbers: ";
    for (int n : even_numbers) {
        std::cout << n << " ";
    }
    std::cout << std::endl;
    
    return 0;
}
`
                    }
                ]
            };

            socket.on('compile_cpp_advanced_reply', (data) => {
                messages.push(data);
                console.log(`Advanced compilation: ${data.status} - ${data.result?.substring(0, 100)}`);
                
                if (data.isDone) {
                    expect(data.code).to.equal(0);
                    expect(data.status).to.equal('build-done');
                    expect(data.result).to.include('Advanced compilation completed');
                    
                    // Verify compilation stages
                    const statuses = messages.map(m => m.status);
                    expect(statuses).to.include('compile-start');
                    expect(statuses).to.include('configure-stdout');
                    expect(statuses).to.include('build-done');
                    
                    done();
                }
            });

            socket.emit('compile_cpp_advanced', testData);
        });
    });

    describe('Multi-file Project Compilation', function() {
        it('should compile complex multi-file project', function(done) {
            const testData = {
                app_name: 'test_multifile_advanced',
                target_type: 'executable',
                config: {
                    cpp_standard: '17',
                    build_type: 'Debug',
                    compiler_flags: '-g -Wall'
                },
                files: [
                    {
                        type: 'file',
                        name: 'include/calculator.h',
                        content: `#pragma once

class Calculator {
public:
    Calculator();
    ~Calculator();
    
    double add(double a, double b);
    double subtract(double a, double b);
    double multiply(double a, double b);
    double divide(double a, double b);
    
private:
    int operation_count;
};
`
                    },
                    {
                        type: 'file',
                        name: 'src/calculator.cpp',
                        content: `#include "calculator.h"
#include <stdexcept>

Calculator::Calculator() : operation_count(0) {}

Calculator::~Calculator() {}

double Calculator::add(double a, double b) {
    operation_count++;
    return a + b;
}

double Calculator::subtract(double a, double b) {
    operation_count++;
    return a - b;
}

double Calculator::multiply(double a, double b) {
    operation_count++;
    return a * b;
}

double Calculator::divide(double a, double b) {
    if (b == 0.0) {
        throw std::runtime_error("Division by zero");
    }
    operation_count++;
    return a / b;
}
`
                    },
                    {
                        type: 'file',
                        name: 'main.cpp',
                        content: `#include <iostream>
#include <stdexcept>
#include "calculator.h"

int main() {
    try {
        Calculator calc;
        
        std::cout << "Calculator Test" << std::endl;
        std::cout << "2 + 3 = " << calc.add(2, 3) << std::endl;
        std::cout << "5 - 2 = " << calc.subtract(5, 2) << std::endl;
        std::cout << "4 * 6 = " << calc.multiply(4, 6) << std::endl;
        std::cout << "10 / 2 = " << calc.divide(10, 2) << std::endl;
        
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}
`
                    }
                ]
            };

            socket.on('compile_cpp_advanced_reply', (data) => {
                messages.push(data);
                console.log(`Multi-file advanced: ${data.status}`);
                
                if (data.isDone) {
                    expect(data.code).to.equal(0);
                    expect(data.status).to.equal('build-done');
                    done();
                }
            });

            socket.emit('compile_cpp_advanced', testData);
        });
    });

    describe('Library Target Compilation', function() {
        it('should compile library target through advanced endpoint', function(done) {
            const testData = {
                app_name: 'test_lib_via_advanced',
                target_type: 'static',
                config: {
                    cpp_standard: '17',
                    target_name: 'mylib'
                },
                files: [
                    {
                        type: 'file',
                        name: 'include/mylib.h',
                        content: `#pragma once

namespace mylib {
    int factorial(int n);
    bool is_prime(int n);
}
`
                    },
                    {
                        type: 'file',
                        name: 'src/mylib.cpp',
                        content: `#include "mylib.h"

namespace mylib {
    int factorial(int n) {
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }
    
    bool is_prime(int n) {
        if (n <= 1) return false;
        if (n <= 3) return true;
        if (n % 2 == 0 || n % 3 == 0) return false;
        
        for (int i = 5; i * i <= n; i += 6) {
            if (n % i == 0 || n % (i + 2) == 0) {
                return false;
            }
        }
        return true;
    }
}
`
                    }
                ]
            };

            socket.on('compile_cpp_advanced_reply', (data) => {
                messages.push(data);
                console.log(`Library via advanced: ${data.status}`);
                
                if (data.isDone) {
                    expect(data.code).to.equal(0);
                    expect(data.status).to.equal('build-done');
                    done();
                }
            });

            socket.emit('compile_cpp_advanced', testData);
        });
    });

    describe('Error Handling', function() {
        it('should handle compilation errors gracefully', function(done) {
            const testData = {
                app_name: 'test_compilation_error',
                target_type: 'executable',
                files: [
                    {
                        type: 'file',
                        name: 'main.cpp',
                        content: `#include <iostream>

int main() {
    // Intentional syntax error
    undefined_function();
    missing_semicolon
    return 0;
}
`
                    }
                ]
            };

            socket.on('compile_cpp_advanced_reply', (data) => {
                messages.push(data);
                console.log(`Error handling test: ${data.status}`);
                
                if (data.isDone) {
                    expect(data.code).to.not.equal(0);
                    expect(data.status).to.be.oneOf(['configure-failed', 'build-done']);
                    
                    // Should have error messages
                    const errorMessages = messages.filter(m => 
                        m.status.includes('stderr') || m.result.includes('error'));
                    expect(errorMessages.length).to.be.greaterThan(0);
                    
                    done();
                }
            });

            socket.emit('compile_cpp_advanced', testData);
        });

        it('should handle invalid configuration', function(done) {
            const testData = {
                app_name: 'test_invalid_config',
                target_type: 'invalid_target_type',
                files: []
            };

            socket.on('compile_cpp_advanced_reply', (data) => {
                if (data.isDone) {
                    expect(data.code).to.equal(1);
                    expect(data.status).to.include('err');
                    done();
                }
            });

            socket.emit('compile_cpp_advanced', testData);
        });

        it('should handle missing required fields', function(done) {
            const testData = {
                // Missing app_name and files
                target_type: 'executable'
            };

            socket.on('compile_cpp_advanced_reply', (data) => {
                if (data.isDone) {
                    expect(data.code).to.equal(1);
                    expect(data.status).to.equal('err: invalid');
                    expect(data.result).to.include('app_name and files array required');
                    done();
                }
            });

            socket.emit('compile_cpp_advanced', testData);
        });
    });
});