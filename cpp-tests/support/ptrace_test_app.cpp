#include <atomic>
#include <chrono>
#include <csignal>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <thread>

volatile int counter = 0;
volatile double sensor_value = 0.0;
std::atomic<bool> keep_running{true};

void handle_signal(int) {
    keep_running.store(false);
}

int main() {
    std::signal(SIGINT, handle_signal);
    std::signal(SIGTERM, handle_signal);

    std::cout << "ptrace test app starting" << std::endl;

    int tick = 0;
    while (keep_running.load()) {
        counter += 1;
        sensor_value = std::sin(static_cast<double>(tick) * 0.25) * 42.0;

        std::cout << "counter=" << counter << " sensor_value=" << sensor_value << std::endl;

        ++tick;
        std::this_thread::sleep_for(std::chrono::milliseconds(150));
    }

    std::cout << "ptrace test app stopping" << std::endl;
    return 0;
}
