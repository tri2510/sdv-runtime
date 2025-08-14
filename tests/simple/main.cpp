#include <iostream>
#include <string>
#include "config.h"

int main() {
    std::cout << "=== SIMPLE SDV COMPILATION TEST ===" << std::endl;
    
    // Test 1: Basic output
    std::cout << "Hello from Production SDV Runtime!" << std::endl;
    
    // Test 2: String manipulation
    std::string message = "Compilation successful";
    std::cout << "Status: " << message << std::endl;
    
    // Test 3: Configuration access
    std::cout << "Config Version: " << CONFIG_VERSION << std::endl;
    std::cout << "Config Name: " << CONFIG_NAME << std::endl;
    
    // Test 4: Mathematical computation
    int sum = 0;
    for (int i = 1; i <= 1000; i++) {
        sum += i;
    }
    std::cout << "Sum 1-1000: " << sum << std::endl;
    
    std::cout << "=== TEST COMPLETED SUCCESSFULLY ===" << std::endl;
    
    return 0;
}