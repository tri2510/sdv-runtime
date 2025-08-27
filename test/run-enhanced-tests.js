// Copyright (c) 2025 Eclipse Foundation.
// 
// This program and the accompanying materials are made available under the
// terms of the MIT License which is available at
// https://opensource.org/licenses/MIT.
//
// SPDX-License-Identifier: MIT

const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Running Enhanced C++ Compilation Feature Tests');
console.log('================================================');

// Test configuration
const testConfig = {
    timeout: 60000,
    reporter: 'spec',
    grep: process.argv[2] || '', // Allow test filtering
};

// Test suites to run
const testSuites = [
    // Original tests (backward compatibility)
    '01-hello-world',
    '02-tree-format', 
    '03-multi-file-tree',
    '06-automotive-basic',
    '09-error-handling',
    
    // New enhanced feature tests
    '10-enhanced-library-compilation',
    '11-session-package-installation', 
    '12-advanced-compilation',
    '13-conan-integration',
    '14-backward-compatibility'
];

let totalPassed = 0;
let totalFailed = 0;
let totalSkipped = 0;

async function runTestSuite(suiteName) {
    return new Promise((resolve) => {
        console.log(`\n📋 Running test suite: ${suiteName}`);
        console.log('─'.repeat(50));
        
        const testPath = path.join(__dirname, suiteName, 'test.js');
        const mocha = spawn('npx', ['mocha', testPath, '--timeout', testConfig.timeout, '--reporter', testConfig.reporter], {
            stdio: 'pipe',
            cwd: __dirname
        });

        let stdout = '';
        let stderr = '';
        
        mocha.stdout.on('data', (data) => {
            stdout += data;
            process.stdout.write(data);
        });
        
        mocha.stderr.on('data', (data) => {
            stderr += data;
            process.stderr.write(data);
        });
        
        mocha.on('close', (code) => {
            // Parse test results from output
            const passMatch = stdout.match(/(\d+) passing/);
            const failMatch = stdout.match(/(\d+) failing/);
            const skipMatch = stdout.match(/(\d+) pending/);
            
            const passed = passMatch ? parseInt(passMatch[1]) : 0;
            const failed = failMatch ? parseInt(failMatch[1]) : 0;
            const skipped = skipMatch ? parseInt(skipMatch[1]) : 0;
            
            totalPassed += passed;
            totalFailed += failed;
            totalSkipped += skipped;
            
            const status = code === 0 ? '✅ PASSED' : '❌ FAILED';
            console.log(`\n${status}: ${suiteName} (${passed} passed, ${failed} failed, ${skipped} skipped)`);
            
            resolve({
                suite: suiteName,
                code,
                passed,
                failed,
                skipped,
                stdout,
                stderr
            });
        });

        mocha.on('error', (err) => {
            console.error(`❌ ERROR running ${suiteName}:`, err.message);
            resolve({
                suite: suiteName,
                code: 1,
                passed: 0,
                failed: 1,
                skipped: 0,
                error: err.message
            });
        });
    });
}

async function runAllTests() {
    const startTime = Date.now();
    const results = [];
    
    console.log(`Starting test run with ${testSuites.length} test suites...`);
    
    for (const suite of testSuites) {
        try {
            const result = await runTestSuite(suite);
            results.push(result);
        } catch (err) {
            console.error(`Fatal error running ${suite}:`, err);
            results.push({
                suite,
                code: 1,
                passed: 0,
                failed: 1,
                skipped: 0,
                error: err.message
            });
        }
    }
    
    const endTime = Date.now();
    const duration = (endTime - startTime) / 1000;
    
    // Final summary
    console.log('\n' + '='.repeat(60));
    console.log('📊 TEST SUMMARY');
    console.log('='.repeat(60));
    
    console.log(`⏱️  Total time: ${duration.toFixed(2)}s`);
    console.log(`📈 Total tests: ${totalPassed + totalFailed}`);
    console.log(`✅ Passed: ${totalPassed}`);
    console.log(`❌ Failed: ${totalFailed}`);
    console.log(`⏭️  Skipped: ${totalSkipped}`);
    
    console.log('\n📋 Detailed Results:');
    results.forEach(result => {
        const status = result.code === 0 ? '✅' : '❌';
        console.log(`  ${status} ${result.suite}: ${result.passed}P, ${result.failed}F, ${result.skipped}S`);
        if (result.error) {
            console.log(`      Error: ${result.error}`);
        }
    });
    
    // Feature validation summary
    console.log('\n🔍 FEATURE VALIDATION:');
    console.log('─'.repeat(40));
    
    const featureResults = {
        'Original Compilation': results.find(r => r.suite.includes('01-hello-world'))?.code === 0,
        'Tree Structure': results.find(r => r.suite.includes('02-tree-format'))?.code === 0,
        'Multi-file Projects': results.find(r => r.suite.includes('03-multi-file-tree'))?.code === 0,
        'Error Handling': results.find(r => r.suite.includes('09-error-handling'))?.code === 0,
        'Library Compilation': results.find(r => r.suite.includes('10-enhanced-library'))?.code === 0,
        'Package Installation': results.find(r => r.suite.includes('11-session-package'))?.code === 0,
        'Advanced Compilation': results.find(r => r.suite.includes('12-advanced-compilation'))?.code === 0,
        'Conan Integration': results.find(r => r.suite.includes('13-conan-integration'))?.code === 0,
        'Backward Compatibility': results.find(r => r.suite.includes('14-backward-compatibility'))?.code === 0
    };
    
    Object.entries(featureResults).forEach(([feature, passed]) => {
        const status = passed ? '✅' : '❌';
        console.log(`  ${status} ${feature}`);
    });
    
    // Exit with appropriate code
    const overallSuccess = totalFailed === 0;
    const exitCode = overallSuccess ? 0 : 1;
    
    console.log(`\n🏁 Overall result: ${overallSuccess ? '✅ SUCCESS' : '❌ FAILURE'}`);
    
    if (!overallSuccess) {
        console.log('\n⚠️  Some tests failed. Check the output above for details.');
        console.log('   This may be expected if the SDV Runtime container is not running');
        console.log('   or if optional dependencies (like Conan) are not installed.');
    }
    
    process.exit(exitCode);
}

// Handle signals gracefully
process.on('SIGINT', () => {
    console.log('\n⚠️  Test run interrupted by user');
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});

// Start the test run
console.log('⚡ Initializing enhanced C++ compilation test suite...');
runAllTests().catch(err => {
    console.error('Fatal error in test runner:', err);
    process.exit(1);
});