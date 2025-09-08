/**
 * RTPA Studio - Configuration Manager Implementation
 * Configuration dynamique avec adaptation automatique Windows/Linux/macOS
 */

#include "ConfigManager.h"
#include <QApplication>
#include <QDir>
#include <QStandardPaths>
#include <QJsonDocument>
#include <QJsonObject>
#include <iostream>
#include <fstream>

namespace rtpa::core {

ConfigManager::ConfigManager(QObject* parent) 
    : QObject(parent)
    , m_hardwareDetector(std::make_unique<rtpa::utils::HardwareDetector>())
    , m_performanceTimer(new QTimer(this))
    , m_hardwareTimer(new QTimer(this))
{
    // Initialisation settings Qt pour persistance
    QString configPath = QStandardPaths::writableLocation(QStandardPaths::AppConfigLocation);
    QDir().mkpath(configPath);
    m_settings = std::make_unique<QSettings>(configPath + "/rtpa_config.ini", QSettings::IniFormat);
    
    // Configuration des timers
    connect(m_performanceTimer, &QTimer::timeout, this, &ConfigManager::onPerformanceMonitorTimer);
    connect(m_hardwareTimer, &QTimer::timeout, this, &ConfigManager::onHardwareAdaptationTimer);
    
    std::cout << "⚙️  Configuration Manager initialisé" << std::endl;
}

ConfigManager::~ConfigManager() {
    shutdown();
}

bool ConfigManager::initialize() {
    std::cout << "🛠️  Initialisation Configuration Manager..." << std::endl;
    
    // Détection matérielle
    if (!m_hardwareDetector->detectHardware()) {
        std::cerr << "⚠️  Détection matérielle échouée, utilisation configuration par défaut" << std::endl;
    }
    
    // Configuration par défaut
    initializeDefaultConfig();
    
    // Chargement configuration sauvée
    loadConfig();
    
    // Calcul configuration optimale basée sur matériel
    updateFromHardware();
    
    // Démarrage monitoring si activé
    if (m_performanceMonitoring) {
        enablePerformanceMonitoring(true);
    }
    
    if (m_autoHardwareAdaptation) {
        enableAutoHardwareAdaptation(true);
    }
    
    std::cout << "✅ Configuration Manager prêt" << std::endl;
    emit hardwareDetected(m_hardwareDetector->getHardwareInfo());
    
    return true;
}

void ConfigManager::shutdown() {
    m_performanceTimer->stop();
    m_hardwareTimer->stop();
    
    // Sauvegarde configuration avant fermeture
    saveConfig();
    
    std::cout << "🔒 Configuration Manager fermé" << std::endl;
}

void ConfigManager::initializeDefaultConfig() {
    std::lock_guard<std::mutex> lock(m_configMutex);
    
    // === CFR Configuration ===
    m_config["cfr.iterations"] = ConfigValue(1000, 100, 10000, "Nombre d'itérations CFR", "CFR");
    m_config["cfr.threads"] = ConfigValue(4, 1, 32, "Threads de calcul CFR", "CFR");
    m_config["cfr.batch_size"] = ConfigValue(500, 100, 5000, "Taille batch CFR", "CFR");
    m_config["cfr.enable_gpu"] = ConfigValue(false, "Activer accélération GPU", "CFR");
    m_config["cfr.discount_factor"] = ConfigValue(0.95, 0.1, 1.0, "Facteur de discount CFR", "CFR");
    
    // === GPU Configuration ===
    m_config["gpu.enable_cuda"] = ConfigValue(false, "Activer CUDA", "GPU");
    m_config["gpu.memory_limit"] = ConfigValue(2048, 512, 8192, "Limite mémoire GPU (MB)", "GPU");
    m_config["gpu.auto_fallback"] = ConfigValue(true, "Fallback CPU automatique", "GPU");
    
    // === OCR Configuration ===
    m_config["ocr.threads"] = ConfigValue(2, 1, 8, "Threads OCR", "OCR");
    m_config["ocr.scale_factor"] = ConfigValue(1.0, 0.5, 3.0, "Facteur d'échelle OCR", "OCR");
    m_config["ocr.enable_preprocessing"] = ConfigValue(true, "Préprocessing OpenCV", "OCR");
    m_config["ocr.tesseract_oem"] = ConfigValue(3, 0, 3, "Tesseract OEM mode", "OCR");
    
    // === Performance Configuration ===
    m_config["perf.max_memory_mb"] = ConfigValue(1024, 256, 16384, "Mémoire maximum (MB)", "Performance");
    m_config["perf.enable_monitoring"] = ConfigValue(true, "Monitoring performance", "Performance");
    m_config["perf.auto_optimization"] = ConfigValue(true, "Optimisation automatique", "Performance");
    m_config["perf.target_fps"] = ConfigValue(60, 30, 144, "FPS cible interface", "Performance");
    
    // === Interface Configuration ===
    m_config["ui.theme"] = ConfigValue("dark", "Thème interface", "Interface");
    m_config["ui.language"] = ConfigValue("fr", "Langue interface", "Interface");
    m_config["ui.enable_animations"] = ConfigValue(true, "Animations interface", "Interface");
    m_config["ui.opacity"] = ConfigValue(0.95, 0.3, 1.0, "Opacité fenêtres", "Interface");
    
    // === Windows Specific ===
    #ifdef _WIN32
    m_config["windows.high_dpi_scaling"] = ConfigValue(true, "Mise à l'échelle DPI", "Windows");
    m_config["windows.hardware_acceleration"] = ConfigValue(true, "Accélération matérielle", "Windows");
    m_config["windows.power_management"] = ConfigValue(false, "Gestion alimentation", "Windows");
    #endif
}

bool ConfigManager::getBool(const std::string& key, bool defaultValue) const {
    std::lock_guard<std::mutex> lock(m_configMutex);
    auto it = m_config.find(key);
    return (it != m_config.end() && it->second.type == ConfigValue::Boolean) ? 
           it->second.boolValue : defaultValue;
}

int ConfigManager::getInt(const std::string& key, int defaultValue) const {
    std::lock_guard<std::mutex> lock(m_configMutex);
    auto it = m_config.find(key);
    return (it != m_config.end() && it->second.type == ConfigValue::Integer) ? 
           it->second.intValue : defaultValue;
}

double ConfigManager::getDouble(const std::string& key, double defaultValue) const {
    std::lock_guard<std::mutex> lock(m_configMutex);
    auto it = m_config.find(key);
    return (it != m_config.end() && it->second.type == ConfigValue::Double) ? 
           it->second.doubleValue : defaultValue;
}

std::string ConfigManager::getString(const std::string& key, const std::string& defaultValue) const {
    std::lock_guard<std::mutex> lock(m_configMutex);
    auto it = m_config.find(key);
    return (it != m_config.end() && it->second.type == ConfigValue::String) ? 
           it->second.stringValue : defaultValue;
}

void ConfigManager::setBool(const std::string& key, bool value, ConfigChangeType changeType) {
    {
        std::lock_guard<std::mutex> lock(m_configMutex);
        auto it = m_config.find(key);
        if (it != m_config.end() && it->second.type == ConfigValue::Boolean) {
            if (it->second.boolValue != value) {
                it->second.boolValue = value;
                m_lastChangeType[key] = changeType;
            } else {
                return; // Pas de changement
            }
        }
    }
    
    emit configChanged(key, changeType);
    
    // Auto-save si changement manuel
    if (changeType == ConfigChangeType::Manual) {
        saveConfig();
    }
}

void ConfigManager::setInt(const std::string& key, int value, ConfigChangeType changeType) {
    {
        std::lock_guard<std::mutex> lock(m_configMutex);
        auto it = m_config.find(key);
        if (it != m_config.end() && it->second.type == ConfigValue::Integer) {
            // Validation des limites
            value = std::max(it->second.minInt, std::min(value, it->second.maxInt));
            
            if (it->second.intValue != value) {
                it->second.intValue = value;
                m_lastChangeType[key] = changeType;
            } else {
                return;
            }
        }
    }
    
    emit configChanged(key, changeType);
    
    if (changeType == ConfigChangeType::Manual) {
        saveConfig();
    }
}

void ConfigManager::setDouble(const std::string& key, double value, ConfigChangeType changeType) {
    {
        std::lock_guard<std::mutex> lock(m_configMutex);
        auto it = m_config.find(key);
        if (it != m_config.end() && it->second.type == ConfigValue::Double) {
            value = std::max(it->second.minDouble, std::min(value, it->second.maxDouble));
            
            if (std::abs(it->second.doubleValue - value) > 1e-6) {
                it->second.doubleValue = value;
                m_lastChangeType[key] = changeType;
            } else {
                return;
            }
        }
    }
    
    emit configChanged(key, changeType);
    
    if (changeType == ConfigChangeType::Manual) {
        saveConfig();
    }
}

void ConfigManager::updateFromHardware() {
    if (!m_hardwareDetector) return;
    
    std::cout << "🔧 Mise à jour configuration depuis matériel détecté..." << std::endl;
    
    m_currentOptimalSettings = m_hardwareDetector->calculateOptimalSettings();
    applyOptimalSettings(m_currentOptimalSettings);
    
    emit optimalSettingsCalculated(m_currentOptimalSettings);
}

void ConfigManager::applyOptimalSettings(const rtpa::utils::OptimalSettings& settings) {
    // Application sans déclenchement sauvegarde (auto-configuration)
    setInt("cfr.iterations", settings.cfrIterations, ConfigChangeType::Automatic);
    setInt("cfr.threads", settings.cfrThreads, ConfigChangeType::Automatic);
    setInt("cfr.batch_size", settings.batchSize, ConfigChangeType::Automatic);
    setBool("cfr.enable_gpu", settings.useGPUAcceleration, ConfigChangeType::Automatic);
    
    setInt("ocr.threads", settings.ocrThreads, ConfigChangeType::Automatic);
    setDouble("ocr.scale_factor", settings.ocrScaleFactor, ConfigChangeType::Automatic);
    
    setInt("perf.max_memory_mb", static_cast<int>(settings.maxMemoryUsageMB), ConfigChangeType::Automatic);
    
    std::cout << "  ✅ Configuration matérielle appliquée automatiquement" << std::endl;
    emit categoryChanged("CFR", ConfigChangeType::Automatic);
    emit categoryChanged("OCR", ConfigChangeType::Automatic);
    emit categoryChanged("Performance", ConfigChangeType::Automatic);
}

void ConfigManager::enableAutoHardwareAdaptation(bool enable) {
    m_autoHardwareAdaptation = enable;
    
    if (enable) {
        m_hardwareTimer->start(30000); // Check every 30 seconds
        std::cout << "🔄 Adaptation matérielle automatique activée" << std::endl;
    } else {
        m_hardwareTimer->stop();
        std::cout << "⏸️  Adaptation matérielle automatique désactivée" << std::endl;
    }
}

void ConfigManager::enablePerformanceMonitoring(bool enable) {
    m_performanceMonitoring = enable;
    
    if (enable) {
        m_performanceTimer->start(5000); // Monitor every 5 seconds
        std::cout << "📊 Monitoring performance activé" << std::endl;
    } else {
        m_performanceTimer->stop();
        std::cout << "⏸️  Monitoring performance désactivé" << std::endl;
    }
}

void ConfigManager::onPerformanceMonitorTimer() {
    if (!m_hardwareDetector) return;
    
    double cpuUsage = m_hardwareDetector->getCurrentCPUUsage();
    double ramUsage = m_hardwareDetector->getCurrentRAMUsage();
    
    // Alerte si utilisation critique
    if (cpuUsage > 90.0) {
        emit performanceAlert("CPU usage critique: " + std::to_string(static_cast<int>(cpuUsage)) + "%", 
                             "Réduire threads CFR recommandé");
    }
    
    if (ramUsage > 85.0) {
        emit performanceAlert("Mémoire critique: " + std::to_string(static_cast<int>(ramUsage)) + "%",
                             "Réduire limite mémoire recommandé");
    }
    
    // Auto-ajustement si activé
    if (getBool("perf.auto_optimization", true)) {
        rtpa::utils::OptimalSettings settings = m_currentOptimalSettings;
        m_hardwareDetector->updateSettingsBasedOnPerformance(settings);
        
        if (settings.cfrThreads != m_currentOptimalSettings.cfrThreads ||
            settings.maxMemoryUsageMB != m_currentOptimalSettings.maxMemoryUsageMB) {
            m_currentOptimalSettings = settings;
            applyOptimalSettings(settings);
        }
    }
}

void ConfigManager::onHardwareAdaptationTimer() {
    // Re-détecter le matériel périodiquement (nouveau GPU, changement config)
    updateFromHardware();
}

bool ConfigManager::saveConfig() {
    std::lock_guard<std::mutex> lock(m_configMutex);
    
    if (!m_settings) return false;
    
    try {
        m_settings->clear();
        
        for (const auto& [key, value] : m_config) {
            switch (value.type) {
                case ConfigValue::Integer:
                    m_settings->setValue(QString::fromStdString(key), value.intValue);
                    break;
                case ConfigValue::Double:
                    m_settings->setValue(QString::fromStdString(key), value.doubleValue);
                    break;
                case ConfigValue::Boolean:
                    m_settings->setValue(QString::fromStdString(key), value.boolValue);
                    break;
                case ConfigValue::String:
                    m_settings->setValue(QString::fromStdString(key), QString::fromStdString(value.stringValue));
                    break;
            }
        }
        
        m_settings->sync();
        
        if (m_settings->status() != QSettings::NoError) {
            std::cerr << "⚠️  Erreur sauvegarde configuration" << std::endl;
            return false;
        }
        
        std::cout << "💾 Configuration sauvegardée" << std::endl;
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "❌ Exception sauvegarde config: " << e.what() << std::endl;
        return false;
    }
}

bool ConfigManager::loadConfig() {
    std::lock_guard<std::mutex> lock(m_configMutex);
    
    if (!m_settings) return false;
    
    try {
        for (auto& [key, value] : m_config) {
            QString qkey = QString::fromStdString(key);
            
            if (m_settings->contains(qkey)) {
                QVariant qvalue = m_settings->value(qkey);
                
                switch (value.type) {
                    case ConfigValue::Integer:
                        value.intValue = qvalue.toInt();
                        break;
                    case ConfigValue::Double:
                        value.doubleValue = qvalue.toDouble();
                        break;
                    case ConfigValue::Boolean:
                        value.boolValue = qvalue.toBool();
                        break;
                    case ConfigValue::String:
                        value.stringValue = qvalue.toString().toStdString();
                        break;
                }
            }
        }
        
        std::cout << "📂 Configuration chargée depuis fichier" << std::endl;
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "❌ Exception chargement config: " << e.what() << std::endl;
        return false;
    }
}

std::map<std::string, ConfigValue> ConfigManager::getConfigByCategory(const std::string& category) const {
    std::lock_guard<std::mutex> lock(m_configMutex);
    
    std::map<std::string, ConfigValue> result;
    for (const auto& [key, value] : m_config) {
        if (value.category == category) {
            result[key] = value;
        }
    }
    return result;
}

std::vector<std::string> ConfigManager::getCategories() const {
    std::lock_guard<std::mutex> lock(m_configMutex);
    
    std::set<std::string> categories;
    for (const auto& [key, value] : m_config) {
        categories.insert(value.category);
    }
    
    return std::vector<std::string>(categories.begin(), categories.end());
}

const rtpa::utils::HardwareInfo& ConfigManager::getHardwareInfo() const {
    return m_hardwareDetector->getHardwareInfo();
}

const rtpa::utils::OptimalSettings& ConfigManager::getCurrentSettings() const {
    return m_currentOptimalSettings;
}

} // namespace rtpa::core

#include "ConfigManager.moc"