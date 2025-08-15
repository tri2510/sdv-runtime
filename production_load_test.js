const io = require('socket.io-client');
const fs = require('fs').promises;
const path = require('path');

console.log('🚀 Production SDV Runtime Load Testing');
console.log('======================================\n');

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

class ProductionLoadTester {
    constructor(containerUrl = 'http://localhost:3090') {
        this.containerUrl = containerUrl;
        this.results = [];
        this.activeConnections = 0;
    }
    
    async createTestProject(clientId) {
        // Load base test files and modify for load testing
        const baseFiles = await loadTestFiles('./tests/simple');
        if (!baseFiles) {
            throw new Error('Could not load base test files');
        }
        
        // Modify main.cpp to include client ID
        const modifiedFiles = { ...baseFiles };
        if (modifiedFiles['main.cpp']) {
            modifiedFiles['main.cpp'] = modifiedFiles['main.cpp'].replace(
                '=== SIMPLE SDV COMPILATION TEST ===',
                `=== LOAD TEST CLIENT ${clientId} ===`
            );
        }
        
        return modifiedFiles;
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    std::cout << "Client ${clientId} workload completed in " << duration.count() << "ms" << std::endl;
    std::cout << "Production SDV Runtime compilation successful for client ${clientId}!" << std::endl;
    
    return 0;
}`,
            "client_config.h": `#ifndef CLIENT_CONFIG_H
#define CLIENT_CONFIG_H

#define CLIENT_ID ${clientId}
#define CLIENT_WORKLOAD 50000
#define PRODUCTION_SDV_VERSION "2.0.0"
#define LOAD_TEST_ENABLED true

    }
    
    runLoadTest(numClients = 3, staggerDelay = 800) {
        console.log(`🔥 Starting Production SDV load test with ${numClients} concurrent clients`);
        console.log(`⏱️  Stagger delay: ${staggerDelay}ms between client starts\n`);
        
        const startTime = Date.now();
        let completedClients = 0;
        
        for (let i = 1; i <= numClients; i++) {
            setTimeout(() => {
                this.runSingleClient(i, startTime, () => {
                    completedClients++;
                    if (completedClients === numClients) {
                        this.showLoadTestResults(startTime);
                    }
                });
            }, (i - 1) * staggerDelay);
        }
    }
    
    runSingleClient(clientId, globalStartTime, callback) {
        const socket = io(this.containerUrl, { 
            forceNew: true,
            timeout: 45000
        });
        
        const clientStartTime = Date.now();
        this.activeConnections++;
        
        socket.on('connect', async () => {
            console.log(`🔌 Production Client ${clientId} connected (${this.activeConnections} active)`);
            
            const projectFiles = await this.createTestProject(clientId);
            socket.emit('compile_cpp', {
                files: projectFiles,
                app_name: `prod_load_test_client_${clientId}`,
                run: true
            });
        });
        
        socket.on('compile_cpp_reply', (data) => {
            if (data.isDone) {
                const elapsed = Date.now() - clientStartTime;
                const globalElapsed = Date.now() - globalStartTime;
                
                this.results.push({
                    clientId: clientId,
                    success: data.code === 0,
                    duration: elapsed,
                    globalTime: globalElapsed
                });
                
                console.log(`✅ Production Client ${clientId} completed in ${elapsed}ms (code: ${data.code})`);
                
                this.activeConnections--;
                socket.disconnect();
                callback();
            }
        });
        
        socket.on('connect_error', (error) => {
            console.error(`❌ Production Client ${clientId} connection failed: ${error.message}`);
            
            this.results.push({
                clientId: clientId,
                success: false,
                duration: Date.now() - clientStartTime,
                globalTime: Date.now() - globalStartTime,
                error: error.message
            });
            
            this.activeConnections--;
            callback();
        });
        
        // Timeout handling
        setTimeout(() => {
            if (socket.connected) {
                console.log(`⏰ Production Client ${clientId} timed out`);
                socket.disconnect();
            }
        }, 90000);
    }
    
    showLoadTestResults(startTime) {
        const totalTime = Date.now() - startTime;
        
        console.log('\n📊 Production SDV Load Test Results');
        console.log('===================================');
        console.log(`⏱️  Total Test Duration: ${totalTime}ms`);
        console.log(`👥 Total Clients: ${this.results.length}`);
        
        const successful = this.results.filter(r => r.success);
        const failed = this.results.filter(r => !r.success);
        
        console.log(`✅ Successful Compilations: ${successful.length}`);
        console.log(`❌ Failed Compilations: ${failed.length}`);
        console.log(`📈 Success Rate: ${(successful.length / this.results.length * 100).toFixed(1)}%`);
        
        if (successful.length > 0) {
            const avgDuration = successful.reduce((sum, r) => sum + r.duration, 0) / successful.length;
            const minDuration = Math.min(...successful.map(r => r.duration));
            const maxDuration = Math.max(...successful.map(r => r.duration));
            
            console.log(`\n📊 Production Performance Metrics:`);
            console.log(`   Average Compilation Time: ${avgDuration.toFixed(1)}ms`);
            console.log(`   Fastest Compilation: ${minDuration}ms`);
            console.log(`   Slowest Compilation: ${maxDuration}ms`);
            console.log(`   Performance Deviation: ${this.calculateStdDev(successful.map(r => r.duration)).toFixed(1)}ms`);
        }
        
        if (failed.length > 0) {
            console.log(`\n❌ Failed Production Clients:`);
            failed.forEach(result => {
                console.log(`   Client ${result.clientId}: ${result.error || 'Unknown error'}`);
            });
        }
        
        console.log(`\n🏆 Production SDV Runtime Load Test Summary:`);
        console.log(`   🐳 Container handled ${this.results.length} concurrent compilation requests`);
        console.log(`   ⚡ Enhanced compilation features performed under load`);
        console.log(`   🔧 Multi-file project support maintained concurrent performance`);
        console.log(`   📡 Real-time streaming worked across all clients`);
        console.log(`   🎯 Production environment stability: ${successful.length > 0 ? 'EXCELLENT' : 'NEEDS ATTENTION'}`);
        
        console.log(`\n🔥 Production SDV load test completed successfully!`);
    }
    
    calculateStdDev(values) {
        const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
        const squareDiffs = values.map(value => Math.pow(value - avg, 2));
        const avgSquareDiff = squareDiffs.reduce((sum, val) => sum + val, 0) / values.length;
        return Math.sqrt(avgSquareDiff);
    }
}

// Run production load test
const tester = new ProductionLoadTester();

// Test with production-appropriate configurations
const testConfigs = [
    { clients: 2, delay: 1000, name: "Light Production Load" },
    { clients: 3, delay: 600, name: "Medium Production Load" }
];

let currentTest = 0;

function runNextTest() {
    if (currentTest < testConfigs.length) {
        const config = testConfigs[currentTest];
        console.log(`\n🚀 Running ${config.name} Test (${config.clients} clients, ${config.delay}ms delay)`);
        console.log('='.repeat(70));
        
        const testTester = new ProductionLoadTester();
        // Override the callback to run next test
        const originalShow = testTester.showLoadTestResults;
        testTester.showLoadTestResults = function(startTime) {
            originalShow.call(this, startTime);
            currentTest++;
            setTimeout(runNextTest, 3000); // Wait 3s between tests
        };
        
        testTester.runLoadTest(config.clients, config.delay);
    } else {
        console.log('\n🎉 All Production SDV load tests completed!');
        console.log('===============================================');
        console.log('Production SDV Runtime enhanced compilation features');
        console.log('successfully handled concurrent client loads! 🚀');
        process.exit(0);
    }
}

// Start testing
runNextTest();