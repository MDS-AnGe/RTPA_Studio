/**
 * CFR Engine C++20 Ultra-Performance
 * Remplacement complet du moteur Python/Rust
 * Optimisations SIMD + multithreading + CUDA optionnel
 */

#pragma once

#include <memory>
#include <unordered_map>
#include <vector>
#include <atomic>
#include <thread>
#include <mutex>
#include <future>
#include <random>

#include "types/PokerTypes.h"
#include "types/ConfigTypes.h"

#ifdef RTPA_CUDA_ENABLED
#include <cuda_runtime.h>
#include <curand.h>
#endif

namespace rtpa::algorithms {

/**
 * Moteur CFR (Counterfactual Regret Minimization) haute performance
 * Architecture thread-safe avec optimisations natives C++20
 */
class CfrEngine {
public:
    struct Config {
        uint32_t maxIterations = 10000;
        double convergenceThreshold = 0.01;
        uint32_t numThreads = std::thread::hardware_concurrency();
        bool useGpuAcceleration = true;
        uint32_t batchSize = 1000;
        double explorationRate = 0.1;
        double discountFactor = 0.95;
    };

    explicit CfrEngine(const Config& config = Config{});
    ~CfrEngine();

    // Interface principale
    bool initialize();
    void shutdown();

    // Training CFR
    double trainBatch(const std::vector<types::GameState>& states);
    std::future<double> trainBatchAsync(const std::vector<types::GameState>& states);
    double trainIntensive(const std::vector<types::GameState>& states, uint32_t iterations);

    // Stratégies optimales
    types::Strategy getStrategy(const types::GameState& state) const;
    types::ActionType getBestAction(const types::GameState& state) const;
    double getActionProbability(const types::GameState& state, types::ActionType action) const;

    // Calculs de probabilités
    double calculateWinProbability(const types::GameState& state, uint32_t simulations = 10000);
    types::SimulationResult calculateExpectedValue(const types::GameState& state, uint32_t simulations = 10000);

    // État et diagnostics
    types::PerformanceStats getPerformanceStats() const;
    bool isInitialized() const { return initialized_; }
    void resetStatistics();

    // Persistence
    bool saveModel(const std::string& filepath) const;
    bool loadModel(const std::string& filepath);

private:
    // Configuration
    Config config_;
    std::atomic<bool> initialized_{false};
    std::atomic<bool> shutdown_requested_{false};

    // Tables CFR thread-safe
    mutable std::mutex infosets_mutex_;
    std::unordered_map<std::string, std::unique_ptr<types::InfoSet>> infoSets_;

    // Statistiques
    mutable std::mutex stats_mutex_;
    types::PerformanceStats stats_;

    // Threading
    std::vector<std::thread> worker_threads_;
    std::vector<std::mt19937> thread_rngs_;

    // CUDA ressources
    #ifdef RTPA_CUDA_ENABLED
    cudaStream_t cuda_stream_ = nullptr;
    curandGenerator_t curand_gen_ = nullptr;
    float* d_states_ = nullptr;
    float* d_results_ = nullptr;
    size_t cuda_memory_allocated_ = 0;
    bool cuda_initialized_ = false;

    bool initializeCuda();
    void shutdownCuda();
    double trainBatchCuda(const std::vector<types::GameState>& states);
    #endif

    // Méthodes internes CFR
    double cfr(const types::GameState& state, double probability, std::mt19937& rng);
    double calculateRegret(const types::GameState& state, types::ActionType action, double probability, std::mt19937& rng);
    
    // Gestion des information sets
    types::InfoSet* getOrCreateInfoSet(const std::string& key);
    std::string generateInfoSetKey(const types::GameState& state) const;
    
    // Simulations Monte Carlo optimisées
    double runMonteCarloSimulation(const types::GameState& state, uint32_t simulations, std::mt19937& rng);
    bool simulateHand(const types::GameState& state, std::mt19937& rng);
    
    // Optimisations SIMD (si supportées)
    #ifdef __AVX2__
    void vectorizedRegretUpdate(float* regrets, const float* updates, size_t count);
    #endif

    // Threading helpers
    void initializeThreads();
    void shutdownThreads();
    double trainBatchMultiThreaded(const std::vector<types::GameState>& states);

    // Utilitaires
    std::vector<types::ActionType> getLegalActions(const types::GameState& state) const;
    double calculateHandStrength(const types::GameState& state) const;
    double calculatePotOdds(const types::GameState& state) const;
};

/**
 * Factory pour création d'engines CFR avec différentes configurations
 */
class CfrEngineFactory {
public:
    enum class EngineType {
        Standard,      // Configuration standard
        HighPerformance, // Max performance avec toutes optimisations
        LowLatency,    // Optimisé pour latence minimale
        HighThroughput // Optimisé pour débit maximal
    };

    static std::unique_ptr<CfrEngine> create(EngineType type);
    static std::unique_ptr<CfrEngine> create(const CfrEngine::Config& config);
};

} // namespace rtpa::algorithms