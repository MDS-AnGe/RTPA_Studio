/**
 * Implémentation CFR Engine C++20 haute performance
 * Calculs natifs ultra-optimisés
 */

#include "CfrEngine.h"
#include "utils/Logger.h"

#include <algorithm>
#include <execution>
#include <numeric>
#include <cmath>
#include <chrono>
#include <fstream>
#include <immintrin.h> // AVX2 si disponible

using namespace rtpa::algorithms;
using namespace rtpa::types;

CfrEngine::CfrEngine(const Config& config) : config_(config) {
    utils::Logger::info("🚀 Initialisation CFR Engine C++20 haute performance");
    utils::Logger::info("   ⚡ Threads: " + std::to_string(config_.numThreads));
    utils::Logger::info("   🎯 Max iterations: " + std::to_string(config_.maxIterations));
    
    #ifdef RTPA_CUDA_ENABLED
    utils::Logger::info("   🔥 CUDA: Support disponible");
    #endif
}

CfrEngine::~CfrEngine() {
    shutdown();
}

bool CfrEngine::initialize() {
    if (initialized_) return true;

    try {
        // Initialisation des générateurs aléatoires par thread
        thread_rngs_.reserve(config_.numThreads);
        std::random_device rd;
        
        for (uint32_t i = 0; i < config_.numThreads; ++i) {
            thread_rngs_.emplace_back(rd() + i);
        }

        // Initialisation threading
        initializeThreads();

        #ifdef RTPA_CUDA_ENABLED
        if (config_.useGpuAcceleration) {
            if (initializeCuda()) {
                utils::Logger::info("✅ CUDA acceleration activée");
            } else {
                utils::Logger::warn("⚠️ CUDA initialization échouée, fallback CPU");
                config_.useGpuAcceleration = false;
            }
        }
        #endif

        // Reset statistiques
        resetStatistics();

        initialized_ = true;
        utils::Logger::info("✅ CFR Engine initialisé avec succès");
        return true;

    } catch (const std::exception& e) {
        utils::Logger::error("❌ Erreur initialisation CFR Engine: " + std::string(e.what()));
        return false;
    }
}

void CfrEngine::shutdown() {
    if (!initialized_) return;

    shutdown_requested_ = true;
    
    shutdownThreads();

    #ifdef RTPA_CUDA_ENABLED
    shutdownCuda();
    #endif

    // Cleanup info sets
    {
        std::lock_guard<std::mutex> lock(infosets_mutex_);
        infoSets_.clear();
    }

    initialized_ = false;
    utils::Logger::info("✅ CFR Engine fermé proprement");
}

double CfrEngine::trainBatch(const std::vector<GameState>& states) {
    if (!initialized_ || states.empty()) return 0.0;

    auto start_time = std::chrono::high_resolution_clock::now();

    double convergence = 0.0;

    // Choix de l'implémentation selon configuration
    #ifdef RTPA_CUDA_ENABLED
    if (config_.useGpuAcceleration && cuda_initialized_ && states.size() >= config_.batchSize) {
        convergence = trainBatchCuda(states);
    } else {
        convergence = trainBatchMultiThreaded(states);
    }
    #else
    convergence = trainBatchMultiThreaded(states);
    #endif

    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);

    // Mise à jour des statistiques
    {
        std::lock_guard<std::mutex> lock(stats_mutex_);
        stats_.totalIterations++;
        stats_.averageConvergence = (stats_.averageConvergence + convergence) / 2.0;
        stats_.totalInfoSets = infoSets_.size();
    }

    utils::Logger::debug("CFR batch training: " + std::to_string(states.size()) + 
                        " états, convergence: " + std::to_string(convergence) +
                        ", temps: " + std::to_string(duration.count()) + "μs");

    return convergence;
}

double CfrEngine::trainBatchMultiThreaded(const std::vector<GameState>& states) {
    const size_t num_states = states.size();
    const size_t states_per_thread = std::max(1UL, num_states / config_.numThreads);
    
    std::vector<std::future<double>> futures;
    futures.reserve(config_.numThreads);

    // Lancement des tâches parallèles
    for (uint32_t thread_id = 0; thread_id < config_.numThreads; ++thread_id) {
        size_t start_idx = thread_id * states_per_thread;
        size_t end_idx = (thread_id == config_.numThreads - 1) ? num_states : (start_idx + states_per_thread);
        
        if (start_idx >= num_states) break;

        futures.emplace_back(std::async(std::launch::async, [this, &states, start_idx, end_idx, thread_id]() {
            double thread_convergence = 0.0;
            auto& rng = thread_rngs_[thread_id];

            for (size_t i = start_idx; i < end_idx; ++i) {
                thread_convergence += cfr(states[i], 1.0, rng);
            }

            return thread_convergence / (end_idx - start_idx);
        }));
    }

    // Collecte des résultats
    double total_convergence = 0.0;
    for (auto& future : futures) {
        total_convergence += future.get();
    }

    return total_convergence / futures.size();
}

double CfrEngine::cfr(const GameState& state, double probability, std::mt19937& rng) {
    if (!state.isValid()) return 0.0;

    std::string info_set_key = generateInfoSetKey(state);
    auto* info_set = getOrCreateInfoSet(info_set_key);

    auto legal_actions = getLegalActions(state);
    if (legal_actions.empty()) return 0.0;

    // Calcul de la stratégie courante
    std::vector<double> action_probs(legal_actions.size());
    double normalizing_sum = 0.0;

    for (size_t i = 0; i < legal_actions.size(); ++i) {
        double regret = info_set->strategy.actionProbabilities[legal_actions[i]];
        action_probs[i] = std::max(regret, 0.0);
        normalizing_sum += action_probs[i];
    }

    // Normalisation
    if (normalizing_sum > 0.0) {
        for (auto& prob : action_probs) {
            prob /= normalizing_sum;
        }
    } else {
        // Stratégie uniforme par défaut
        std::fill(action_probs.begin(), action_probs.end(), 1.0 / legal_actions.size());
    }

    // Calcul des utilités pour chaque action
    std::vector<double> action_utilities(legal_actions.size(), 0.0);
    double node_utility = 0.0;

    for (size_t i = 0; i < legal_actions.size(); ++i) {
        // Simulation rapide de l'action
        action_utilities[i] = calculateRegret(state, legal_actions[i], probability * action_probs[i], rng);
        node_utility += action_probs[i] * action_utilities[i];
    }

    // Mise à jour des regrets
    for (size_t i = 0; i < legal_actions.size(); ++i) {
        double regret = action_utilities[i] - node_utility;
        info_set->strategy.updateRegret(legal_actions[i], regret);
    }

    // Mise à jour de la stratégie cumulée
    for (size_t i = 0; i < legal_actions.size(); ++i) {
        auto& cumulative_prob = info_set->strategy.actionProbabilities[legal_actions[i]];
        cumulative_prob += probability * action_probs[i];
    }

    return node_utility;
}

double CfrEngine::calculateRegret(const GameState& state, ActionType action, double probability, std::mt19937& rng) {
    // Heuristique rapide pour calcul de regret
    double base_value = 0.0;
    
    switch (action) {
        case ActionType::Fold:
            base_value = 0.0;
            break;
        case ActionType::Call:
        case ActionType::Check:
            base_value = state.potSize * 0.4 * calculateHandStrength(state);
            break;
        case ActionType::Bet:
        case ActionType::Raise:
            base_value = state.potSize * 0.8 * calculateHandStrength(state);
            break;
        case ActionType::AllIn:
            base_value = state.stackSize * calculateHandStrength(state);
            break;
    }

    // Facteurs d'ajustement
    double position_factor = (static_cast<int>(state.position) + 1) / 6.0;
    double pot_factor = std::min(state.potSize / state.stackSize, 2.0);
    double player_factor = (10.0 - state.numPlayers) / 10.0;

    return base_value * (0.8 + position_factor * 0.4) * (1.0 + pot_factor * 0.2) * (1.0 + player_factor * 0.1);
}

Strategy CfrEngine::getStrategy(const GameState& state) const {
    std::string info_set_key = generateInfoSetKey(state);
    
    {
        std::lock_guard<std::mutex> lock(infosets_mutex_);
        auto it = infoSets_.find(info_set_key);
        if (it != infoSets_.end()) {
            return it->second->strategy;
        }
    }

    // Stratégie par défaut
    Strategy default_strategy;
    default_strategy.actionProbabilities[ActionType::Fold] = 0.2;
    default_strategy.actionProbabilities[ActionType::Call] = 0.3;
    default_strategy.actionProbabilities[ActionType::Bet] = 0.3;
    default_strategy.actionProbabilities[ActionType::Check] = 0.2;
    
    return default_strategy;
}

double CfrEngine::calculateWinProbability(const GameState& state, uint32_t simulations) {
    if (!initialized_) return 0.5;

    auto& rng = thread_rngs_[0]; // Utilise le premier RNG pour thread principal
    return runMonteCarloSimulation(state, simulations, rng);
}

double CfrEngine::runMonteCarloSimulation(const GameState& state, uint32_t simulations, std::mt19937& rng) {
    uint32_t wins = 0;
    
    for (uint32_t i = 0; i < simulations; ++i) {
        if (simulateHand(state, rng)) {
            wins++;
        }
    }

    double win_probability = static_cast<double>(wins) / simulations;
    
    // Mise à jour statistiques
    {
        std::lock_guard<std::mutex> lock(stats_mutex_);
        stats_.totalSimulations += simulations;
    }

    return win_probability;
}

bool CfrEngine::simulateHand(const GameState& state, std::mt19937& rng) {
    // Simulation rapide basée sur la force de main et les facteurs de jeu
    double hand_strength = calculateHandStrength(state);
    double position_bonus = static_cast<int>(state.position) * 0.02;
    double pot_factor = calculatePotOdds(state) * 0.1;
    
    double hero_strength = hand_strength + position_bonus + pot_factor;
    
    // Simulation de l'adversaire moyen
    std::uniform_real_distribution<double> dist(0.2, 0.8);
    double opponent_strength = dist(rng);
    
    return hero_strength > opponent_strength;
}

double CfrEngine::calculateHandStrength(const GameState& state) const {
    // Évaluation rapide de la force de main
    // Implémentation simplifiée - peut être améliorée avec évaluateur complet
    
    double strength = 0.5; // Base neutre
    
    // Bonus pour cartes hautes
    for (const auto& card : state.holeCards) {
        if (static_cast<int>(card.rank) >= 11) { // Jack ou plus
            strength += 0.1;
        }
    }
    
    // Bonus pour paires
    if (state.holeCards[0].rank == state.holeCards[1].rank) {
        strength += 0.2;
    }
    
    // Bonus pour cartes assorties
    if (state.holeCards[0].suit == state.holeCards[1].suit) {
        strength += 0.05;
    }
    
    // Ajustements selon le board
    if (!state.communityCards.empty()) {
        // Logique pour évaluer avec board community cards
        // Simplifié pour cette implémentation
        strength += 0.1; // Bonus arbitraire post-flop
    }
    
    return std::clamp(strength, 0.0, 1.0);
}

InfoSet* CfrEngine::getOrCreateInfoSet(const std::string& key) {
    std::lock_guard<std::mutex> lock(infosets_mutex_);
    
    auto it = infoSets_.find(key);
    if (it != infoSets_.end()) {
        return it->second.get();
    }
    
    auto info_set = std::make_unique<InfoSet>(key);
    auto* ptr = info_set.get();
    infoSets_[key] = std::move(info_set);
    
    return ptr;
}

std::string CfrEngine::generateInfoSetKey(const GameState& state) const {
    // Génération de clé optimisée pour information set
    std::string key;
    key.reserve(64);
    
    // Round de mise
    key += std::to_string(static_cast<int>(state.bettingRound));
    key += "_";
    
    // Position
    key += std::to_string(static_cast<int>(state.position));
    key += "_";
    
    // Abstraction de pot size
    int pot_bucket = static_cast<int>((state.potSize / state.stackSize) * 5.0) % 5;
    key += std::to_string(pot_bucket);
    key += "_";
    
    // Hash des cartes (simplifié)
    uint64_t card_hash = 0;
    for (const auto& card : state.holeCards) {
        card_hash = card_hash * 53 + card.hash();
    }
    key += std::to_string(card_hash % 1000);
    
    return key;
}

PerformanceStats CfrEngine::getPerformanceStats() const {
    std::lock_guard<std::mutex> lock(stats_mutex_);
    return stats_;
}

void CfrEngine::resetStatistics() {
    std::lock_guard<std::mutex> lock(stats_mutex_);
    stats_ = PerformanceStats{};
}

// Factory methods
std::unique_ptr<CfrEngine> CfrEngineFactory::create(EngineType type) {
    CfrEngine::Config config;
    
    switch (type) {
        case EngineType::HighPerformance:
            config.numThreads = std::thread::hardware_concurrency();
            config.useGpuAcceleration = true;
            config.batchSize = 2000;
            config.maxIterations = 50000;
            break;
            
        case EngineType::LowLatency:
            config.numThreads = std::min(4U, std::thread::hardware_concurrency());
            config.useGpuAcceleration = false;
            config.batchSize = 100;
            config.maxIterations = 1000;
            break;
            
        case EngineType::HighThroughput:
            config.numThreads = std::thread::hardware_concurrency() * 2;
            config.useGpuAcceleration = true;
            config.batchSize = 5000;
            config.maxIterations = 100000;
            break;
            
        case EngineType::Standard:
        default:
            // Configuration par défaut
            break;
    }
    
    return std::make_unique<CfrEngine>(config);
}

// Stubs pour méthodes manquantes
void CfrEngine::initializeThreads() {
    // Implementation des worker threads si nécessaire
}

void CfrEngine::shutdownThreads() {
    // Cleanup threads
}

std::vector<ActionType> CfrEngine::getLegalActions(const GameState& state) const {
    std::vector<ActionType> actions;
    actions.push_back(ActionType::Fold);
    actions.push_back(ActionType::Call);
    actions.push_back(ActionType::Bet);
    if (state.toCall == 0.0) {
        actions.push_back(ActionType::Check);
    }
    return actions;
}

double CfrEngine::calculatePotOdds(const GameState& state) const {
    if (state.toCall <= 0.0) return 1.0;
    return state.potSize / (state.potSize + state.toCall);
}

#ifdef RTPA_CUDA_ENABLED
bool CfrEngine::initializeCuda() {
    // Implementation CUDA si nécessaire
    return false; // Stub pour compilation
}

void CfrEngine::shutdownCuda() {
    // Cleanup CUDA
}

double CfrEngine::trainBatchCuda(const std::vector<GameState>& states) {
    // Implementation CUDA
    return trainBatchMultiThreaded(states); // Fallback
}
#endif