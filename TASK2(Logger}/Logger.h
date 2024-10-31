#ifndef LOGGER_H
#define LOGGER_H

#include <iostream>
#include <fstream>
#include <string>
#include <mutex>
#include <memory>

class Logger {
public:
    // Get the singleton instance of the Logger
    static Logger& getInstance() {
        static Logger instance;
        return instance;
    }

    // Disable copy constructor and assignment operator
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

    // Log a message to the log file
    void log(const std::string& message) {
        std::lock_guard<std::mutex> lock(mutex_);  // Lock the mutex for thread-safe logging
        logFile_ << message << std::endl;
    }

private:
    std::ofstream logFile_;  // Output file stream for logging
    std::mutex mutex_;       // Mutex to protect file writing

    // Private constructor to enforce singleton
    Logger() {
        logFile_.open("log.txt", std::ios::out | std::ios::app);
        if (!logFile_.is_open()) {
            std::cerr << "Failed to open log file!" << std::endl;
        }
    }

    // Destructor closes the file
    ~Logger() {
        if (logFile_.is_open()) {
            logFile_.close();
        }
    }
};

#endif
