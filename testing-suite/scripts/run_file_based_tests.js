const { spawn } = require('child_process');
const path = require('path');

console.log('📁 FILE-BASED TEST SUITE');
console.log('=======================\n');

const tests = [
    {
        name: 'Simple Test from Files',
        script: 'test_simple_from_files.js',
        description: 'Basic C++ compilation with file-based input'
    },
    {
        name: 'Multi-file Test from Files', 
        script: 'test_multifile_from_files.js',
        description: 'Complex multi-directory project with file-based input'
    },
    {
        name: 'Communication Test from Files',
        script: 'test_communication_from_files.js', 
        description: 'Executable communication testing with file-based input'
    }
];

let currentTest = 0;
let results = [];

function runTest(test) {
    return new Promise((resolve) => {
        console.log(`\n${'='.repeat(60)}`);
        console.log(`🧪 RUNNING: ${test.name}`);
        console.log(`📝 ${test.description}`);
        console.log(`📄 Script: ${test.script}`);
        console.log(`${'='.repeat(60)}\n`);
        
        const startTime = Date.now();
        const child = spawn('node', [test.script], {
            cwd: __dirname,
            stdio: 'pipe'
        });
        
        let stdout = '';
        let stderr = '';
        
        child.stdout.on('data', (data) => {
            const output = data.toString();
            stdout += output;
            process.stdout.write(output);
        });
        
        child.stderr.on('data', (data) => {
            const error = data.toString();
            stderr += error;
            process.stderr.write(error);
        });
        
        child.on('close', (code) => {
            const duration = Date.now() - startTime;
            const success = code === 0;
            
            console.log(`\n${'─'.repeat(60)}`);
            console.log(`🏁 ${test.name} completed in ${duration}ms`);
            console.log(`📊 Exit Code: ${code} ${success ? '✅' : '❌'}`);
            console.log(`${'─'.repeat(60)}\n`);
            
            results.push({
                name: test.name,
                success: success,
                duration: duration,
                exitCode: code,
                hasOutput: stdout.length > 0,
                hasErrors: stderr.length > 0
            });
            
            resolve();
        });
        
        child.on('error', (error) => {
            console.error(`❌ Failed to run ${test.name}:`, error.message);
            results.push({
                name: test.name,
                success: false,
                duration: Date.now() - startTime,
                exitCode: -1,
                hasOutput: false,
                hasErrors: true,
                error: error.message
            });
            resolve();
        });
    });
}

async function runAllTests() {
    console.log('🚀 Starting file-based test suite...\n');
    
    for (const test of tests) {
        await runTest(test);
        // Small delay between tests
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    // Generate final report
    console.log('\n' + '='.repeat(80));
    console.log('📊 FILE-BASED TEST SUITE FINAL REPORT');
    console.log('='.repeat(80));
    
    const successCount = results.filter(r => r.success).length;
    const totalTests = results.length;
    const overallSuccess = successCount === totalTests;
    
    console.log(`\n🎯 OVERALL RESULT: ${overallSuccess ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
    console.log(`📈 Success Rate: ${successCount}/${totalTests} (${(successCount/totalTests*100).toFixed(1)}%)`);
    
    console.log(`\n📋 DETAILED RESULTS:`);
    console.log('==================');
    
    results.forEach((result, index) => {
        console.log(`\n${index + 1}. ${result.name}`);
        console.log(`   Status: ${result.success ? '✅ PASSED' : '❌ FAILED'}`);
        console.log(`   Duration: ${result.duration}ms`);
        console.log(`   Exit Code: ${result.exitCode}`);
        console.log(`   Output: ${result.hasOutput ? '✅' : '❌'}`);
        console.log(`   Errors: ${result.hasErrors ? '⚠️' : '✅'}`);
        if (result.error) {
            console.log(`   Error: ${result.error}`);
        }
    });
    
    console.log(`\n⏱️  PERFORMANCE SUMMARY:`);
    console.log('======================');
    const totalDuration = results.reduce((sum, r) => sum + r.duration, 0);
    const avgDuration = totalDuration / results.length;
    console.log(`   Total Time: ${totalDuration}ms`);
    console.log(`   Average Time: ${avgDuration.toFixed(0)}ms per test`);
    console.log(`   Fastest Test: ${Math.min(...results.map(r => r.duration))}ms`);
    console.log(`   Slowest Test: ${Math.max(...results.map(r => r.duration))}ms`);
    
    if (overallSuccess) {
        console.log(`\n🎉 FILE-BASED TESTING APPROACH: ✅ FULLY VALIDATED`);
        console.log(`📁 All file-based input methods working perfectly!`);
        console.log(`🔄 Tests are now more transparent and maintainable!`);
    } else {
        console.log(`\n⚠️  FILE-BASED TESTING APPROACH: ❌ NEEDS ATTENTION`);
        console.log(`🔧 Some file-based tests failed - check results above`);
    }
    
    console.log('\n' + '='.repeat(80));
}

runAllTests().catch(console.error);