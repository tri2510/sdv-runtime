#include <iostream>
#include <thread>
#include <chrono>
#include "VehicleController.h"
#include "SensorManager.h"

int main() {
    std::cout << "Starting CMake Vehicle Systems Monitor..." << std::endl;
    std::cout << "This project demonstrates structured C++ with atomic variables" << std::endl;
    
    VehicleController controller;
    SensorManager sensors;
    
    for (int cycle = 0; cycle < 40; ++cycle) {
        std::cout << "\n--- Cycle " << cycle + 1 << " ---" << std::endl;
        
        // Update both systems
        controller.updateControlSystems();
        sensors.updateSensors();
        
        // Display status every 5 cycles
        if ((cycle + 1) % 5 == 0) {
            controller.displayStatus();
            std::cout << std::endl;
            sensors.displaySensorData();
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(750));
    }
    
    std::cout << "\nCMake Vehicle Systems Monitor completed." << std::endl;
    return 0;
}