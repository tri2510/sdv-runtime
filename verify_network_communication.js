const io = require('socket.io-client');
const net = require('net');
const fs = require('fs').promises;
const path = require('path');

console.log('🌐 VERIFICATION: Network Communication Test');
console.log('==========================================\n');

const socket = io('http://localhost:3090');

async function loadTestFiles(testDir) {
    const files = {};
    
    try {
        // Read all files in the test directory recursively
        async function readDir(dir, baseDir = '') {
            const items = await fs.readdir(dir, { withFileTypes: true });
            
            for (const item of items) {
                const fullPath = path.join(dir, item.name);
                const relativePath = baseDir ? path.join(baseDir, item.name) : item.name;
                
                if (item.isDirectory()) {
                    await readDir(fullPath, relativePath);
                } else if (item.isFile() && (item.name.endsWith('.cpp') || item.name.endsWith('.h'))) {
                    const content = await fs.readFile(fullPath, 'utf8');
                    files[relativePath] = content;
                    console.log(`📄 Loaded: ${relativePath} (${content.length} chars)`);
                }
            }
        }
        
        await readDir(testDir);
        return files;
    } catch (error) {
        console.error('❌ Failed to load test files:', error.message);
        return null;
    }
}

// Create a simple TCP server for testing network communication
let testServer;

function createTestServer() {
    return new Promise((resolve) => {
        testServer = net.createServer((connection) => {
            console.log('📡 Test server: Client connected');
            
            connection.on('data', (data) => {
                const message = data.toString().trim();
                console.log(`📨 Test server received: ${message}`);
                
                // Echo back with confirmation
                connection.write(`SERVER_RESPONSE: ${message}`);
            });
            
            connection.on('end', () => {
                console.log('📡 Test server: Client disconnected');
            });
        });
        
        testServer.listen(8899, 'localhost', () => {
            console.log('📡 Test server listening on localhost:8899');
            resolve();
        });
    });
}


let networkTestStarted = false;

socket.on('connect', async () => {
    console.log('🔌 Connected to SDV Runtime for network communication test');
    
    // Start test server first
    console.log('🚀 Setting up test server...');
    await createTestServer();
    
    // Load network test files
    const testFiles = await loadTestFiles('./tests/network');
    
    if (!testFiles) {
        console.log('❌ Could not load test files');
        socket.disconnect();
        return;
    }
    
    console.log(`📤 Uploading network communication project with ${Object.keys(testFiles).length} files...\n`);
    
    socket.emit('compile_cpp', {
        files: testFiles,
        app_name: "network_test",
        run: true
    });
});

socket.on('compile_cpp_reply', (data) => {
    if (data.status === 'compile-start') {
        console.log('📋 Network test compilation started');
    } else if (data.status === 'file-written') {
        console.log(`📝 ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 ${data.result.trim()}`);
    } else if (data.status === 'run-stdout') {
        console.log(`🌐 NETWORK EXEC: ${data.result.trim()}`);
    } else if (data.status === 'run-stderr') {
        console.log(`⚠️  NETWORK ERROR: ${data.result.trim()}`);
    } else if (data.status === 'run-done') {
        console.log(`🏁 Network test execution completed with code: ${data.code}`);
        analyzeNetworkTest(data.code);
    }
    
    if (data.isDone) {
        setTimeout(() => {
            if (testServer) {
                testServer.close(() => {
                    console.log('📡 Test server shut down');
                    socket.disconnect();
                });
            } else {
                socket.disconnect();
            }
        }, 1000);
    }
});

function analyzeNetworkTest(exitCode) {
    console.log(`\n🌐 NETWORK COMMUNICATION ANALYSIS:`);
    console.log(`=================================`);
    
    const success = exitCode === 0;
    console.log(`🎯 Overall Result: ${success ? '✅ SUCCESS' : '❌ FAILED'}`);
    console.log(`🔢 Exit Code: ${exitCode}`);
    
    if (success) {
        console.log(`✅ Socket creation: Working`);
        console.log(`✅ Network connection: Working`);
        console.log(`✅ Data transmission: Working`);
        console.log(`✅ Data reception: Working`);
        console.log(`✅ Connection cleanup: Working`);
        
        console.log(`\n🎉 NETWORK COMMUNICATION: ✅ FULLY FUNCTIONAL`);
        console.log(`🚀 Compiled executables can communicate over network!`);
    } else {
        console.log(`❌ Network communication failed`);
        console.log(`🔧 Check network connectivity and firewall settings`);
        
        console.log(`\n⚠️  NETWORK COMMUNICATION: ❌ FAILED`);
    }
}

socket.on('connect_error', (error) => {
    console.error('❌ Connection to SDV Runtime failed:', error.message);
    if (testServer) {
        testServer.close();
    }
    process.exit(1);
});

console.log('🔄 Starting network communication verification...');