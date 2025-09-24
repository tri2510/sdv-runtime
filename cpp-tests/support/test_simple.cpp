#include <atomic>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <iostream>
#include <thread>

std::atomic<int> test_counter{0};
std::atomic<float> test_value{0.0f};
std::atomic<bool> keep_running{true};

void handle_signal(int) {
    keep_running.store(false);
}

int main() {
    std::signal(SIGINT, handle_signal);
    std::signal(SIGTERM, handle_signal);

    std::cout << "test_simple starting" << std::endl;

    while (keep_running.load()) {
        test_counter.fetch_add(1);
        test_value.store(test_value.load() + 1.5f);

        std::cout << "test_counter=" << test_counter.load()
                  << " test_value=" << test_value.load() << std::endl;

        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    std::cout << "test_simple stopping" << std::endl;
    return 0;
}
