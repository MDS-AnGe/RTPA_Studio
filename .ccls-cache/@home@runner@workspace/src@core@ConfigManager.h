/**
 * Gestionnaire de configuration YAML
 */

#pragma once

#include "types/ConfigTypes.h"
#include <string>
#include <memory>

namespace rtpa::core {

class ConfigManager {
public:
    ConfigManager();
    ~ConfigManager();

    bool loadDefaultConfig();
    bool loadConfig(const std::string& path);
    bool saveConfig(const std::string& path) const;
    
    const types::AppConfig& getConfig() const { return config_; }
    void setConfig(const types::AppConfig& config) { config_ = config; }

private:
    types::AppConfig config_;
};

} // namespace rtpa::core