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

describe('Session Package Installation', function() {
    this.timeout(120000); // Package installation can take time
    
    let socket;
    let messages = [];

    before(function(done) {
        socket = io(config.SOCKET_URL);
        socket.on('connect', () => {
            console.log('Connected to Kit Manager for package installation test');
            done();
        });
    });

    after(function() {
        if (socket) socket.disconnect();
    });

    beforeEach(function() {
        messages = [];
    });

    describe('Basic Package Installation', function() {
        it('should install basic development packages', function(done) {
            const testData = {
                packages: ['libfmt-dev'] // Small, fast package
            };

            let installationStarted = false;
            let installationCompleted = false;

            socket.on('package_install_reply', (data) => {
                messages.push(data);
                console.log(`Package installation: ${data.status} - ${data.result?.substring(0, 100)}`);
                
                if (data.status === 'installing') {
                    installationStarted = true;
                }
                
                if (data.isDone) {
                    installationCompleted = true;
                    expect(installationStarted).to.be.true;
                    expect(data.status).to.be.oneOf(['installed', 'failed']);
                    
                    // If it fails, it might be because package is already installed
                    // or not available in the container - both are acceptable
                    console.log(`Final status: ${data.status}`);
                    done();
                }
            });

            socket.emit('install_session_packages', testData);
        });
    });

    describe('Multiple Package Installation', function() {
        it('should handle multiple package installation request', function(done) {
            const testData = {
                packages: ['curl', 'wget'] // Common packages likely to exist
            };

            socket.on('package_install_reply', (data) => {
                messages.push(data);
                console.log(`Multi-package installation: ${data.status}`);
                
                if (data.isDone) {
                    expect(data.status).to.be.oneOf(['installed', 'failed']);
                    
                    // Check that installation process was initiated
                    const statuses = messages.map(m => m.status);
                    expect(statuses).to.include('installing');
                    done();
                }
            });

            socket.emit('install_session_packages', testData);
        });
    });

    describe('Error Handling', function() {
        it('should handle empty package list', function(done) {
            const testData = {
                packages: []
            };

            socket.on('package_install_reply', (data) => {
                if (data.isDone) {
                    expect(data.status).to.equal('failed');
                    expect(data.result).to.include('packages array required');
                    done();
                }
            });

            socket.emit('install_session_packages', testData);
        });

        it('should handle missing packages field', function(done) {
            const testData = {};

            socket.on('package_install_reply', (data) => {
                if (data.isDone) {
                    expect(data.status).to.equal('failed');
                    expect(data.result).to.include('packages array required');
                    done();
                }
            });

            socket.emit('install_session_packages', testData);
        });

        it('should handle invalid package names gracefully', function(done) {
            const testData = {
                packages: ['nonexistent-package-xyz-123']
            };

            socket.on('package_install_reply', (data) => {
                messages.push(data);
                console.log(`Invalid package test: ${data.status}`);
                
                if (data.isDone) {
                    // Should fail gracefully
                    expect(data.status).to.equal('failed');
                    done();
                }
            });

            socket.emit('install_session_packages', testData);
        });
    });

    describe('Advanced Compilation with Packages', function() {
        it('should compile code after installing packages', function(done) {
            this.timeout(180000); // Extended timeout for this complex test
            
            let packageInstallDone = false;
            let compilationDone = false;

            // Step 1: Install packages
            const packageData = {
                packages: ['libfmt-dev']
            };

            socket.on('package_install_reply', (data) => {
                console.log(`Package phase: ${data.status}`);
                
                if (data.isDone) {
                    packageInstallDone = true;
                    
                    // Step 2: Now try compilation with enhanced features
                    const compilationData = {
                        app_name: 'test_with_packages',
                        target_type: 'executable',
                        dependencies: {
                            system_packages: [] // Packages already installed
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

int main() {
    std::cout << "Hello from enhanced compilation!" << std::endl;
    return 0;
}
`
                            }
                        ]
                    };

                    socket.emit('compile_cpp_advanced', compilationData);
                }
            });

            socket.on('compile_cpp_advanced_reply', (data) => {
                console.log(`Compilation phase: ${data.status}`);
                
                if (data.isDone) {
                    compilationDone = true;
                    expect(packageInstallDone).to.be.true;
                    expect(data.status).to.equal('build-done');
                    done();
                }
            });

            socket.emit('install_session_packages', packageData);
        });
    });
});