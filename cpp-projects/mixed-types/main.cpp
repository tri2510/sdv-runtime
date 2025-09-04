#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <iomanip>
#include <cmath>

// Comprehensive atomic type testing for monitoring robustness
std::atomic<int8_t> tiny_value{100};
std::atomic<int16_t> small_value{30000};
std::atomic<int32_t> medium_value{2000000};
std::atomic<int64_t> large_value{9000000000LL};

std::atomic<uint8_t> unsigned_tiny{200};
std::atomic<uint16_t> unsigned_small{50000};
std::atomic<uint32_t> unsigned_medium{3000000000U};

std::atomic<float> float_precision{3.14159f};
std::atomic<double> double_precision{2.718281828459045};

std::atomic<bool> flag_alpha{true};
std::atomic<bool> flag_beta{false};
std::atomic<bool> flag_gamma{true};

// Char atomics (less common but valid)
std::atomic<char> char_value{'A'};
std::atomic<signed char> signed_char_value{-50};
std::atomic<unsigned char> unsigned_char_value{250};

// Size-specific types
std::atomic<size_t> memory_size{1024UL};
std::atomic<intptr_t> pointer_sized{0x7fff0000};

void printBanner() {
    std::cout << "╔═══════════════════════════════════════════════╗" << std::endl;
    std::cout << "║        MIXED ATOMIC TYPES TESTING            ║" << std::endl;
    std::cout << "║      Comprehensive Type Monitoring Test      ║" << std::endl;
    std::cout << "╚═══════════════════════════════════════════════╝" << std::endl;
}

void updateVariables(int cycle) {
    // Update integer types with different patterns
    tiny_value = 100 + (cycle % 50);
    small_value = 30000 + cycle * 100;
    medium_value = 2000000 + cycle * 1000;
    large_value = 9000000000LL + cycle * 10000;
    
    // Update unsigned types
    unsigned_tiny = 200 + (cycle % 55);
    unsigned_small = 50000 + cycle * 200;
    unsigned_medium = 3000000000U + cycle * 50000;
    
    // Update floating point with mathematical functions
    float_precision = 3.14159f * std::sin(cycle * 0.1f);
    double_precision = 2.718281828459045 + std::cos(cycle * 0.05) * 0.5;
    
    // Update boolean flags with different patterns
    flag_alpha = (cycle % 7 != 0);
    flag_beta = (cycle % 11 == 0);
    flag_gamma = (cycle % 3 == 0);
    
    // Update character types
    char_value = 'A' + (cycle % 26); // A-Z cycling
    signed_char_value = -50 + (cycle % 100); // -50 to +49
    unsigned_char_value = 200 + (cycle % 56); // 200-255
    
    // Update size types
    memory_size = 1024UL * (1 + cycle / 10);
    pointer_sized = 0x7fff0000 + cycle * 0x1000;
}

void printStatus(int cycle) {
    std::cout << "\n--- Cycle " << std::setw(3) << cycle << " ---" << std::endl;
    
    // Integer types
    std::cout << "📊 Int8: " << static_cast<int>(tiny_value.load()) 
              << " | Int16: " << small_value.load()
              << " | Int32: " << medium_value.load() 
              << " | Int64: " << large_value.load() << std::endl;
              
    // Unsigned types
    std::cout << "📊 UInt8: " << static_cast<unsigned>(unsigned_tiny.load()) 
              << " | UInt16: " << unsigned_small.load()
              << " | UInt32: " << unsigned_medium.load() << std::endl;
              
    // Floating point
    std::cout << std::fixed << std::setprecision(4)
              << "📊 Float: " << float_precision.load() 
              << " | Double: " << double_precision.load() << std::endl;
              
    // Booleans
    std::cout << "📊 Alpha: " << (flag_alpha.load() ? "T" : "F")
              << " | Beta: " << (flag_beta.load() ? "T" : "F") 
              << " | Gamma: " << (flag_gamma.load() ? "T" : "F") << std::endl;
              
    // Character types
    std::cout << "📊 Char: '" << char_value.load() << "'"
              << " | SChar: " << static_cast<int>(signed_char_value.load())
              << " | UChar: " << static_cast<unsigned>(unsigned_char_value.load()) << std::endl;
              
    // Size types
    std::cout << "📊 Size: " << memory_size.load() 
              << " | Ptr: 0x" << std::hex << pointer_sized.load() << std::dec << std::endl;
}

int main() {
    printBanner();
    
    std::cout << "🔧 Testing comprehensive atomic type monitoring..." << std::endl;
    std::cout << "📊 Testing 16 different atomic variable types:" << std::endl;
    std::cout << "    • Integer types: int8_t, int16_t, int32_t, int64_t" << std::endl;
    std::cout << "    • Unsigned types: uint8_t, uint16_t, uint32_t" << std::endl;
    std::cout << "    • Floating types: float, double" << std::endl;
    std::cout << "    • Boolean types: bool (3 instances)" << std::endl;
    std::cout << "    • Character types: char, signed char, unsigned char" << std::endl;
    std::cout << "    • System types: size_t, intptr_t" << std::endl;
    std::cout << "⏱️  Running for 30 seconds with 300ms intervals\n" << std::endl;
    
    for (int cycle = 0; cycle < 100; ++cycle) {
        updateVariables(cycle);
        
        // Print detailed status every 15 cycles to avoid spam
        if (cycle % 15 == 0) {
            printStatus(cycle);
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
    }
    
    std::cout << "\n✅ Mixed atomic types test completed!" << std::endl;
    printStatus(99); // Final status
    
    return 0;
}