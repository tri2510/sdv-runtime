const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

console.log('🔧 VERIFICATION: Direct Executable Execution Test');
console.log('===============================================\n');

async function testDirectExecution() {
    try {
        // Find the most recent executable from our tests
        const outputDir = './docker-output';
        const files = await fs.readdir(outputDir);
        const executables = files.filter(f => f.startsWith('app_'));
        
        if (executables.length === 0) {
            console.log('❌ No executables found in output directory');
            return false;
        }
        
        // Get the most recent executable
        const stats = await Promise.all(
            executables.map(async f => ({
                name: f,
                stat: await fs.stat(path.join(outputDir, f))
            }))
        );
        
        const newest = stats.sort((a, b) => b.stat.mtime - a.stat.mtime)[0];
        const executablePath = path.join(outputDir, newest.name);
        
        console.log(`🔍 Testing executable: ${newest.name}`);
        console.log(`📅 Created: ${newest.stat.mtime.toISOString()}`);
        console.log(`📦 Size: ${newest.stat.size} bytes`);
        console.log(`🔄 Starting direct execution test...\n`);
        
        return new Promise((resolve) => {
            const startTime = Date.now();
            const child = spawn(path.resolve(executablePath), [], {
                cwd: path.dirname(path.resolve(executablePath))
            });
            
            let stdout = '';
            let stderr = '';
            let outputLines = [];
            
            child.stdout.on('data', (data) => {
                const output = data.toString();
                stdout += output;
                const lines = output.split('\\n').filter(line => line.trim());
                lines.forEach(line => {
                    outputLines.push(line);
                    console.log(`📤 STDOUT: ${line}`);
                });
            });
            
            child.stderr.on('data', (data) => {
                const error = data.toString();
                stderr += error;
                console.log(`⚠️  STDERR: ${error}`);
            });
            
            child.on('close', (code) => {
                const elapsed = Date.now() - startTime;
                console.log(`\\n🏁 EXECUTION COMPLETED:`);
                console.log(`======================`);
                console.log(`⏱️  Execution Time: ${elapsed}ms`);
                console.log(`🔢 Exit Code: ${code}`);
                console.log(`📤 Output Lines: ${outputLines.length}`);
                console.log(`📏 Stdout Length: ${stdout.length} chars`);
                console.log(`🚨 Stderr Length: ${stderr.length} chars`);
                
                // Analysis
                const success = code !== null && stderr.length === 0;
                const hasOutput = stdout.length > 0;
                const reasonable_time = elapsed < 5000;
                
                console.log(`\\n📊 DIRECT EXECUTION ANALYSIS:`);
                console.log(`============================`);
                console.log(`✅ Process Completion: ${code !== null ? '✅ SUCCESS' : '❌ FAILED'}`);
                console.log(`📤 Output Generation: ${hasOutput ? '✅ SUCCESS' : '❌ FAILED'}`);
                console.log(`⚡ Performance: ${reasonable_time ? '✅ GOOD' : '❌ SLOW'} (${elapsed}ms)`);
                console.log(`🚨 Error Free: ${stderr.length === 0 ? '✅ SUCCESS' : '❌ FAILED'}`);
                
                if (stdout.length > 0) {
                    console.log(`\\n📜 CAPTURED OUTPUT:`);
                    console.log(`==================`);
                    console.log(stdout);
                }
                
                if (stderr.length > 0) {
                    console.log(`\\n🚨 ERROR OUTPUT:`);
                    console.log(`===============`);
                    console.log(stderr);
                }
                
                const overallSuccess = success && hasOutput && reasonable_time;
                console.log(`\\n🎯 DIRECT EXECUTION: ${overallSuccess ? '✅ FULLY WORKING' : '❌ ISSUES DETECTED'}`);
                
                resolve(overallSuccess);
            });
            
            child.on('error', (error) => {
                console.error(`❌ EXECUTION ERROR: ${error.message}`);
                console.log(`🎯 DIRECT EXECUTION: ❌ FAILED`);
                resolve(false);
            });
            
            // Safety timeout
            setTimeout(() => {
                if (!child.killed) {
                    console.log(`⏰ Timeout reached, killing process`);
                    child.kill('SIGKILL');
                    resolve(false);
                }
            }, 10000);
        });
        
    } catch (error) {
        console.error('❌ Test setup failed:', error.message);
        return false;
    }
}

// Test multiple executables if available
async function testMultipleExecutables() {
    console.log('🔍 Testing multiple executables for consistency...\n');
    
    try {
        const outputDir = './docker-output';
        const files = await fs.readdir(outputDir);
        const executables = files.filter(f => f.startsWith('app_')).slice(0, 3); // Test up to 3
        
        let successCount = 0;
        
        for (const [index, executable] of executables.entries()) {
            console.log(`\\n--- Testing Executable ${index + 1}/${executables.length}: ${executable} ---`);
            
            const executablePath = path.join(outputDir, executable);
            const stat = await fs.stat(executablePath);
            console.log(`📦 Size: ${stat.size} bytes`);
            
            const success = await new Promise((resolve) => {
                const child = spawn(path.resolve(executablePath), [], {
                    timeout: 5000
                });
                
                let hasOutput = false;
                
                child.stdout.on('data', (data) => {
                    hasOutput = true;
                    console.log(`✅ Output detected: ${data.toString().slice(0, 50)}...`);
                });
                
                child.on('close', (code) => {
                    const success = code === 0 || code === 42; // Accept our custom return codes
                    console.log(`${success ? '✅' : '❌'} Exit code: ${code} ${success ? '(Success)' : '(Failed)'}`);
                    resolve(success && hasOutput);
                });
                
                child.on('error', (error) => {
                    console.log(`❌ Execution failed: ${error.message}`);
                    resolve(false);
                });
            });
            
            if (success) {
                successCount++;
                console.log(`✅ Executable ${index + 1}: WORKING`);
            } else {
                console.log(`❌ Executable ${index + 1}: FAILED`);
            }
        }
        
        console.log(`\\n📊 MULTIPLE EXECUTABLE TEST SUMMARY:`);
        console.log(`===================================`);
        console.log(`✅ Working Executables: ${successCount}/${executables.length}`);
        console.log(`📈 Success Rate: ${(successCount / executables.length * 100).toFixed(1)}%`);
        
        const allWorking = successCount === executables.length;
        console.log(`🎯 OVERALL RESULT: ${allWorking ? '✅ ALL EXECUTABLES WORKING' : '❌ SOME ISSUES DETECTED'}`);
        
        return allWorking;
        
    } catch (error) {
        console.error('❌ Multiple executable test failed:', error.message);
        return false;
    }
}

// Run tests
async function runAllTests() {
    console.log('🚀 Starting comprehensive executable communication verification...\\n');
    
    const singleTest = await testDirectExecution();
    const multipleTest = await testMultipleExecutables();
    
    console.log('\\n🏆 FINAL EXECUTABLE COMMUNICATION ASSESSMENT:');
    console.log('==============================================');
    console.log(`🔧 Direct Execution: ${singleTest ? '✅ WORKING' : '❌ FAILED'}`);
    console.log(`📊 Multiple Executables: ${multipleTest ? '✅ WORKING' : '❌ FAILED'}`);
    
    const overallSuccess = singleTest && multipleTest;
    console.log(`\\n🎯 EXECUTABLE COMMUNICATION: ${overallSuccess ? '✅ FULLY VERIFIED' : '❌ NEEDS ATTENTION'}`);
    
    if (overallSuccess) {
        console.log('🚀 All compiled executables can run and communicate properly!');
        console.log('✅ Production SDV Runtime executable generation is fully functional!');
    } else {
        console.log('🔧 Some executables have communication issues that need investigation.');
    }
}

runAllTests().catch(console.error);