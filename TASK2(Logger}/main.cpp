#include "Logger.h"
#include <thread>
#include <vector>
#include <iterator>
#include <chrono>

// Function that each thread will run to log messages
void logMessages(int thread_id) {
    for (int i = 0; i < 5; ++i) {
        Logger::getInstance().log("Thread " + std::to_string(thread_id) + " - Message " + std::to_string(i));
        std::this_thread::sleep_for(std::chrono::milliseconds(10));  // Optional delay for readability
    }
}

int main() {
    const int numThreads = 10;
    std::vector<std::thread> threads;

    // Create multiple threads to simulate simultaneous logging
    for (int i = 0; i < numThreads; ++i) {
        threads.emplace_back(logMessages, i);
    }

    // Wait for all threads to finish
    for (auto& t : threads) {
        t.join();
    }

    std::cout << "Logging complete. Check log.txt for output." << std::endl;
    return 0;
}
