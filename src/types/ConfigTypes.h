/**
 * Types de configuration pour RTPA Studio
 * Structures centralisées pour tous les paramètres
 */

#pragma once

#include <string>
#include <vector>
#include <unordered_map>
#include <cstdint>

namespace rtpa::types {

// Configuration CFR Engine
struct CfrConfig {
    uint32_t maxIterations = 10000;
    double convergenceThreshold = 0.01;
    uint32_t numThreads = 8;
    bool useGpuAcceleration = true;
    uint32_t batchSize = 1000;
    double explorationRate = 0.1;
    double discountFactor = 0.95;
    
    // Persistence
    std::string modelSavePath = "./models/cfr_model.dat";
    bool autoSaveModel = true;
    uint32_t autoSaveInterval = 1000; // iterations
};

// Configuration OCR
struct OCRConfig {
    std::string tesseractLanguage = "eng";
    int ocrEngineMode = 3;
    int pageSegmentationMode = 8;
    
    bool enableCache = true;
    size_t maxCacheSize = 1000;
    
    bool enableParallel = true;
    int numThreads = 4;
    
    // Preprocessing
    bool useGaussianBlur = true;
    double blurSigma = 1.0;
    bool useAdaptiveThreshold = true;
    bool useMorphology = true;
    
    // Zones de capture par plateforme
    struct Platform {
        std::string name;
        std::vector<OCRConfig::CaptureZone> zones;
        bool autoDetect = true;
    };
    
    struct CaptureZone {
        std::string name;
        int x, y, width, height;
        std::string type; // "card", "pot", "stack", "action"
    };
    
    std::vector<Platform> platforms;
    std::string activePlatform = "auto";
};

// Configuration UI
struct UIConfig {
    // Thème et apparence
    std::string theme = "dark";
    std::string accentColor = "#4CAF50";
    int fontSize = 12;
    std::string fontFamily = "Segoe UI";
    
    // Fenêtre
    int windowWidth = 1400;
    int windowHeight = 900;
    bool startMaximized = false;
    bool rememberPosition = true;
    
    // Opacité et transparence
    double windowOpacity = 1.0;
    bool alwaysOnTop = false;
    
    // Mise à jour temps réel
    uint32_t gameStateUpdateMs = 1000;
    uint32_t strategyUpdateMs = 2000;
    uint32_t statsUpdateMs = 5000;
    uint32_t performanceUpdateMs = 3000;
    
    // Affichage
    bool showPerformanceMetrics = true;
    bool showDebugLogs = false;
    bool showCharts = true;
    
    // Notifications
    bool enableTrayIcon = true;
    bool minimizeToTray = true;
    bool showNotifications = true;
    
    // Langue
    std::string language = "fr";
};

// Configuration base de données
struct DatabaseConfig {
    std::string type = "sqlite"; // "sqlite", "postgresql"
    std::string path = "./data/rtpa.db";
    
    // Pour PostgreSQL
    std::string host = "localhost";
    uint16_t port = 5432;
    std::string database = "rtpa";
    std::string username;
    std::string password;
    
    // Performance
    uint32_t connectionPoolSize = 5;
    uint32_t queryTimeout = 30;
    
    // Rétention des données
    uint32_t maxGameHistoryDays = 30;
    bool autoCleanup = true;
};

// Configuration système
struct SystemConfig {
    // Threading
    uint32_t maxWorkerThreads = 16;
    bool useThreadPool = true;
    
    // Mémoire
    size_t maxMemoryUsage = 2ULL * 1024 * 1024 * 1024; // 2GB
    bool enableMemoryMonitoring = true;
    
    // Performance
    bool enableCpuOptimizations = true;
    bool enableSIMD = true;
    std::string cpuAffinityMask;
    
    // Logging
    std::string logLevel = "info"; // "debug", "info", "warn", "error"
    std::string logPath = "./logs/";
    bool enableFileLogging = true;
    bool enableConsoleLogging = true;
    uint32_t maxLogFiles = 10;
    
    // Platform detection
    uint32_t platformDetectionInterval = 2000; // ms
    bool autoStartOnPlatformDetected = true;
    
    // CUDA
    bool enableCuda = true;
    int cudaDeviceId = 0;
    size_t cudaMemoryLimit = 1ULL * 1024 * 1024 * 1024; // 1GB
};

// Configuration complète de l'application
struct AppConfig {
    CfrConfig cfr;
    OCRConfig ocr;
    UIConfig ui;
    DatabaseConfig database;
    SystemConfig system;
    
    // Métadonnées
    std::string version = "2.0.0";
    std::string configVersion = "1.0";
    uint64_t lastModified = 0;
    
    // Validation
    bool isValid() const;
    
    // Serialization
    bool saveToFile(const std::string& path) const;
    bool loadFromFile(const std::string& path);
    
    // Defaults
    static AppConfig getDefault();
    static AppConfig getHighPerformance();
    static AppConfig getLowResource();
    static AppConfig getDevelopment();
};

// Configuration session utilisateur
struct SessionConfig {
    std::string sessionId;
    uint64_t startTime;
    uint64_t endTime;
    
    // Statistiques de session
    uint64_t handsPlayed = 0;
    uint64_t cfrIterations = 0;
    uint64_t monteCarloSimulations = 0;
    
    // Paramètres utilisateur de session
    std::string activePlatform;
    std::unordered_map<std::string, std::string> userSettings;
    
    // Persistance modèle CFR pour cette session
    std::string cfrModelSnapshot;
    
    bool saveToFile(const std::string& path) const;
    bool loadFromFile(const std::string& path);
};

} // namespace rtpa::types