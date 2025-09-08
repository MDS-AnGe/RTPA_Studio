/**
 * RTPA Studio - Hardware Detection & Auto Configuration
 * Détection automatique du matériel et adaptation des paramètres
 * Compatible Windows, Linux, macOS
 */

#pragma once

#include <string>
#include <vector>
#include <memory>
#include <map>

namespace rtpa::utils {

struct HardwareInfo {
    // CPU Info
    std::string cpuName;
    int cpuCores = 0;
    int cpuThreads = 0;
    double cpuFrequencyMHz = 0.0;
    
    // GPU Info
    bool hasNvidiaGPU = false;
    bool hasAMDGPU = false;
    bool hasIntelGPU = false;
    std::string gpuName;
    size_t gpuMemoryMB = 0;
    bool cudaSupported = false;
    
    // RAM Info
    size_t totalRamMB = 0;
    size_t availableRamMB = 0;
    
    // Système
    std::string osName;
    std::string osVersion;
    bool is64Bit = true;
};

struct OptimalSettings {
    // CFR Performance
    int cfrIterations = 1000;
    int cfrThreads = 4;
    bool useGPUAcceleration = false;
    int batchSize = 500;
    
    // OCR Settings
    int ocrThreads = 2;
    double ocrScaleFactor = 1.0;
    bool useOpenCVOptimizations = true;
    
    // Memory Management
    size_t maxMemoryUsageMB = 1024;
    bool enableMemoryMapping = false;
    
    // Graphics
    bool enableVSync = true;
    int targetFPS = 60;
    bool useHardwareAcceleration = true;
};

class HardwareDetector {
public:
    HardwareDetector();
    ~HardwareDetector();
    
    // Détection automatique
    bool detectHardware();
    const HardwareInfo& getHardwareInfo() const { return m_hardwareInfo; }
    
    // Configuration optimale
    OptimalSettings calculateOptimalSettings() const;
    void applyOptimalSettings(OptimalSettings& settings) const;
    
    // Windows specific
    bool detectWindowsGPU();
    bool detectWindowsCPU();
    size_t detectWindowsRAM();
    
    // Cross-platform
    std::string getOSName() const;
    bool isCUDAAvailable() const;
    bool isOpenCLAvailable() const;
    
    // Monitoring
    double getCurrentCPUUsage() const;
    double getCurrentRAMUsage() const;
    double getCurrentGPUUsage() const;
    
    // Configuration dynamique
    void updateSettingsBasedOnPerformance(OptimalSettings& settings) const;
    bool shouldEnableGPUAcceleration() const;
    int recommendedThreadCount() const;
    
private:
    HardwareInfo m_hardwareInfo;
    mutable std::map<std::string, double> m_performanceMetrics;
    
    // Platform specific detection
    #ifdef _WIN32
    bool detectWindowsHardware();
    #elif defined(__linux__)
    bool detectLinuxHardware();
    #elif defined(__APPLE__)
    bool detectMacOSHardware();
    #endif
    
    void detectCUDACapabilities();
    void detectOpenCLCapabilities();
    void measurePerformanceBaselines();
    
    // Helper methods
    std::vector<std::string> runCommand(const std::string& command) const;
    bool fileExists(const std::string& path) const;
    std::string readFileContent(const std::string& path) const;
};

} // namespace rtpa::utils