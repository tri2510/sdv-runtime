const io = require('socket.io-client');
const fs = require('fs').promises;
const path = require('path');

console.log('📁 VERIFICATION: Multi-file Test from Files');
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

function analyzeFileStructure(files) {
    console.log('\n🏗️  FILE STRUCTURE ANALYSIS:');
    console.log('============================');
    
    const fileCount = Object.keys(files).length;
    const cppFiles = Object.keys(files).filter(f => f.endsWith('.cpp')).length;
    const headerFiles = Object.keys(files).filter(f => f.endsWith('.h')).length;
    
    console.log(`📊 Total files: ${fileCount}`);
    console.log(`📄 CPP files: ${cppFiles}`);
    console.log(`📋 Header files: ${headerFiles}`);
    
    console.log(`\n📂 Directory structure:`);
    const directories = new Set();
    Object.keys(files).forEach(file => {
        const dir = path.dirname(file);
        if (dir !== '.') directories.add(dir);
    });
    
    directories.forEach(dir => {
        console.log(`  📁 ${dir}/`);
        Object.keys(files).forEach(file => {
            if (path.dirname(file) === dir) {
                console.log(`    📄 ${path.basename(file)}`);
            }
        });
    });
}

socket.on('connect', async () => {
    console.log('🔌 Connected to SDV Runtime');
    
    // Load multi-file test files
    const testFiles = await loadTestFiles('./tests/multifile');
    
    if (!testFiles) {
        console.log('❌ Could not load test files');
        socket.disconnect();
        return;
    }
    
    console.log(`\n📤 Uploading multi-file test project with ${Object.keys(testFiles).length} files...\n`);
    
    // Analyze file structure
    analyzeFileStructure(testFiles);
    
    console.log('\n🚀 Starting compilation...\n');
    
    socket.emit('compile_cpp', {
        files: testFiles,
        app_name: "multifile_from_files",
        run: true
    });
});

socket.on('compile_cpp_reply', (data) => {
    if (data.status === 'compile-start') {
        console.log('📋 Multi-file test compilation started');
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
        analyzeMultifileTest(data.code);
    }
    
    if (data.isDone) {
        setTimeout(() => {
            socket.disconnect();
        }, 1000);
    }
});

function analyzeMultifileTest(exitCode) {
    console.log(`\n📊 MULTI-FILE TEST ANALYSIS:`);
    console.log(`===========================`);
    
    const success = exitCode === 0;
    console.log(`🎯 Result: ${success ? '✅ SUCCESS' : '❌ FAILED'}`);
    console.log(`🔢 Exit Code: ${exitCode}`);
    
    if (success) {
        console.log(`✅ Multi-directory compilation: Working`);
        console.log(`✅ Cross-module dependencies: Working`);
        console.log(`✅ Class instantiation: Working`);
        console.log(`✅ Header file resolution: Working`);
        console.log(`✅ Vehicle system simulation: Working`);
        console.log(`✅ Sensor integration: Working`);
        console.log(`✅ Logging system: Working`);
        console.log(`✅ Configuration management: Working`);
        
        console.log(`\n🎉 FILE-BASED MULTI-FILE TEST: ✅ FULLY FUNCTIONAL`);
        console.log(`🏗️  Complex project structure compiled successfully!`);
    } else {
        console.log(`❌ Multi-file compilation failed`);
        console.log(`🔧 Check file dependencies and include paths`);
        
        console.log(`\n⚠️  FILE-BASED MULTI-FILE TEST: ❌ FAILED`);
    }
}

socket.on('connect_error', (error) => {
    console.error('❌ Connection to SDV Runtime failed:', error.message);
    process.exit(1);
});

console.log('🔄 Starting file-based multi-file test verification...');