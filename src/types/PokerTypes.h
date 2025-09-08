/**
 * Types fondamentaux pour le poker
 * Structures C++20 optimisées pour performance maximale
 */

#pragma once

#include <array>
#include <vector>
#include <string>
#include <unordered_map>
#include <memory>
#include <cstdint>

namespace rtpa::types {

// Énumérations de base
enum class Suit : uint8_t { Spades = 0, Hearts = 1, Diamonds = 2, Clubs = 3 };
enum class Rank : uint8_t { Two = 2, Three, Four, Five, Six, Seven, Eight, Nine, Ten, Jack, Queen, King, Ace };

enum class BettingRound : uint8_t { 
    Preflop = 0, 
    Flop = 1, 
    Turn = 2, 
    River = 3 
};

enum class ActionType : uint8_t {
    Fold = 0,
    Check = 1,
    Call = 2,
    Bet = 3,
    Raise = 4,
    AllIn = 5
};

enum class Position : uint8_t {
    SmallBlind = 0,
    BigBlind = 1,
    UnderTheGun = 2,
    MiddlePosition = 3,
    Cutoff = 4,
    Button = 5
};

// Structure carte optimisée
struct Card {
    Rank rank;
    Suit suit;
    
    constexpr Card() : rank(Rank::Two), suit(Suit::Spades) {}
    constexpr Card(Rank r, Suit s) : rank(r), suit(s) {}
    
    // Hash pour utilisation dans containers
    constexpr uint8_t hash() const noexcept {
        return static_cast<uint8_t>(rank) * 4 + static_cast<uint8_t>(suit);
    }
    
    // Comparaisons
    constexpr bool operator==(const Card& other) const noexcept {
        return rank == other.rank && suit == other.suit;
    }
    
    // String representation
    std::string toString() const;
};

// Action de poker
struct Action {
    ActionType type;
    double amount;
    uint64_t timestamp;
    
    Action(ActionType t, double a = 0.0) 
        : type(t), amount(a), timestamp(0) {}
};

// État de main de poker
struct GameState {
    // Cartes
    std::array<Card, 2> holeCards;
    std::vector<Card> communityCards;
    
    // État de la table
    double potSize = 0.0;
    double stackSize = 0.0;
    double bigBlind = 2.0;
    double smallBlind = 1.0;
    
    // Position et joueurs
    Position position = Position::Button;
    uint8_t numPlayers = 6;
    uint8_t numActivePlayers = 6;
    
    // Round de mise
    BettingRound bettingRound = BettingRound::Preflop;
    
    // Historique des actions
    std::vector<Action> actionHistory;
    
    // État calculé
    double toCall = 0.0;
    double minRaise = 0.0;
    double maxBet = 0.0;
    
    // Validité de l'état
    bool isValid() const;
    
    // Génération d'information set pour CFR
    std::string generateInfoSet() const;
    
    // Actions légales disponibles
    std::vector<ActionType> getLegalActions() const;
};

// Stratégie CFR
struct Strategy {
    std::unordered_map<ActionType, double> actionProbabilities;
    double totalRegret = 0.0;
    uint64_t visitCount = 0;
    
    // Normalisation de la stratégie
    void normalize();
    
    // Mise à jour des regrets
    void updateRegret(ActionType action, double regret);
    
    // Obtenir meilleure action
    ActionType getBestAction() const;
    
    // Probabilité d'action
    double getActionProbability(ActionType action) const;
};

// Information set pour CFR
struct InfoSet {
    std::string key;
    Strategy strategy;
    double averageStrategySum = 0.0;
    
    InfoSet(const std::string& k) : key(k) {}
};

// Résultat de simulation Monte Carlo
struct SimulationResult {
    double winProbability = 0.0;
    double tieProbability = 0.0;
    double expectedValue = 0.0;
    uint32_t simulations = 0;
    
    // Statistiques détaillées
    std::array<double, 10> handRankDistribution = {0.0}; // Probabilités par force de main
    
    bool isValid() const { return simulations > 0; }
};

// Configuration OCR
struct OCRConfig {
    // Zones de capture écran
    struct CaptureZone {
        int x, y, width, height;
        std::string name;
        
        CaptureZone(int x_, int y_, int w, int h, const std::string& n)
            : x(x_), y(y_), width(w), height(h), name(n) {}
    };
    
    std::vector<CaptureZone> zones;
    
    // Paramètres Tesseract
    std::string tesseractLanguage = "eng";
    int ocrEngineMode = 3; // Default, based on what is available
    int pageSegmentationMode = 8; // Single word
    
    // Preprocessing OpenCV
    bool useGaussianBlur = true;
    double blurKernelSize = 1.5;
    bool useBinaryThreshold = true;
    int binaryThresholdValue = 128;
    
    // Calibration automatique
    bool autoCalibrationEnabled = true;
    std::string targetPlatform = "auto"; // "pokerstars", "winamax", "pmu", etc.
};

// Statistiques de performance
struct PerformanceStats {
    // CFR Engine
    uint64_t totalIterations = 0;
    double averageConvergence = 0.0;
    uint64_t totalInfoSets = 0;
    
    // Simulations Monte Carlo
    uint64_t totalSimulations = 0;
    double averageSimulationTime = 0.0; // en milliseconds
    
    // OCR
    uint64_t totalOCROperations = 0;
    double averageOCRTime = 0.0;
    double ocrAccuracy = 0.0;
    
    // Performance système
    double cpuUsage = 0.0;
    double memoryUsage = 0.0;
    double gpuUsage = 0.0; // Si CUDA disponible
    
    // Timing global
    uint64_t uptimeSeconds = 0;
    uint64_t handsAnalyzed = 0;
};

} // namespace rtpa::types

// Spécialisations de hash pour std::unordered_map
namespace std {
    template<>
    struct hash<rtpa::types::Card> {
        constexpr std::size_t operator()(const rtpa::types::Card& card) const noexcept {
            return card.hash();
        }
    };
    
    template<>
    struct hash<rtpa::types::ActionType> {
        constexpr std::size_t operator()(const rtpa::types::ActionType& action) const noexcept {
            return static_cast<std::size_t>(action);
        }
    };
}