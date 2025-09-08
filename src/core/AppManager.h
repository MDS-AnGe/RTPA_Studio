/**
 * Gestionnaire principal de l'application RTPA Studio
 * Orchestre tous les composants C++ haute performance
 */

#pragma once

#include <memory>
#include <atomic>
#include <thread>
#include <mutex>
#include <future>
#include <queue>
#include <condition_variable>

#include "types/PokerTypes.h"
#include "types/ConfigTypes.h"

// Forward declarations
namespace rtpa::algorithms {
    class CfrEngine;
    class MonteCarloSimulator;
}

namespace rtpa::ocr {
    class ScreenCapture;
    class TesseractOCR;
    class GameStateExtractor;
}

namespace rtpa::database {
    class DatabaseManager;
}

namespace rtpa::utils {
    class Logger;
    class PlatformDetector;
}

namespace rtpa::core {

class ConfigManager;

/**
 * Gestionnaire principal orchestrant tous les composants RTPA
 * Remplacement complet du système Python multi-fichiers
 */
class AppManager {
public:
    enum class State {
        Uninitialized,
        Initializing,
        Ready,
        Running,
        Stopping,
        Error
    };

    AppManager();
    ~AppManager();

    // Lifecycle principal
    bool initialize();
    void shutdown();
    bool isInitialized() const { return state_ == State::Ready || state_ == State::Running; }
    State getState() const { return state_; }

    // Contrôle CFR Engine
    bool startCfrTraining();
    void stopCfrTraining();
    bool isCfrTrainingActive() const { return cfrTrainingActive_; }
    
    std::future<double> trainCfrBatch(const std::vector<types::GameState>& states);
    std::future<double> runIntensiveTraining(uint32_t iterations);
    void resetCfrModel();

    // Contrôle OCR et capture
    bool startScreenCapture();
    void stopScreenCapture();
    bool isScreenCaptureActive() const { return screenCaptureActive_; }
    
    bool calibrateOCR();
    types::GameState extractCurrentGameState();

    // Interface stratégie et recommandations
    types::Strategy getCurrentStrategy() const;
    types::ActionType getBestAction() const;
    double calculateWinProbability(uint32_t simulations = 10000);
    types::SimulationResult calculateExpectedValue(uint32_t simulations = 10000);

    // Gestion de configuration
    bool loadConfiguration(const std::string& configPath = "");
    bool saveConfiguration(const std::string& configPath = "") const;
    void updateConfiguration(const types::AppConfig& newConfig);

    // Persistence et session
    bool saveSession(const std::string& sessionPath);
    bool loadSession(const std::string& sessionPath);
    
    bool saveCfrModel(const std::string& modelPath);
    bool loadCfrModel(const std::string& modelPath);

    // Statistiques et monitoring
    types::PerformanceStats getPerformanceStats() const;
    std::vector<types::GameState> getGameHistory(size_t maxRecords = 100) const;
    
    // Auto-detection des plateformes poker
    bool detectPokerPlatform();
    std::vector<std::string> getAvailablePlatforms() const;
    void setPlatform(const std::string& platformName);

    // Événements et callbacks
    using GameStateCallback = std::function<void(const types::GameState&)>;
    using StrategyCallback = std::function<void(const types::Strategy&)>;
    using PerformanceCallback = std::function<void(const types::PerformanceStats&)>;

    void setGameStateCallback(GameStateCallback callback);
    void setStrategyCallback(StrategyCallback callback);
    void setPerformanceCallback(PerformanceCallback callback);

private:
    // État principal
    std::atomic<State> state_{State::Uninitialized};
    std::atomic<bool> shutdownRequested_{false};

    // Composants principaux
    std::unique_ptr<ConfigManager> configManager_;
    std::unique_ptr<algorithms::CfrEngine> cfrEngine_;
    std::unique_ptr<algorithms::MonteCarloSimulator> monteCarloSimulator_;
    std::unique_ptr<ocr::ScreenCapture> screenCapture_;
    std::unique_ptr<ocr::TesseractOCR> tesseractOCR_;
    std::unique_ptr<ocr::GameStateExtractor> gameStateExtractor_;
    std::unique_ptr<database::DatabaseManager> databaseManager_;
    std::unique_ptr<utils::PlatformDetector> platformDetector_;

    // Threading et synchronisation
    std::thread mainWorkerThread_;
    std::thread ocrWorkerThread_;
    std::thread cfrWorkerThread_;
    
    mutable std::mutex stateMutex_;
    mutable std::mutex gameStateMutex_;
    mutable std::mutex strategyMutex_;

    // État applicatif
    std::atomic<bool> cfrTrainingActive_{false};
    std::atomic<bool> screenCaptureActive_{false};
    
    types::GameState currentGameState_;
    types::Strategy currentStrategy_;
    types::AppConfig appConfig_;

    // File d'événements
    struct Event {
        enum Type { 
            GameStateUpdate, 
            StrategyUpdate, 
            PerformanceUpdate,
            PlatformDetected,
            Error
        };
        
        Type type;
        std::any data;
        uint64_t timestamp;
    };
    
    std::queue<Event> eventQueue_;
    std::mutex eventQueueMutex_;
    std::condition_variable eventCondition_;

    // Callbacks
    GameStateCallback gameStateCallback_;
    StrategyCallback strategyCallback_;
    PerformanceCallback performanceCallback_;

    // Méthodes internes d'initialisation
    bool initializeComponents();
    void shutdownComponents();
    
    bool initializeCfrEngine();
    bool initializeOCRSystem();
    bool initializeDatabase();
    bool initializePlatformDetection();

    // Workers threads
    void mainWorkerLoop();
    void ocrWorkerLoop();
    void cfrWorkerLoop();
    
    void processEventQueue();
    void updateGameState();
    void updateStrategy();
    void updatePerformanceStats();

    // Gestion des événements
    void pushEvent(Event::Type type, std::any data = {});
    void handleEvent(const Event& event);
    
    void onGameStateChanged(const types::GameState& newState);
    void onStrategyUpdated(const types::Strategy& newStrategy);
    void onPlatformDetected(const std::string& platform);

    // Utilitaires internes
    bool validateConfiguration() const;
    void applyConfiguration();
    
    std::string generateSessionId() const;
    std::string getDefaultConfigPath() const;
    std::string getDefaultSessionPath() const;

    // Error handling
    void handleError(const std::string& component, const std::string& error);
    void setState(State newState);
};

/**
 * Factory pour création d'AppManager avec différents profils
 */
class AppManagerFactory {
public:
    enum class Profile {
        Development,    // Configuration pour développement/debug
        Performance,    // Performance maximale
        LowResource,    // Optimisé ressources limitées
        Production      // Configuration production stable
    };

    static std::unique_ptr<AppManager> create(Profile profile = Profile::Production);
    static types::AppConfig getProfileConfig(Profile profile);
};

} // namespace rtpa::core