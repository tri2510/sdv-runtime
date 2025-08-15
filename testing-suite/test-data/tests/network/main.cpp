#include <iostream>
#include <string>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>

int main() {
    std::cout << "=== NETWORK COMMUNICATION TEST ===" << std::endl;
    
    // Test 1: Create socket
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        std::cout << "ERROR: Failed to create socket" << std::endl;
        return 1;
    }
    std::cout << "✅ Socket created successfully" << std::endl;
    
    // Test 2: Setup server address
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8899);
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    
    std::cout << "📍 Connecting to localhost:8899..." << std::endl;
    
    // Test 3: Connect to test server
    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cout << "ERROR: Connection failed" << std::endl;
        close(sock);
        return 2;
    }
    std::cout << "✅ Connected to test server" << std::endl;
    
    // Test 4: Send data
    const char* message = "Hello from compiled executable!";
    if (send(sock, message, strlen(message), 0) < 0) {
        std::cout << "ERROR: Failed to send data" << std::endl;
        close(sock);
        return 3;
    }
    std::cout << "📤 Sent message: " << message << std::endl;
    
    // Test 5: Receive response
    char buffer[1024] = {0};
    int bytes_received = recv(sock, buffer, sizeof(buffer), 0);
    if (bytes_received < 0) {
        std::cout << "ERROR: Failed to receive data" << std::endl;
        close(sock);
        return 4;
    }
    std::cout << "📨 Received response: " << buffer << std::endl;
    
    // Test 6: Cleanup
    close(sock);
    std::cout << "🔌 Connection closed" << std::endl;
    std::cout << "✅ Network communication test completed successfully!" << std::endl;
    
    return 0;
}