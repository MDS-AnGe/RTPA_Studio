/**
 * RTPA Studio - Configuration Manager avec adaptation automatique
 * Gestion dynamique des paramètres avec mise à jour visuelle temps réel
 * Compatible Windows avec détection matérielle automatique
 */

#pragma once

#include <string>
#include <map>
#include <memory>
#include <functional>
#include <mutex>
#include <atomic>
#include <set>
#include <QObject>
#include <QTimer>
#include <QSettings>

#include "utils/HardwareDetector.h"

namespace rtpa::core {

enum class ConfigChangeType {
    Manual,        // Changement utilisateur
    Automatic,     // Adaptation matérielle automatique
    Performance    // Optimisation performance temps réel
};

struct ConfigValue {
    enum Type { Integer, Double, Boolean, String };
    
    Type type;
    int intValue = 0;
    double doubleValue = 0.0;
    bool boolValue = false;
    std::string stringValue;
    
    // Metadata pour UI
    int minInt = 0, maxInt = 100;
    double minDouble = 0.0, maxDouble = 100.0;
    std::string description;
    std::string category;
    bool requiresRestart = false;
    
    ConfigValue(int val, int min = 0, int max = 100, const std::string& desc = "", const std::string& cat = "General")
        : type(Integer), intValue(val), minInt(min), maxInt(max), description(desc), category(cat) {}
    
    ConfigValue(double val, double min = 0.0, double max = 100.0, const std::string& desc = "", const std::string& cat = "General")
        : type(Double), doubleValue(val), minDouble(min), maxDouble(max), description(desc), category(cat) {}
    
    ConfigValue(bool val, const std::string& desc = "", const std::string& cat = "General")
        : type(Boolean), boolValue(val), description(desc), category(cat) {}
    
    ConfigValue(const std::string& val, const std::string& desc = "", const std::string& cat = "General")
        : type(String), stringValue(val), description(desc), category(cat) {}
};

class ConfigManager : public QObject {
    Q_OBJECT
    
public:
    explicit ConfigManager(QObject* parent = nullptr);
    ~ConfigManager();
    
    // Initialisation avec détection matérielle
    bool initialize();
    void shutdown();
    
    // Configuration values
    bool getBool(const std::string& key, bool defaultValue = false) const;
    int getInt(const std::string& key, int defaultValue = 0) const;
    double getDouble(const std::string& key, double defaultValue = 0.0) const;
    std::string getString(const std::string& key, const std::string& defaultValue = "") const;
    
    void setBool(const std::string& key, bool value, ConfigChangeType changeType = ConfigChangeType::Manual);
    void setInt(const std::string& key, int value, ConfigChangeType changeType = ConfigChangeType::Manual);
    void setDouble(const std::string& key, double value, ConfigChangeType changeType = ConfigChangeType::Manual);
    void setString(const std::string& key, const std::string& value, ConfigChangeType changeType = ConfigChangeType::Manual);
    
    // Configuration complète par catégorie
    std::map<std::string, ConfigValue> getConfigByCategory(const std::string& category) const;
    std::vector<std::string> getCategories() const;
    
    // Sauvegarde/Chargement
    bool saveConfig();
    bool loadConfig();
    void resetToDefaults();
    
    // Adaptation automatique matérielle
    void enableAutoHardwareAdaptation(bool enable = true);
    void updateFromHardware();
    bool isHardwareAdaptationEnabled() const { return m_autoHardwareAdaptation; }
    
    // Configuration dynamique temps réel
    void enablePerformanceMonitoring(bool enable = true);
    void updateFromPerformanceMetrics();
    
    // Export/Import configuration
    bool exportConfig(const std::string& filename) const;
    bool importConfig(const std::string& filename);
    
    // Getters pour matériel détecté
    const rtpa::utils::HardwareInfo& getHardwareInfo() const;
    const rtpa::utils::OptimalSettings& getCurrentSettings() const;
    
signals:
    // Signaux pour mise à jour UI temps réel
    void configChanged(const std::string& key, ConfigChangeType changeType);
    void categoryChanged(const std::string& category, ConfigChangeType changeType);
    void hardwareDetected(const rtpa::utils::HardwareInfo& info);
    void optimalSettingsCalculated(const rtpa::utils::OptimalSettings& settings);
    void performanceAlert(const std::string& message, const std::string& recommendation);

private slots:
    void onPerformanceMonitorTimer();
    void onHardwareAdaptationTimer();

private:
    void initializeDefaultConfig();
    void applyOptimalSettings(const rtpa::utils::OptimalSettings& settings);
    void validateConfigValue(const std::string& key, ConfigValue& value) const;
    
    // Configuration storage
    mutable std::mutex m_configMutex;
    std::map<std::string, ConfigValue> m_config;
    std::unique_ptr<QSettings> m_settings;
    
    // Hardware detection
    std::unique_ptr<rtpa::utils::HardwareDetector> m_hardwareDetector;
    rtpa::utils::OptimalSettings m_currentOptimalSettings;
    std::atomic<bool> m_autoHardwareAdaptation{true};
    
    // Performance monitoring
    QTimer* m_performanceTimer;
    QTimer* m_hardwareTimer;
    std::atomic<bool> m_performanceMonitoring{false};
    mutable std::map<std::string, double> m_performanceHistory;
    
    // Change tracking
    std::map<std::string, ConfigChangeType> m_lastChangeType;
};

} // namespace rtpa::core