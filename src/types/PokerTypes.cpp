/**
 * Implémentation des types poker
 */

#include "PokerTypes.h"
#include <sstream>
#include <algorithm>

namespace rtpa::types {

std::string Card::toString() const {
    std::stringstream ss;
    
    // Rank
    switch (rank) {
        case Rank::Two: ss << "2"; break;
        case Rank::Three: ss << "3"; break;
        case Rank::Four: ss << "4"; break;
        case Rank::Five: ss << "5"; break;
        case Rank::Six: ss << "6"; break;
        case Rank::Seven: ss << "7"; break;
        case Rank::Eight: ss << "8"; break;
        case Rank::Nine: ss << "9"; break;
        case Rank::Ten: ss << "T"; break;
        case Rank::Jack: ss << "J"; break;
        case Rank::Queen: ss << "Q"; break;
        case Rank::King: ss << "K"; break;
        case Rank::Ace: ss << "A"; break;
    }
    
    // Suit
    switch (suit) {
        case Suit::Spades: ss << "♠"; break;
        case Suit::Hearts: ss << "♥"; break;
        case Suit::Diamonds: ss << "♦"; break;
        case Suit::Clubs: ss << "♣"; break;
    }
    
    return ss.str();
}

bool GameState::isValid() const {
    return potSize >= 0.0 && stackSize > 0.0 && numPlayers >= 2;
}

std::string GameState::generateInfoSet() const {
    std::stringstream ss;
    ss << static_cast<int>(bettingRound) << "_";
    ss << static_cast<int>(position) << "_";
    ss << static_cast<int>(potSize / bigBlind) << "_";
    ss << numPlayers;
    return ss.str();
}

std::vector<ActionType> GameState::getLegalActions() const {
    std::vector<ActionType> actions;
    
    actions.push_back(ActionType::Fold);
    
    if (toCall == 0.0) {
        actions.push_back(ActionType::Check);
        actions.push_back(ActionType::Bet);
    } else {
        actions.push_back(ActionType::Call);
        if (stackSize > toCall) {
            actions.push_back(ActionType::Raise);
        }
    }
    
    if (stackSize > 0) {
        actions.push_back(ActionType::AllIn);
    }
    
    return actions;
}

void Strategy::normalize() {
    double total = 0.0;
    for (const auto& [action, prob] : actionProbabilities) {
        total += std::max(prob, 0.0);
    }
    
    if (total > 0.0) {
        for (auto& [action, prob] : actionProbabilities) {
            prob = std::max(prob, 0.0) / total;
        }
    }
}

void Strategy::updateRegret(ActionType action, double regret) {
    actionProbabilities[action] += regret;
    totalRegret += std::abs(regret);
    visitCount++;
}

ActionType Strategy::getBestAction() const {
    auto best = std::max_element(actionProbabilities.begin(), actionProbabilities.end(),
        [](const auto& a, const auto& b) { return a.second < b.second; });
    
    return best != actionProbabilities.end() ? best->first : ActionType::Fold;
}

double Strategy::getActionProbability(ActionType action) const {
    auto it = actionProbabilities.find(action);
    return it != actionProbabilities.end() ? it->second : 0.0;
}

} // namespace rtpa::types