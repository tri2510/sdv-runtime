const io = require('socket.io-client');
const fs = require('fs').promises;
const path = require('path');

console.log('🐳 Production SDV Runtime: Simple C++ Test');
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

let startTime = Date.now();

socket.on('connect', async () => {
    console.log('🔌 Connected to Production SDV Runtime');
    
    // Load simple test files
    const testFiles = await loadTestFiles('../test-data/tests/simple');
    
    if (!testFiles) {
        console.log('❌ Could not load test files');
        socket.disconnect();
        return;
    }
    
    console.log(`📤 Sending C++ project with ${Object.keys(testFiles).length} files for compilation...\n`);
    
    // Send compilation request
    socket.emit('compile_cpp', {
        files: testFiles,
        app_name: "simple_test",
        run: true  // Execute after compilation
    });
});

socket.on('compile_cpp_reply', (data) => {
    const elapsed = Date.now() - startTime;
    
    if (data.status === 'run-stdout') {
        console.log(`🚀 [${elapsed}ms] Program Output: ${data.result.trim()}`);
    } else if (data.status === 'file-written') {
        console.log(`📝 [${elapsed}ms] ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 [${elapsed}ms] ${data.result.trim()}`);
    } else {
        console.log(`📋 [${elapsed}ms] ${data.status}: ${data.result.trim()}`);
    }
    
    if (data.isDone) {
        console.log(`\n🎯 Result: ${data.code === 0 ? '✅ SUCCESS' : '❌ FAILED'}`);
        console.log(`⏱️  Total Time: ${elapsed}ms`);
        socket.disconnect();
    }
});

socket.on('connect_error', (error) => {
    console.error('❌ Connection failed:', error.message);
    process.exit(1);
});
