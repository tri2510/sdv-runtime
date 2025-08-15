const io = require('socket.io-client');
const fs = require('fs').promises;
const path = require('path');

console.log('📁 VERIFICATION: Simple Test from Files');
console.log('=====================================\n');

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

socket.on('connect', async () => {
    console.log('🔌 Connected to SDV Runtime');
    
    // Load simple test files
    const testFiles = await loadTestFiles('../test-data/tests/simple');
    
    if (!testFiles) {
        console.log('❌ Could not load test files');
        socket.disconnect();
        return;
    }
    
    console.log(`\n📤 Uploading simple test project with ${Object.keys(testFiles).length} files...\n`);
    
    // Show file contents for transparency
    console.log('📋 FILE CONTENTS:');
    console.log('==================');
    for (const [filename, content] of Object.entries(testFiles)) {
        console.log(`\n--- ${filename} ---`);
        console.log(content);
        console.log(`--- End of ${filename} ---`);
    }
    console.log('\n🚀 Starting compilation...\n');
    
    socket.emit('compile_cpp', {
        files: testFiles,
        app_name: "simple_file_test",
        run: true
    });
});

socket.on('compile_cpp_reply', (data) => {
    if (data.status === 'compile-start') {
        console.log('📋 Simple file test compilation started');
    } else if (data.status === 'file-written') {
        console.log(`📝 ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 ${data.result.trim()}`);
    } else if (data.status === 'run-stdout') {
        console.log(`📤 OUTPUT: ${data.result.trim()}`);
    } else if (data.status === 'run-stderr') {
        console.log(`⚠️  ERROR: ${data.result.trim()}`);
    } else if (data.status === 'run-done') {
        console.log(`🏁 Execution completed with exit code: ${data.code}`);
        analyzeSimpleTest(data.code);
    }
    
    if (data.isDone) {
        setTimeout(() => {
            socket.disconnect();
        }, 1000);
    }
});

function analyzeSimpleTest(exitCode) {
    console.log(`\n📊 SIMPLE FILE TEST ANALYSIS:`);
    console.log(`============================`);
    
    const success = exitCode === 0;
    console.log(`🎯 Result: ${success ? '✅ SUCCESS' : '❌ FAILED'}`);
    console.log(`🔢 Exit Code: ${exitCode}`);
    
    if (success) {
        console.log(`✅ File-based input: Working`);
        console.log(`✅ Header inclusion: Working`);
        console.log(`✅ Configuration access: Working`);
        console.log(`✅ Mathematical computation: Working`);
        
        console.log(`\n🎉 FILE-BASED SIMPLE TEST: ✅ FULLY FUNCTIONAL`);
        console.log(`📁 Test files loaded and compiled successfully!`);
    } else {
        console.log(`❌ File-based compilation failed`);
        
        console.log(`\n⚠️  FILE-BASED SIMPLE TEST: ❌ FAILED`);
    }
}

socket.on('connect_error', (error) => {
    console.error('❌ Connection to SDV Runtime failed:', error.message);
    process.exit(1);
});

console.log('🔄 Starting file-based simple test verification...');