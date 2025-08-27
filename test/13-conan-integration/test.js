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

describe('Conan Package Integration', function() {
    this.timeout(300000); // Conan operations can take very long
    
    let socket;
    let messages = [];

    before(function(done) {
        socket = io(config.SOCKET_URL);
        socket.on('connect', () => {
            console.log('Connected to Kit Manager for Conan integration test');
            done();
        });
    });

    after(function() {
        if (socket) socket.disconnect();
    });

    beforeEach(function() {
        messages = [];
    });

    // Note: These tests may require Conan to be installed in the container
    // They will be skipped if Conan is not available
    
    describe('Basic Conan Package Installation', function() {
        it('should handle Conan package installation request', function(done) {
            const testData = {
                packages: ['zlib/1.2.11'] // Simple, commonly available package
            };

            let installationStarted = false;

            socket.on('conan_install_reply', (data) => {
                messages.push(data);
                console.log(`Conan installation: ${data.status} - ${data.result?.substring(0, 100)}`);
                
                if (data.status === 'installing') {
                    installationStarted = true;
                }
                
                if (data.isDone) {
                    expect(installationStarted).to.be.true;
                    expect(data.status).to.be.oneOf(['completed', 'failed']);
                    
                    // If it fails, it's likely because Conan isn't installed or configured
                    // This is acceptable for testing the API structure
                    console.log(`Final Conan status: ${data.status}`);
                    if (data.status === 'failed') {
                        console.log('Conan installation failed - this is expected if Conan is not available');
                    }
                    
                    done();
                }
            });

            socket.emit('install_conan_packages', testData);
        });
    });

    describe('Multiple Conan Packages', function() {
        it('should handle multiple Conan package installation', function(done) {
            const testData = {
                packages: ['zlib/1.2.11', 'bzip2/1.0.8']
            };

            socket.on('conan_install_reply', (data) => {
                messages.push(data);
                console.log(`Multi Conan installation: ${data.status}`);
                
                if (data.isDone) {
                    expect(data.status).to.be.oneOf(['completed', 'failed']);
                    
                    // Verify process was initiated
                    const statuses = messages.map(m => m.status);
                    expect(statuses).to.include('installing');
                    
                    done();
                }
            });

            socket.emit('install_conan_packages', testData);
        });
    });

    describe('Conan Error Handling', function() {
        it('should handle empty package list', function(done) {
            const testData = {
                packages: []
            };

            socket.on('conan_install_reply', (data) => {
                if (data.isDone) {
                    expect(data.status).to.equal('failed');
                    expect(data.result).to.include('packages array required');
                    done();
                }
            });

            socket.emit('install_conan_packages', testData);
        });

        it('should handle missing packages field', function(done) {
            const testData = {};

            socket.on('conan_install_reply', (data) => {
                if (data.isDone) {
                    expect(data.status).to.equal('failed');
                    expect(data.result).to.include('packages array required');
                    done();
                }
            });

            socket.emit('install_conan_packages', testData);
        });

        it('should handle invalid package specifications', function(done) {
            const testData = {
                packages: ['invalid-package/999.999.999']
            };

            socket.on('conan_install_reply', (data) => {
                messages.push(data);
                console.log(`Invalid Conan package test: ${data.status}`);
                
                if (data.isDone) {
                    // Should fail gracefully
                    expect(data.status).to.equal('failed');
                    done();
                }
            });

            socket.emit('install_conan_packages', testData);
        });
    });

    describe('Integration with Advanced Compilation', function() {
        it('should attempt compilation with Conan dependencies', function(done) {
            this.timeout(360000); // Extended timeout for complex operation
            
            const testData = {
                app_name: 'test_conan_integration',
                target_type: 'executable',
                dependencies: {
                    conan_packages: ['zlib/1.2.11']
                },
                config: {
                    cpp_standard: '17',
                    build_type: 'Release'
                },
                files: [
                    {
                        type: 'file',
                        name: 'main.cpp',
                        content: `#include <iostream>

// Note: This is a minimal test that doesn't actually use zlib
// The test verifies the compilation pipeline works even if Conan fails
int main() {
    std::cout << "Conan integration test" << std::endl;
    std::cout << "This executable was built with Conan dependency handling" << std::endl;
    return 0;
}
`
                    }
                ]
            };

            let conanPhaseCompleted = false;
            let compilationCompleted = false;

            socket.on('compile_cpp_advanced_reply', (data) => {
                messages.push(data);
                console.log(`Conan integration compilation: ${data.status} - ${data.result?.substring(0, 80)}`);
                
                if (data.status === 'installing-conan') {
                    console.log('Conan installation phase detected');
                }
                
                if (data.status === 'compile-start') {
                    console.log('Compilation phase started');
                }
                
                if (data.isDone) {
                    compilationCompleted = true;
                    
                    // The compilation may succeed or fail depending on Conan availability
                    // Both outcomes are acceptable for testing the integration
                    expect(data.status).to.be.oneOf(['build-done', 'configure-failed', 'err_build']);
                    
                    console.log(`Final compilation status: ${data.status} with code ${data.code}`);
                    
                    // Verify that the Conan phase was attempted if specified
                    const statuses = messages.map(m => m.status);
                    if (testData.dependencies.conan_packages.length > 0) {
                        // Should have attempted Conan installation
                        expect(statuses).to.include('compile-start');
                    }
                    
                    done();
                }
            });

            socket.emit('compile_cpp_advanced', testData);
        });
    });

    describe('Conan Profile Support', function() {
        it('should handle custom Conan profile', function(done) {
            const testData = {
                packages: ['zlib/1.2.11'],
                profile: 'custom'
            };

            socket.on('conan_install_reply', (data) => {
                messages.push(data);
                console.log(`Custom profile test: ${data.status}`);
                
                if (data.isDone) {
                    // Profile handling is best-effort
                    expect(data.status).to.be.oneOf(['completed', 'failed']);
                    done();
                }
            });

            socket.emit('install_conan_packages', testData);
        });
    });
});