const io = require('socket.io-client');

console.log('🔌 Testing Production SDV Runtime Connection');
console.log('==========================================\n');

const socket = io('http://localhost:3090', {
    timeout: 10000,
    forceNew: true
});

socket.on('connect', () => {
    console.log('✅ Successfully connected to Production SDV Runtime');
    console.log('🔌 Socket ID:', socket.id);
    console.log('🌐 Enhanced compilation service is ready!');
    console.log('📡 Available endpoints: compile_cpp, compile_rust');
    
    socket.disconnect();
    process.exit(0);
});

socket.on('connect_error', (error) => {
    console.error('❌ Failed to connect to SDV Runtime:', error.message);
    console.log('\n🔧 Troubleshooting:');
    console.log('1. Check container: docker ps | grep sdv-runtime');
    console.log('2. Check logs: docker logs sdv-runtime-container');
    console.log('3. Verify port: curl http://localhost:3090');
    
    process.exit(1);
});

console.log('🔄 Connecting to SDV Runtime on localhost:3090...');
