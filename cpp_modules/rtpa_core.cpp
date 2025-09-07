/*
 * RTPA Studio - Module C++ Core
 * Optimisations hautes performances pour calculs CFR/Nash et OCR
 */

#include <Python.h>
#include <vector>
#include <unordered_map>
#include <random>
#include <chrono>
#include <algorithm>
#include <cmath>
#include <string>

// Structure pour état de jeu optimisé
struct GameState {
    int street;
    int hero_cards[2];
    int board_cards[5];
    double pot_size;
    double hero_stack;
    int position;
    int num_players;
    double current_bet;
    bool action_to_hero;
    std::string table_type;
};

// Structure pour recommandation
struct Recommendation {
    std::string action_type;
    double bet_size;
    double win_probability;
    double expected_value;
    double risk_level;
    double confidence;
    std::string reasoning;
};

// Classe CFR optimisée
class OptimizedCFR {
private:
    std::unordered_map<std::string, std::unordered_map<std::string, double>> regret_sum;
    std::unordered_map<std::string, std::unordered_map<std::string, double>> strategy_sum;
    std::mt19937 rng;
    
public:
    OptimizedCFR() : rng(std::chrono::steady_clock::now().time_since_epoch().count()) {}
    
    // Calcul rapide d'équité Monte Carlo
    double calculate_equity(const std::vector<int>& hero_cards, 
                          const std::vector<int>& board_cards,
                          int num_opponents = 1,
                          int simulations = 10000) {
        
        int wins = 0;
        std::vector<int> deck;
        
        // Création du deck (52 cartes - cartes connues)
        for (int i = 0; i < 52; i++) {
            bool used = false;
            for (int card : hero_cards) {
                if (card == i) { used = true; break; }
            }
            for (int card : board_cards) {
                if (card == i) { used = true; break; }
            }
            if (!used) deck.push_back(i);
        }
        
        // Simulations Monte Carlo
        for (int sim = 0; sim < simulations; sim++) {
            std::shuffle(deck.begin(), deck.end(), rng);
            
            // Complétion du board si nécessaire
            std::vector<int> full_board = board_cards;
            int board_index = 0;
            while (full_board.size() < 5) {
                full_board.push_back(deck[board_index++]);
            }
            
            // Distribution des cartes adverses
            std::vector<std::vector<int>> opponent_hands(num_opponents);
            for (int opp = 0; opp < num_opponents; opp++) {
                opponent_hands[opp] = {deck[board_index], deck[board_index + 1]};
                board_index += 2;
            }
            
            // Évaluation des mains
            int hero_strength = evaluate_hand(hero_cards, full_board);
            bool wins_hand = true;
            
            for (const auto& opp_hand : opponent_hands) {
                int opp_strength = evaluate_hand(opp_hand, full_board);
                if (opp_strength >= hero_strength) {
                    wins_hand = false;
                    break;
                }
            }
            
            if (wins_hand) wins++;
        }
        
        return static_cast<double>(wins) / simulations;
    }
    
    // Évaluation rapide de main (simplifiée)
    int evaluate_hand(const std::vector<int>& hand_cards, const std::vector<int>& board_cards) {
        std::vector<int> all_cards = hand_cards;
        all_cards.insert(all_cards.end(), board_cards.begin(), board_cards.end());
        
        // Conversion en rangs et couleurs
        std::vector<int> ranks(all_cards.size());
        std::vector<int> suits(all_cards.size());
        
        for (size_t i = 0; i < all_cards.size(); i++) {
            ranks[i] = all_cards[i] % 13;
            suits[i] = all_cards[i] / 13;
        }
        
        // Comptage des rangs
        std::vector<int> rank_counts(13, 0);
        for (int rank : ranks) {
            rank_counts[rank]++;
        }
        
        // Recherche de combinaisons (simplifiée)
        std::sort(rank_counts.rbegin(), rank_counts.rend());
        
        if (rank_counts[0] == 4) return 7000; // Carré
        if (rank_counts[0] == 3 && rank_counts[1] == 2) return 6000; // Full
        if (rank_counts[0] == 3) return 3000; // Brelan
        if (rank_counts[0] == 2 && rank_counts[1] == 2) return 2000; // Double paire
        if (rank_counts[0] == 2) return 1000; // Paire
        
        // Carte haute
        std::sort(ranks.rbegin(), ranks.rend());
        return ranks[0] * 10 + ranks[1];
    }
    
    // Calcul CFR optimisé
    Recommendation get_recommendation(const GameState& state) {
        Recommendation rec;
        
        // Conversion cartes
        std::vector<int> hero_cards = {state.hero_cards[0], state.hero_cards[1]};
        std::vector<int> board_cards;
        for (int i = 0; i < 5 && state.board_cards[i] != -1; i++) {
            board_cards.push_back(state.board_cards[i]);
        }
        
        // Calcul d'équité
        double equity = calculate_equity(hero_cards, board_cards, state.num_players - 1);
        
        // Logique de décision simplifiée mais rapide
        if (equity > 0.7) {
            rec.action_type = "bet_large";
            rec.bet_size = state.pot_size * 0.75;
            rec.risk_level = 40.0;
        } else if (equity > 0.5) {
            rec.action_type = "bet_medium";
            rec.bet_size = state.pot_size * 0.5;
            rec.risk_level = 50.0;
        } else if (equity > 0.3) {
            if (state.current_bet == 0) {
                rec.action_type = "check";
                rec.bet_size = 0.0;
            } else {
                rec.action_type = "call";
                rec.bet_size = state.current_bet;
            }
            rec.risk_level = 60.0;
        } else {
            rec.action_type = "fold";
            rec.bet_size = 0.0;
            rec.risk_level = 0.0;
        }
        
        rec.win_probability = equity * 100.0;
        rec.expected_value = equity * state.pot_size - (1.0 - equity) * rec.bet_size;
        rec.confidence = std::min(95.0, 50.0 + equity * 50.0);
        rec.reasoning = "Analyse C++ optimisée";
        
        return rec;
    }
};

// Variables globales
static OptimizedCFR* cfr_engine = nullptr;

// Fonctions Python-C++
extern "C" {
    
    // Initialisation du moteur CFR
    static PyObject* init_cfr_engine(PyObject* self, PyObject* args) {
        if (cfr_engine) delete cfr_engine;
        cfr_engine = new OptimizedCFR();
        Py_RETURN_NONE;
    }
    
    // Calcul d'équité rapide
    static PyObject* calculate_equity_fast(PyObject* self, PyObject* args) {
        PyObject* hero_cards_list;
        PyObject* board_cards_list;
        int num_opponents = 1;
        int simulations = 10000;
        
        if (!PyArg_ParseTuple(args, "OO|ii", &hero_cards_list, &board_cards_list, 
                             &num_opponents, &simulations)) {
            return NULL;
        }
        
        // Conversion des listes Python en vecteurs C++
        std::vector<int> hero_cards;
        std::vector<int> board_cards;
        
        // Traitement des cartes héros
        if (PyList_Check(hero_cards_list)) {
            for (Py_ssize_t i = 0; i < PyList_Size(hero_cards_list); i++) {
                PyObject* item = PyList_GetItem(hero_cards_list, i);
                if (PyLong_Check(item)) {
                    hero_cards.push_back(PyLong_AsLong(item));
                }
            }
        }
        
        // Traitement des cartes board
        if (PyList_Check(board_cards_list)) {
            for (Py_ssize_t i = 0; i < PyList_Size(board_cards_list); i++) {
                PyObject* item = PyList_GetItem(board_cards_list, i);
                if (PyLong_Check(item)) {
                    board_cards.push_back(PyLong_AsLong(item));
                }
            }
        }
        
        // Calcul
        if (!cfr_engine) cfr_engine = new OptimizedCFR();
        double equity = cfr_engine->calculate_equity(hero_cards, board_cards, 
                                                   num_opponents, simulations);
        
        return PyFloat_FromDouble(equity);
    }
    
    // Recommandation rapide
    static PyObject* get_recommendation_fast(PyObject* self, PyObject* args) {
        // Paramètres
        int street, hero_card1, hero_card2, position, num_players;
        double pot_size, hero_stack, current_bet;
        PyObject* board_cards_list;
        const char* table_type;
        int action_to_hero;
        
        if (!PyArg_ParseTuple(args, "iiiidddOsi", &street, &hero_card1, &hero_card2,
                             &position, &num_players, &pot_size, &hero_stack, 
                             &current_bet, &board_cards_list, &table_type, &action_to_hero)) {
            return NULL;
        }
        
        // Construction de l'état
        GameState state;
        state.street = street;
        state.hero_cards[0] = hero_card1;
        state.hero_cards[1] = hero_card2;
        state.position = position;
        state.num_players = num_players;
        state.pot_size = pot_size;
        state.hero_stack = hero_stack;
        state.current_bet = current_bet;
        state.action_to_hero = action_to_hero == 1;
        state.table_type = std::string(table_type);
        
        // Board cards
        for (int i = 0; i < 5; i++) state.board_cards[i] = -1;
        
        if (PyList_Check(board_cards_list)) {
            for (Py_ssize_t i = 0; i < PyList_Size(board_cards_list) && i < 5; i++) {
                PyObject* item = PyList_GetItem(board_cards_list, i);
                if (PyLong_Check(item)) {
                    state.board_cards[i] = PyLong_AsLong(item);
                }
            }
        }
        
        // Calcul de la recommandation
        if (!cfr_engine) cfr_engine = new OptimizedCFR();
        Recommendation rec = cfr_engine->get_recommendation(state);
        
        // Création du dictionnaire de retour
        PyObject* dict = PyDict_New();
        PyDict_SetItemString(dict, "action_type", PyUnicode_FromString(rec.action_type.c_str()));
        PyDict_SetItemString(dict, "bet_size", PyFloat_FromDouble(rec.bet_size));
        PyDict_SetItemString(dict, "win_probability", PyFloat_FromDouble(rec.win_probability));
        PyDict_SetItemString(dict, "expected_value", PyFloat_FromDouble(rec.expected_value));
        PyDict_SetItemString(dict, "risk_level", PyFloat_FromDouble(rec.risk_level));
        PyDict_SetItemString(dict, "confidence", PyFloat_FromDouble(rec.confidence));
        PyDict_SetItemString(dict, "reasoning", PyUnicode_FromString(rec.reasoning.c_str()));
        
        return dict;
    }
    
    // Nettoyage
    static PyObject* cleanup_cfr(PyObject* self, PyObject* args) {
        if (cfr_engine) {
            delete cfr_engine;
            cfr_engine = nullptr;
        }
        Py_RETURN_NONE;
    }
    
    // Table des méthodes
    static PyMethodDef RTPAMethods[] = {
        {"init_cfr_engine", init_cfr_engine, METH_VARARGS, "Initialise le moteur CFR C++"},
        {"calculate_equity_fast", calculate_equity_fast, METH_VARARGS, "Calcul d'équité rapide"},
        {"get_recommendation_fast", get_recommendation_fast, METH_VARARGS, "Recommandation rapide"},
        {"cleanup_cfr", cleanup_cfr, METH_VARARGS, "Nettoyage du moteur CFR"},
        {NULL, NULL, 0, NULL}
    };
    
    // Définition du module
    static struct PyModuleDef rtpamodule = {
        PyModuleDef_HEAD_INIT,
        "rtpa_core",
        "Module C++ optimisé pour RTPA Studio",
        -1,
        RTPAMethods
    };
    
    // Initialisation du module
    PyMODINIT_FUNC PyInit_rtpa_core(void) {
        return PyModule_Create(&rtpamodule);
    }
}

// Fonction de test pour compilation
int main() {
    OptimizedCFR cfr;
    std::vector<int> hero = {12, 25}; // As de pique, Roi de coeur
    std::vector<int> board = {11, 24, 6}; // Dame de pique, Roi de trèfle, 7 de pique
    
    double equity = cfr.calculate_equity(hero, board, 1, 1000);
    printf("Équité calculée: %.2f%%\\n", equity * 100);
    
    return 0;
}
