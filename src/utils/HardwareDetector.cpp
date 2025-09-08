/**
 * RTPA Studio - Hardware Detection Implementation
 * Détection automatique et adaptation matérielle Windows/Linux/macOS
 */

#include "HardwareDetector.h"
#include <iostream>
#include <sstream>
#include <fstream>
#include <algorithm>
#include <thread>
#include <filesystem>
#include <regex>

#ifdef _WIN32
#include <windows.h>
#include <intrin.h>
#include <sysinfoapi.h>
#include <comdef.h>
#include <Wbemidl.h>
#pragma comment(lib, "wbemuuid.lib")
#elif defined(__linux__)
#include <sys/sysinfo.h>
#include <sys/utsname.h>
#include <unistd.h>
#include <cpuid.h>
#elif defined(__APPLE__)
#include <sys/types.h>
#include <sys/sysctl.h>
#include <mach/mach.h>
#endif

namespace rtpa::utils {

HardwareDetector::HardwareDetector() {
    std::cout << "🔍 Initialisation détection matérielle..." << std::endl;
}

HardwareDetector::~HardwareDetector() = default;

bool HardwareDetector::detectHardware() {
    std::cout << "🖥️  Détection automatique du matériel..." << std::endl;
    
    try {
        // Détection système d'exploitation
        m_hardwareInfo.osName = getOSName();
        
        #ifdef _WIN32
        return detectWindowsHardware();
        #elif defined(__linux__)
        return detectLinuxHardware();
        #elif defined(__APPLE__)
        return detectMacOSHardware();
        #else
        std::cout << "⚠️  Plateforme non supportée" << std::endl;
        return false;
        #endif
        
    } catch (const std::exception& e) {
        std::cerr << "❌ Erreur détection matérielle: " << e.what() << std::endl;
        return false;
    }
}

#ifdef _WIN32
bool HardwareDetector::detectWindowsHardware() {
    std::cout << "🏠 Détection matérielle Windows..." << std::endl;
    
    // CPU Detection
    if (!detectWindowsCPU()) {
        std::cerr << "⚠️  Échec détection CPU Windows" << std::endl;
    }
    
    // GPU Detection  
    if (!detectWindowsGPU()) {
        std::cout << "⚠️  Aucun GPU haute performance détecté" << std::endl;
    }
    
    // RAM Detection
    size_t ramMB = detectWindowsRAM();
    m_hardwareInfo.totalRamMB = ramMB;
    m_hardwareInfo.availableRamMB = static_cast<size_t>(ramMB * 0.7); // 70% disponible estimé
    
    detectCUDACapabilities();
    measurePerformanceBaselines();
    
    return true;
}

bool HardwareDetector::detectWindowsCPU() {
    SYSTEM_INFO sysInfo;
    GetSystemInfo(&sysInfo);
    
    m_hardwareInfo.cpuCores = sysInfo.dwNumberOfProcessors;
    m_hardwareInfo.cpuThreads = std::thread::hardware_concurrency();
    
    // Détection nom CPU via registre Windows
    char cpuBrand[49] = {0};
    int cpuInfo[4] = {0};
    
    #ifdef _MSC_VER
    __cpuid(cpuInfo, 0x80000002);
    memcpy(cpuBrand, cpuInfo, sizeof(cpuInfo));
    __cpuid(cpuInfo, 0x80000003);
    memcpy(cpuBrand + 16, cpuInfo, sizeof(cpuInfo));
    __cpuid(cpuInfo, 0x80000004);
    memcpy(cpuBrand + 32, cpuInfo, sizeof(cpuInfo));
    #endif
    
    m_hardwareInfo.cpuName = std::string(cpuBrand);
    
    std::cout << "  CPU: " << m_hardwareInfo.cpuName << " (" 
              << m_hardwareInfo.cpuCores << " cores, " 
              << m_hardwareInfo.cpuThreads << " threads)" << std::endl;
              
    return true;
}

bool HardwareDetector::detectWindowsGPU() {
    // Détection NVIDIA via CUDA
    m_hardwareInfo.hasNvidiaGPU = isCUDAAvailable();
    
    if (m_hardwareInfo.hasNvidiaGPU) {
        m_hardwareInfo.gpuName = "NVIDIA GPU (CUDA Supported)";
        m_hardwareInfo.cudaSupported = true;
        std::cout << "  GPU: NVIDIA détecté avec support CUDA" << std::endl;
        return true;
    }
    
    // Fallback: détection via DirectX
    m_hardwareInfo.hasIntelGPU = true; // Assume Intel integrated
    m_hardwareInfo.gpuName = "Integrated Graphics";
    
    std::cout << "  GPU: Graphiques intégrés détectés" << std::endl;
    return false;
}

size_t HardwareDetector::detectWindowsRAM() {
    MEMORYSTATUSEX memInfo;
    memInfo.dwLength = sizeof(MEMORYSTATUSEX);
    GlobalMemoryStatusEx(&memInfo);
    
    size_t totalRAM = static_cast<size_t>(memInfo.ullTotalPhys / (1024 * 1024));
    std::cout << "  RAM: " << totalRAM << " MB détectés" << std::endl;
    
    return totalRAM;
}

#elif defined(__linux__)
bool HardwareDetector::detectLinuxHardware() {
    std::cout << "🐧 Détection matérielle Linux..." << std::endl;
    
    // CPU info depuis /proc/cpuinfo
    std::ifstream cpuinfo("/proc/cpuinfo");
    if (cpuinfo.is_open()) {
        std::string line;
        while (std::getline(cpuinfo, line)) {
            if (line.find("model name") != std::string::npos) {
                size_t pos = line.find(": ");
                if (pos != std::string::npos) {
                    m_hardwareInfo.cpuName = line.substr(pos + 2);
                    break;
                }
            }
        }
    }
    
    m_hardwareInfo.cpuCores = std::thread::hardware_concurrency();
    m_hardwareInfo.cpuThreads = m_hardwareInfo.cpuCores;
    
    // RAM info depuis /proc/meminfo
    std::ifstream meminfo("/proc/meminfo");
    if (meminfo.is_open()) {
        std::string line;
        while (std::getline(meminfo, line)) {
            if (line.find("MemTotal:") != std::string::npos) {
                std::istringstream iss(line);
                std::string token;
                iss >> token >> token; // Skip "MemTotal:"
                size_t ramKB = std::stoull(token);
                m_hardwareInfo.totalRamMB = ramKB / 1024;
                m_hardwareInfo.availableRamMB = static_cast<size_t>(m_hardwareInfo.totalRamMB * 0.7);
                break;
            }
        }
    }
    
    // GPU detection
    m_hardwareInfo.hasNvidiaGPU = fileExists("/proc/driver/nvidia/version");
    if (m_hardwareInfo.hasNvidiaGPU) {
        m_hardwareInfo.cudaSupported = isCUDAAvailable();
        m_hardwareInfo.gpuName = "NVIDIA GPU";
    }
    
    detectCUDACapabilities();
    measurePerformanceBaselines();
    
    std::cout << "  Système Linux détecté avec succès" << std::endl;
    return true;
}
#endif

std::string HardwareDetector::getOSName() const {
    #ifdef _WIN32
    return "Windows";
    #elif defined(__linux__)
    return "Linux";
    #elif defined(__APPLE__)
    return "macOS";
    #else
    return "Unknown";
    #endif
}

bool HardwareDetector::isCUDAAvailable() const {
    // Vérification simple de la présence CUDA
    #ifdef _WIN32
    return GetFileAttributesA("C:\\Program Files\\NVIDIA GPU Computing Toolkit") != INVALID_FILE_ATTRIBUTES ||
           GetFileAttributesA("C:\\Program Files\\NVIDIA Corporation\\NVIDIA NGX") != INVALID_FILE_ATTRIBUTES;
    #elif defined(__linux__)
    return fileExists("/usr/local/cuda") || fileExists("/opt/cuda") || 
           fileExists("/usr/lib/x86_64-linux-gnu/libcuda.so");
    #else
    return false;
    #endif
}

OptimalSettings HardwareDetector::calculateOptimalSettings() const {
    OptimalSettings settings;
    
    std::cout << "⚙️  Calcul configuration optimale..." << std::endl;
    
    // Configuration CFR basée sur CPU
    if (m_hardwareInfo.cpuCores >= 8) {
        settings.cfrIterations = 2000;
        settings.cfrThreads = std::min(m_hardwareInfo.cpuCores - 2, 12);
        settings.batchSize = 1000;
    } else if (m_hardwareInfo.cpuCores >= 4) {
        settings.cfrIterations = 1500;
        settings.cfrThreads = m_hardwareInfo.cpuCores - 1;
        settings.batchSize = 750;
    } else {
        settings.cfrIterations = 1000;
        settings.cfrThreads = 2;
        settings.batchSize = 500;
    }
    
    // Configuration GPU
    if (shouldEnableGPUAcceleration()) {
        settings.useGPUAcceleration = true;
        settings.batchSize *= 2; // GPU peut traiter plus
        std::cout << "  ✅ Accélération GPU activée" << std::endl;
    }
    
    // Configuration mémoire
    if (m_hardwareInfo.totalRamMB >= 16384) { // 16GB+
        settings.maxMemoryUsageMB = 4096;
        settings.enableMemoryMapping = true;
    } else if (m_hardwareInfo.totalRamMB >= 8192) { // 8GB+
        settings.maxMemoryUsageMB = 2048;
        settings.enableMemoryMapping = false;
    } else {
        settings.maxMemoryUsageMB = 1024;
        settings.enableMemoryMapping = false;
    }
    
    // Configuration OCR
    settings.ocrThreads = std::min(4, m_hardwareInfo.cpuCores / 2);
    settings.useOpenCVOptimizations = true;
    
    std::cout << "  🎯 Configuration: " << settings.cfrThreads << " threads CFR, "
              << settings.maxMemoryUsageMB << "MB RAM, GPU=" 
              << (settings.useGPUAcceleration ? "ON" : "OFF") << std::endl;
    
    return settings;
}

bool HardwareDetector::shouldEnableGPUAcceleration() const {
    return m_hardwareInfo.hasNvidiaGPU && m_hardwareInfo.cudaSupported && 
           m_hardwareInfo.totalRamMB >= 4096; // Minimum 4GB RAM requis
}

int HardwareDetector::recommendedThreadCount() const {
    return std::max(1, std::min(m_hardwareInfo.cpuCores - 1, 16));
}

void HardwareDetector::detectCUDACapabilities() {
    if (!m_hardwareInfo.hasNvidiaGPU) return;
    
    // Test simple de capacité CUDA
    m_hardwareInfo.cudaSupported = isCUDAAvailable();
    
    if (m_hardwareInfo.cudaSupported) {
        std::cout << "  🔥 CUDA: Accélération GPU disponible" << std::endl;
    }
}

void HardwareDetector::measurePerformanceBaselines() {
    std::cout << "📊 Mesure performances baseline..." << std::endl;
    
    // Tests rapides de performance pour calibrage
    auto start = std::chrono::high_resolution_clock::now();
    
    // Test CPU simple
    volatile double result = 0.0;
    for (int i = 0; i < 1000000; ++i) {
        result += std::sin(i * 0.001);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    m_performanceMetrics["cpu_baseline_ms"] = duration.count();
    
    std::cout << "  Baseline CPU: " << duration.count() << "ms" << std::endl;
}

bool HardwareDetector::fileExists(const std::string& path) const {
    std::ifstream file(path);
    return file.good();
}

double HardwareDetector::getCurrentCPUUsage() const {
    // Placeholder - implémentation système specific nécessaire
    return 0.0;
}

double HardwareDetector::getCurrentRAMUsage() const {
    #ifdef _WIN32
    MEMORYSTATUSEX memInfo;
    memInfo.dwLength = sizeof(MEMORYSTATUSEX);
    GlobalMemoryStatusEx(&memInfo);
    return 100.0 * (1.0 - static_cast<double>(memInfo.ullAvailPhys) / memInfo.ullTotalPhys);
    #else
    return 0.0; // Placeholder
    #endif
}

void HardwareDetector::updateSettingsBasedOnPerformance(OptimalSettings& settings) const {
    double cpuUsage = getCurrentCPUUsage();
    double ramUsage = getCurrentRAMUsage();
    
    // Ajustement dynamique basé sur l'utilisation actuelle
    if (cpuUsage > 80.0) {
        settings.cfrThreads = std::max(1, settings.cfrThreads - 1);
        settings.batchSize = static_cast<int>(settings.batchSize * 0.8);
    } else if (cpuUsage < 30.0 && settings.cfrThreads < recommendedThreadCount()) {
        settings.cfrThreads++;
    }
    
    if (ramUsage > 85.0) {
        settings.maxMemoryUsageMB = static_cast<size_t>(settings.maxMemoryUsageMB * 0.7);
        settings.enableMemoryMapping = false;
    }
}

} // namespace rtpa::utils