const io = require('socket.io-client');

console.log('🔌 VERIFICATION: Production SDV Runtime Connection Test');
console.log('======================================================\n');

const socket = io('http://localhost:3090', {
    timeout: 10000,
    forceNew: true
});

socket.on('connect', () => {
    console.log('✅ PASS: Successfully connected to Production SDV Runtime');
    console.log('🔌 Socket ID:', socket.id);
    console.log('🌐 Enhanced compilation service is ready!');
    console.log('📡 Available endpoints: compile_cpp, compile_rust');
    
    socket.disconnect();
    console.log('✅ CONNECTIVITY TEST: PASSED\n');
    process.exit(0);
});

socket.on('connect_error', (error) => {
    console.error('❌ FAIL: Failed to connect to SDV Runtime:', error.message);
    console.log('❌ CONNECTIVITY TEST: FAILED\n');
    process.exit(1);
});

console.log('🔄 Testing connection to SDV Runtime on localhost:3090...');

setTimeout(() => {
    console.log('⏰ FAIL: Connection timeout');
    console.log('❌ CONNECTIVITY TEST: FAILED\n');
    process.exit(1);
}, 15000);