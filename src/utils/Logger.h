/**
 * Système de logging unifié
 */

#pragma once

#include <string>
#include <memory>
#include <mutex>
#include <fstream>

namespace rtpa::utils {

enum class LogLevel {
    Debug = 0,
    Info = 1,
    Warn = 2,
    Error = 3
};

class Logger {
public:
    static void initialize(const std::string& logPath = "./logs/rtpa.log", LogLevel level = LogLevel::Info);
    static void shutdown();
    
    static void debug(const std::string& message);
    static void info(const std::string& message);
    static void warn(const std::string& message);
    static void error(const std::string& message);
    
private:
    static std::unique_ptr<Logger> instance_;
    static std::mutex mutex_;
    
    std::ofstream logFile_;
    LogLevel currentLevel_;
    
    void log(LogLevel level, const std::string& message);
    std::string getLevelString(LogLevel level);
    std::string getCurrentTimestamp();
};

} // namespace rtpa::utils