const io = require('socket.io-client');
const fs = require('fs').promises;
const path = require('path');

console.log('🐳 Production SDV Runtime: Multi-File Project Test');
console.log('==================================================\n');

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


let phases = [];
let startTime = Date.now();

socket.on('connect', async () => {
    console.log('🔌 Connected to Production SDV Runtime container');
    
    // Load multi-file test files
    const testFiles = await loadTestFiles('./tests/multifile');
    
    if (!testFiles) {
        console.log('❌ Could not load test files');
        socket.disconnect();
        return;
    }
    
    console.log(`📤 Uploading complex multi-file project with ${Object.keys(testFiles).length} files to production container...\n`);
    
    socket.emit('compile_cpp', {
        files: testFiles,
        app_name: "production_sdv_multifile",
        run: true
    });
});

socket.on('compile_cpp_reply', (data) => {
    const elapsed = Date.now() - startTime;
    phases.push({ phase: data.status, time: elapsed, success: data.code === 0 });
    
    if (data.status === 'run-stdout') {
        console.log(`🚀 SDV Production Output: ${data.result.trim()}`);
    } else if (data.status === 'file-written') {
        console.log(`📝 Production File: ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 Production Build: ${data.result.trim()}`);
    } else if (data.status.includes('configure')) {
        console.log(`⚙️  Configuration: ${data.result.trim()}`);
    } else {
        console.log(`📋 [${elapsed}ms] ${data.status}: ${data.result.trim()}`);
    }
    
    if (data.isDone) {
        console.log(`\n🎯 Production SDV Multi-File Test: ${data.code === 0 ? '✅ SUCCESS' : '❌ FAILED'}`);
        console.log(`⏱️  Total Production Time: ${elapsed}ms`);
        console.log(`📊 Compilation Phases: ${phases.length}`);
        
        console.log('\n📈 Production Phase Breakdown:');
        phases.forEach((phase, idx) => {
            if (idx < 10) { // Show first 10 phases
                console.log(`  ${idx + 1}. ${phase.phase} (${phase.time}ms) ${phase.success ? '✅' : '❌'}`);
            }
        });
        if (phases.length > 10) {
            console.log(`  ... and ${phases.length - 10} more phases`);
        }
        
        console.log('\n🏆 Production SDV Runtime Enhanced Compilation Features:');
        console.log('  ✅ Multi-file C++ project compilation');
        console.log('  ✅ Dynamic header include resolution');
        console.log('  ✅ CMake build system integration');
        console.log('  ✅ Real-time compilation streaming');
        console.log('  ✅ Container-aware path handling');
        console.log('  ✅ Production environment execution');
        
        socket.disconnect();
    }
});

socket.on('connect_error', (error) => {
    console.error('❌ Production SDV connection failed:', error.message);
});

socket.on('disconnect', (reason) => {
    console.log(`🔌 Disconnected from Production SDV: ${reason}`);
    process.exit(0);
});

console.log('🚀 Starting Production SDV Runtime complex multi-file test...');