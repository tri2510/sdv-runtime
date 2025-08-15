const io = require('socket.io-client');
const fs = require('fs').promises;
const { spawn } = require('child_process');
const path = require('path');

console.log('🔧 VERIFICATION: Executable Communication Test');
console.log('=============================================\n');

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

let compilationPhases = [];
let executionOutput = [];
let startTime = Date.now();
let executablePath = '';

socket.on('connect', async () => {
    console.log('🔌 Connected for executable communication testing');
    
    // Load communication test files
    const testFiles = await loadTestFiles('./tests/communication');
    
    if (!testFiles) {
        console.log('❌ Could not load test files');
        socket.disconnect();
        return;
    }
    
    console.log(`📤 Uploading communication test project with ${Object.keys(testFiles).length} files...\n`);
    
    socket.emit('compile_cpp', {
        files: testFiles,
        app_name: "communication_test",
        run: true  // This will test execution
    });
});

socket.on('compile_cpp_reply', (data) => {
    const elapsed = Date.now() - startTime;
    
    if (data.status === 'compile-start') {
        console.log(`📋 [${elapsed}ms] Compilation started`);
        compilationPhases.push({phase: 'start', time: elapsed});
    } else if (data.status === 'file-written') {
        console.log(`📝 [${elapsed}ms] ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 [${elapsed}ms] ${data.result.trim()}`);
        compilationPhases.push({phase: 'build', time: elapsed});
    } else if (data.status === 'build-done') {
        console.log(`✅ [${elapsed}ms] Build completed with code ${data.code}`);
        if (data.code === 0) {
            console.log(`🎯 Executable should be ready for communication testing`);
        }
    } else if (data.status === 'run-stdout') {
        // This is the key part - testing executable communication
        const output = data.result.trim();
        executionOutput.push(output);
        console.log(`🚀 [${elapsed}ms] EXEC: ${output}`);
    } else if (data.status === 'run-stderr') {
        console.log(`⚠️  [${elapsed}ms] EXEC ERROR: ${data.result.trim()}`);
    } else if (data.status === 'run-done') {
        console.log(`🏁 [${elapsed}ms] Execution completed with exit code: ${data.code}`);
        analyzeExecutableCommunication(data.code, elapsed);
    }
    
    if (data.isDone) {
        socket.disconnect();
    }
});

function analyzeExecutableCommunication(exitCode, totalTime) {
    console.log(`\n🔍 EXECUTABLE COMMUNICATION ANALYSIS:`);
    console.log(`=====================================`);
    
    // Test 1: Standard Output Communication
    const hasStandardOutput = executionOutput.some(line => line.includes('MESSAGE:'));
    console.log(`📤 Standard Output: ${hasStandardOutput ? '✅ WORKING' : '❌ FAILED'}`);
    
    if (hasStandardOutput) {
        const messageLines = executionOutput.filter(line => line.includes('MESSAGE:'));
        messageLines.forEach(line => {
            console.log(`   📨 ${line}`);
        });
    }
    
    // Test 2: Status Communication
    const hasStatusUpdates = executionOutput.some(line => line.includes('STATUS:'));
    console.log(`📊 Status Updates: ${hasStatusUpdates ? '✅ WORKING' : '❌ FAILED'}`);
    
    // Test 3: File Communication
    const hasFileOutput = executionOutput.some(line => line.includes('FILE:'));
    console.log(`📁 File Communication: ${hasFileOutput ? '✅ WORKING' : '❌ FAILED'}`);
    
    // Test 4: Return Code Communication
    const expectedReturnCode = 42;
    const returnCodeCorrect = exitCode === expectedReturnCode;
    console.log(`🔢 Return Code: ${returnCodeCorrect ? '✅ WORKING' : '❌ FAILED'} (expected: ${expectedReturnCode}, got: ${exitCode})`);
    
    // Test 5: Performance Communication
    const hasPerformanceData = executionOutput.some(line => line.includes('PERFORMANCE:'));
    console.log(`⚡ Performance Data: ${hasPerformanceData ? '✅ WORKING' : '❌ FAILED'}`);
    
    if (hasPerformanceData) {
        const perfLines = executionOutput.filter(line => line.includes('PERFORMANCE:'));
        perfLines.forEach(line => {
            console.log(`   ⏱️  ${line}`);
        });
    }
    
    // Test 6: Multi-line Communication
    const hasMultilineStart = executionOutput.some(line => line.includes('MULTILINE_START'));
    const hasMultilineEnd = executionOutput.some(line => line.includes('MULTILINE_END'));
    const multilineWorking = hasMultilineStart && hasMultilineEnd;
    console.log(`📄 Multi-line Output: ${multilineWorking ? '✅ WORKING' : '❌ FAILED'}`);
    
    // Test 7: Output Completeness
    const totalOutputLines = executionOutput.length;
    const expectedMinimumLines = 8; // Based on our test program
    const outputComplete = totalOutputLines >= expectedMinimumLines;
    console.log(`📋 Output Completeness: ${outputComplete ? '✅ WORKING' : '❌ FAILED'} (${totalOutputLines} lines)`);
    
    // Overall Assessment
    const testsResults = [
        hasStandardOutput,
        hasStatusUpdates, 
        hasFileOutput,
        returnCodeCorrect,
        hasPerformanceData,
        multilineWorking,
        outputComplete
    ];
    
    const passedTests = testsResults.filter(Boolean).length;
    const totalTests = testsResults.length;
    const successRate = (passedTests / totalTests * 100).toFixed(1);
    
    console.log(`\n📊 COMMUNICATION TEST SUMMARY:`);
    console.log(`=============================`);
    console.log(`✅ Passed Tests: ${passedTests}/${totalTests}`);
    console.log(`📈 Success Rate: ${successRate}%`);
    console.log(`⏱️  Total Time: ${totalTime}ms`);
    console.log(`📤 Output Lines: ${totalOutputLines}`);
    
    if (passedTests === totalTests) {
        console.log(`\n🎉 EXECUTABLE COMMUNICATION: ✅ FULLY WORKING`);
        console.log(`🚀 All communication channels verified successfully!`);
    } else {
        console.log(`\n⚠️  EXECUTABLE COMMUNICATION: ❌ PARTIAL ISSUES`);
        console.log(`🔧 Some communication channels need attention`);
    }
    
    // Display captured output for verification
    console.log(`\n📜 COMPLETE EXECUTABLE OUTPUT:`);
    console.log(`=============================`);
    executionOutput.forEach((line, index) => {
        console.log(`${(index + 1).toString().padStart(2, ' ')}. ${line}`);
    });
}

socket.on('connect_error', (error) => {
    console.error('❌ Connection failed:', error.message);
    process.exit(1);
});

console.log('🔄 Starting executable communication verification...');