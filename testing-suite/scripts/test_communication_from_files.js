const io = require('socket.io-client');
const fs = require('fs').promises;
const path = require('path');

console.log('📁 VERIFICATION: Communication Test from Files');
console.log('==============================================\n');

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

async function verifyFileOutput() {
    try {
        const outputFile = '/tmp/executable_output.txt';
        const content = await fs.readFile(outputFile, 'utf8');
        
        console.log('\n📄 FILE OUTPUT VERIFICATION:');
        console.log('============================');
        console.log('✅ File created successfully');
        console.log(`📄 File content: ${content.length} characters`);
        console.log('\n📜 File contents:');
        console.log(content);
        
        // Check if content contains expected elements
        const hasTimestamp = content.includes('Timestamp:');
        const hasVersion = content.includes('Version:');
        const hasSuccessMessage = content.includes('File communication test successful');
        
        console.log('\n✅ Content verification:');
        console.log(`   Timestamp: ${hasTimestamp ? '✅' : '❌'}`);
        console.log(`   Version info: ${hasVersion ? '✅' : '❌'}`);
        console.log(`   Success message: ${hasSuccessMessage ? '✅' : '❌'}`);
        
        return hasTimestamp && hasVersion && hasSuccessMessage;
    } catch (error) {
        console.log('❌ Could not read output file:', error.message);
        return false;
    }
}

socket.on('connect', async () => {
    console.log('🔌 Connected to SDV Runtime');
    
    // Load communication test files
    const testFiles = await loadTestFiles('../test-data/tests/communication');
    
    if (!testFiles) {
        console.log('❌ Could not load test files');
        socket.disconnect();
        return;
    }
    
    console.log(`\n📤 Uploading communication test project with ${Object.keys(testFiles).length} files...\n`);
    
    // Show what we're testing
    console.log('🧪 COMMUNICATION TESTS:');
    console.log('=======================');
    console.log('📤 Standard output with special characters');
    console.log('📄 File I/O operations');  
    console.log('🔢 Custom exit codes (42)');
    console.log('⏱️  Performance measurements');
    console.log('📋 Configuration access');
    
    console.log('\n🚀 Starting compilation...\n');
    
    socket.emit('compile_cpp', {
        files: testFiles,
        app_name: "comm_from_files",
        run: true
    });
});

let outputLines = [];

socket.on('compile_cpp_reply', (data) => {
    if (data.status === 'compile-start') {
        console.log('📋 Communication test compilation started');
    } else if (data.status === 'file-written') {
        console.log(`📝 ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 ${data.result.trim()}`);
    } else if (data.status === 'run-stdout') {
        const output = data.result.trim();
        outputLines.push(output);
        console.log(`📤 EXEC OUTPUT: ${output}`);
    } else if (data.status === 'run-stderr') {
        console.log(`⚠️  ERROR: ${data.result.trim()}`);
    } else if (data.status === 'run-done') {
        console.log(`🏁 Execution completed with exit code: ${data.code}`);
        analyzeCommunicationTest(data.code, outputLines);
    }
    
    if (data.isDone) {
        setTimeout(async () => {
            await verifyFileOutput();
            socket.disconnect();
        }, 1000);
    }
});

function analyzeCommunicationTest(exitCode, outputs) {
    console.log(`\n📊 COMMUNICATION TEST ANALYSIS:`);
    console.log(`==============================`);
    
    const expectedExitCode = 42;
    const correctExitCode = exitCode === expectedExitCode;
    console.log(`🔢 Exit Code: ${exitCode} ${correctExitCode ? '✅ (Custom code working)' : '❌ (Expected 42)'}`);
    
    // Analyze output content
    const outputText = outputs.join(' ');
    const hasMessage = outputText.includes('MESSAGE:');
    const hasStatus = outputText.includes('STATUS:');
    const hasSpecialChars = outputText.includes('SPECIAL_CHARS:');
    const hasMultiLine = outputText.includes('MULTI_LINE_START:');
    const hasFileCreated = outputText.includes('FILE_CREATED:');
    const hasPerformance = outputText.includes('PERFORMANCE:');
    const hasConfig = outputText.includes('CONFIG:');
    
    console.log('\n✅ Output verification:');
    console.log(`   Message format: ${hasMessage ? '✅' : '❌'}`);
    console.log(`   Status reporting: ${hasStatus ? '✅' : '❌'}`);
    console.log(`   Special characters: ${hasSpecialChars ? '✅' : '❌'}`);
    console.log(`   Multi-line output: ${hasMultiLine ? '✅' : '❌'}`);
    console.log(`   File creation: ${hasFileCreated ? '✅' : '❌'}`);
    console.log(`   Performance data: ${hasPerformance ? '✅' : '❌'}`);
    console.log(`   Configuration access: ${hasConfig ? '✅' : '❌'}`);
    
    console.log(`\n📏 Output statistics:`);
    console.log(`   Total output lines: ${outputs.length}`);
    console.log(`   Total characters: ${outputText.length}`);
    
    const allTestsPassed = correctExitCode && hasMessage && hasStatus && 
                          hasSpecialChars && hasMultiLine && hasFileCreated && 
                          hasPerformance && hasConfig;
    
    if (allTestsPassed) {
        console.log(`\n🎉 FILE-BASED COMMUNICATION TEST: ✅ FULLY FUNCTIONAL`);
        console.log(`📞 All communication channels working perfectly!`);
        console.log(`📄 Standard output, file I/O, and exit codes all verified!`);
    } else {
        console.log(`\n⚠️  FILE-BASED COMMUNICATION TEST: ❌ SOME ISSUES`);
        console.log(`🔧 Check failed communication channels above`);
    }
}

socket.on('connect_error', (error) => {
    console.error('❌ Connection to SDV Runtime failed:', error.message);
    process.exit(1);
});

console.log('🔄 Starting file-based communication test verification...');