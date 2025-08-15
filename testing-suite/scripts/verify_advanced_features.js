const io = require('socket.io-client');
const fs = require('fs').promises;
const path = require('path');

console.log('🔬 VERIFICATION: Advanced Features Test');
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

// Advanced features test using multifile test directory
// Advanced project definition removed - now uses ./tests/multifile/ directory

let phases = [];
let fileCount = 0;
let startTime = Date.now();

socket.on('connect', async () => {
    console.log('🔌 Connected for advanced feature testing');
    
    // Load advanced multi-file test files
    const testFiles = await loadTestFiles('../test-data/tests/multifile');
    
    if (!testFiles) {
        console.log('❌ Could not load test files');
        socket.disconnect();
        return;
    }
    
    console.log(`📁 Project structure: ${Object.keys(testFiles).length} files loaded`);
    console.log('  - Multi-directory structure');
    console.log('  - Cross-module dependencies');
    console.log('  - Complex header resolution');
    console.log('📤 Uploading advanced project...\n');
    
    socket.emit('compile_cpp', {
        files: testFiles,
        app_name: "advanced_features_test",
        run: true
    });
});

socket.on('compile_cpp_reply', (data) => {
    const elapsed = Date.now() - startTime;
    phases.push({ status: data.status, time: elapsed, code: data.code });
    
    if (data.status === 'file-written') {
        fileCount++;
        console.log(`📝 [${elapsed}ms] File ${fileCount}/8: ${data.result.trim()}`);
    } else if (data.status.includes('configure')) {
        console.log(`⚙️  [${elapsed}ms] ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 [${elapsed}ms] ${data.result.trim()}`);
    } else if (data.status === 'run-stdout') {
        console.log(`🚀 [${elapsed}ms] ${data.result.trim()}`);
    }
    
    if (data.isDone) {
        console.log(`\n🔬 ADVANCED FEATURES VERIFICATION RESULTS:`);
        console.log(`==========================================`);
        console.log(`🎯 Overall Result: ${data.code === 0 ? '✅ SUCCESS' : '❌ FAILED'}`);
        console.log(`⏱️  Total Time: ${elapsed}ms`);
        console.log(`📊 Total Phases: ${phases.length}`);
        console.log(`📁 Files Processed: ${fileCount}/8`);
        
        console.log(`\n🔍 Feature Verification Details:`);
        
        // Verify file processing
        if (fileCount === 8) {
            console.log(`  ✅ Multi-file processing: All 8 files processed correctly`);
        } else {
            console.log(`  ❌ Multi-file processing: Only ${fileCount}/8 files processed`);
        }
        
        // Verify deep directory structure
        const configurePhases = phases.filter(p => p.status.includes('configure'));
        if (configurePhases.length > 0) {
            console.log(`  ✅ CMake configuration: ${configurePhases.length} configuration steps`);
        } else {
            console.log(`  ❌ CMake configuration: No configuration detected`);
        }
        
        // Verify build process
        const buildPhases = phases.filter(p => p.status.includes('build'));
        if (buildPhases.length > 0) {
            console.log(`  ✅ Build process: ${buildPhases.length} build steps completed`);
        } else {
            console.log(`  ❌ Build process: No build steps detected`);
        }
        
        // Verify execution
        const runPhases = phases.filter(p => p.status.includes('run'));
        if (runPhases.length > 0 && data.code === 0) {
            console.log(`  ✅ Program execution: Successful with exit code 0`);
        } else {
            console.log(`  ❌ Program execution: Failed or no execution detected`);
        }
        
        // Performance analysis
        console.log(`\n📈 Performance Analysis:`);
        console.log(`  ⚡ Files/second: ${(fileCount / (elapsed/1000)).toFixed(1)}`);
        console.log(`  🕐 Average phase time: ${(elapsed/phases.length).toFixed(1)}ms`);
        
        const success = data.code === 0 && fileCount === 8 && buildPhases.length > 0;
        console.log(`\n🏆 ADVANCED VERIFICATION: ${success ? '✅ PASSED' : '❌ FAILED'}`);
        
        socket.disconnect();
    }
});

socket.on('connect_error', (error) => {
    console.error('❌ FAIL: Connection error:', error.message);
    console.log('🏆 ADVANCED VERIFICATION: ❌ FAILED');
    process.exit(1);
});

console.log('🔄 Starting advanced features verification...');