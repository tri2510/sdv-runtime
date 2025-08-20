// Copyright (c) 2025 Eclipse Foundation.
// 
// This program and the accompanying materials are made available under the
// terms of the MIT License which is available at
// https://opensource.org/licenses/MIT.
//
// SPDX-License-Identifier: MIT

/**
 * Mock Kit Server for testing syncer.py C++ compilation
 * This acts as the kit server that syncer.py connects to
 */

const { Server } = require('socket.io');
const http = require('http');

class MockKitServer {
    constructor(port = 3091) {
        this.port = port;
        this.server = http.createServer();
        this.io = new Server(this.server, {
            cors: {
                origin: "*",
                methods: ["GET", "POST"]
            }
        });
        this.syncerSocket = null;
        this.setupEventHandlers();
    }

    setupEventHandlers() {
        this.io.on('connection', (socket) => {
            console.log(`🔌 Client connected: ${socket.id}`);
            
            // Listen for syncer registration
            socket.on('register_kit', (data) => {
                console.log(`📝 Kit registered: ${data.kit_id}`);
                this.syncerSocket = socket;
                socket.kit_id = data.kit_id;
            });

            // Listen for syncer responses
            socket.on('messageToKit-kitReply', (response) => {
                console.log(`📥 [${response.status || response.cmd}] ${response.result?.substring(0, 100) || 'No result'}...`);
                
                // Emit to any test clients listening
                this.io.emit('compilation_progress', response);
            });

            socket.on('disconnect', () => {
                console.log(`📴 Client disconnected: ${socket.id}`);
                if (this.syncerSocket === socket) {
                    this.syncerSocket = null;
                }
            });
        });
    }

    async start() {
        return new Promise((resolve) => {
            this.server.listen(this.port, () => {
                console.log(`🎯 Mock Kit Server running on port ${this.port}`);
                console.log(`📡 Syncer.py should connect here instead of external server`);
                resolve();
            });
        });
    }

    // Send a C++ compilation request to the connected syncer
    sendCppCompileRequest(files, appName = 'TestApp', run = true) {
        if (!this.syncerSocket) {
            throw new Error('No syncer connected');
        }

        const request = {
            cmd: 'compile_cpp_app',
            request_from: 'mock-kit-server',
            data: {
                files: files,
                app_name: appName,
                run: run
            }
        };

        console.log(`📤 Sending C++ compilation request for: ${appName}`);
        this.syncerSocket.emit('messageToKit', request);
    }

    stop() {
        if (this.server) {
            this.server.close();
            console.log(`🛑 Mock Kit Server stopped`);
        }
    }
}

module.exports = MockKitServer;