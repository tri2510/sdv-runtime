#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include "communication.h"

int main() {
    std::cout << "=== EXECUTABLE COMMUNICATION TEST ===" << std::endl;
    
    // Test 1: Standard output with special characters
    std::cout << "MESSAGE:Hello from compiled executable!" << std::endl;
    std::cout << "STATUS:Executable started successfully" << std::endl;
    std::cout << "SPECIAL_CHARS:@#$%^&*()" << std::endl;
    
    // Test 2: Multi-line output
    std::cout << "MULTI_LINE_START:" << std::endl;
    std::cout << "Line 1: Communication test" << std::endl;
    std::cout << "Line 2: File operations" << std::endl;
    std::cout << "Line 3: Exit code testing" << std::endl;
    std::cout << "MULTI_LINE_END:" << std::endl;
    
    // Test 3: File communication
    std::string filename = "/tmp/executable_output.txt";
    std::ofstream outFile(filename);
    if (outFile.is_open()) {
        outFile << "File communication test successful" << std::endl;
        outFile << "Timestamp: " << getCurrentTimestamp() << std::endl;
        outFile << "Version: " << COMM_VERSION << std::endl;
        outFile.close();
        std::cout << "FILE_CREATED:" << filename << std::endl;
    } else {
        std::cout << "FILE_ERROR:Could not create output file" << std::endl;
    }
    
    // Test 4: Performance measurement
    auto start = std::chrono::high_resolution_clock::now();
    
    // Some work to measure
    long sum = 0;
    for (int i = 0; i < 1000; i++) {
        sum += i * i;
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    std::cout << "PERFORMANCE:Work completed in " << duration.count() << "ms" << std::endl;
    std::cout << "RESULT:Sum of squares: " << sum << std::endl;
    
    // Test 5: Configuration access
    std::cout << "CONFIG:Version " << COMM_VERSION << std::endl;
    std::cout << "CONFIG:Buffer size " << BUFFER_SIZE << std::endl;
    
    std::cout << "=== COMMUNICATION TEST COMPLETED ===" << std::endl;
    
    // Return custom exit code for testing
    return 42;
}