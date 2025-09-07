"""
Base de données en mémoire pour RTPA Studio
Optimisée pour les performances temps réel
"""

import sqlite3
import threading
import time
from typing import Dict, List, Any, Optional
from collections import deque
import json

from ..utils.logger import get_logger

class MemoryDatabase:
    """Base de données en mémoire haute performance"""
    
    def __init__(self, max_history=10000):
        self.logger = get_logger(__name__)
        self.max_history = max_history
        self.lock = threading.RLock()
        
        # Stockage en mémoire
        self.game_states = deque(maxlen=max_history)
        self.recommendations = deque(maxlen=max_history)
        self.hand_history = deque(maxlen=max_history)
        self.statistics = {}
        
        # Index pour recherche rapide
        self.index_by_timestamp = {}
        self.index_by_hand_id = {}
        
        # Base SQLite pour persistance optionnelle
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self._init_tables()
        
        self.logger.info("Base de données mémoire initialisée")
    
    def _init_tables(self):
        """Initialise les tables SQLite"""
        cursor = self.conn.cursor()
        
        # Table des états de jeu
        cursor.execute('''
            CREATE TABLE game_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                table_type TEXT,
                players_count INTEGER,
                hero_position INTEGER,
                hero_cards TEXT,
                board_cards TEXT,
                pot_size REAL,
                hero_stack REAL,
                small_blind REAL,
                big_blind REAL,
                current_bet REAL,
                action_to_hero INTEGER,
                ante REAL,
                tournament_level INTEGER,
                rebuys_available INTEGER,
                data_json TEXT
            )
        ''')
        
        # Table des recommandations
        cursor.execute('''
            CREATE TABLE recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                game_state_id INTEGER,
                action_type TEXT,
                bet_size REAL,
                win_probability REAL,
                expected_value REAL,
                risk_level REAL,
                confidence REAL,
                reasoning TEXT,
                data_json TEXT,
                FOREIGN KEY (game_state_id) REFERENCES game_states (id)
            )
        ''')
        
        # Table des statistiques
        cursor.execute('''
            CREATE TABLE statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                hands_played INTEGER,
                hands_won INTEGER,
                win_rate REAL,
                total_profit REAL,
                hourly_rate REAL,
                bb_per_100 REAL,
                data_json TEXT
            )
        ''')
        
        self.conn.commit()
    
    def store_game_state(self, game_state):
        """Stocke un état de jeu"""
        with self.lock:
            timestamp = time.time()
            
            # Stockage en mémoire
            state_data = {
                'timestamp': timestamp,
                'game_state': game_state,
                'id': len(self.game_states)
            }
            self.game_states.append(state_data)
            self.index_by_timestamp[timestamp] = len(self.game_states) - 1
            
            # Préparation des données pour JSON (sérialisation compatible)
            state_json = {
                'timestamp': timestamp,
                'table_type': game_state.table_type,
                'players_count': game_state.players_count,
                'hero_position': game_state.hero_position,
                'hero_cards': list(game_state.hero_cards),
                'board_cards': list(game_state.board_cards),
                'pot_size': game_state.pot_size,
                'hero_stack': game_state.hero_stack,
                'small_blind': game_state.small_blind,
                'big_blind': game_state.big_blind,
                'current_bet': game_state.current_bet,
                'action_to_hero': game_state.action_to_hero,
                'ante': game_state.ante,
                'tournament_level': game_state.tournament_level,
                'rebuys_available': game_state.rebuys_available
            }
            
            # Stockage SQLite pour persistance
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO game_states (
                    timestamp, table_type, players_count, hero_position,
                    hero_cards, board_cards, pot_size, hero_stack,
                    small_blind, big_blind, current_bet, action_to_hero,
                    ante, tournament_level, rebuys_available, data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, game_state.table_type, game_state.players_count,
                game_state.hero_position, str(game_state.hero_cards),
                str(game_state.board_cards), game_state.pot_size,
                game_state.hero_stack, game_state.small_blind,
                game_state.big_blind, game_state.current_bet,
                int(game_state.action_to_hero), game_state.ante,
                game_state.tournament_level, game_state.rebuys_available,
                json.dumps(state_json)
            ))
            self.conn.commit()
            
            return cursor.lastrowid
    
    def store_recommendation(self, recommendation: Dict[str, Any]):
        """Stocke une recommandation"""
        with self.lock:
            timestamp = time.time()
            
            # Stockage en mémoire
            rec_data = {
                'timestamp': timestamp,
                'recommendation': recommendation
            }
            self.recommendations.append(rec_data)
            
            # Stockage SQLite
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO recommendations (
                    timestamp, action_type, bet_size, win_probability,
                    expected_value, risk_level, confidence, reasoning, data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                recommendation.get('action_type', ''),
                recommendation.get('bet_size', 0.0),
                recommendation.get('win_probability', 0.0),
                recommendation.get('expected_value', 0.0),
                recommendation.get('risk_level', 0.0),
                recommendation.get('confidence', 0.0),
                recommendation.get('reasoning', ''),
                json.dumps(recommendation)
            ))
            self.conn.commit()
    
    def get_latest_recommendation(self) -> Optional[Dict[str, Any]]:
        """Retourne la dernière recommandation"""
        with self.lock:
            if self.recommendations:
                return self.recommendations[-1]['recommendation']
            return None
    
    def get_latest_game_state(self):
        """Retourne le dernier état de jeu"""
        with self.lock:
            if self.game_states:
                return self.game_states[-1]['game_state']
            return None
    
    def get_history(self, limit=100) -> List[Dict[str, Any]]:
        """Retourne l'historique récent"""
        with self.lock:
            history = []
            for i, state_data in enumerate(list(self.game_states)[-limit:]):
                rec_data = None
                if i < len(self.recommendations):
                    rec_data = self.recommendations[i]
                
                history.append({
                    'game_state': state_data,
                    'recommendation': rec_data
                })
            
            return history
    
    def update_statistics(self, stats: Dict[str, Any]):
        """Met à jour les statistiques"""
        with self.lock:
            self.statistics.update(stats)
            
            # Stockage SQLite
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO statistics (
                    timestamp, hands_played, hands_won, win_rate,
                    total_profit, hourly_rate, bb_per_100, data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                time.time(),
                stats.get('hands_played', 0),
                stats.get('hands_won', 0),
                stats.get('win_rate', 0.0),
                stats.get('total_profit', 0.0),
                stats.get('hourly_rate', 0.0),
                stats.get('bb_per_100', 0.0),
                json.dumps(stats)
            ))
            self.conn.commit()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques actuelles"""
        with self.lock:
            return self.statistics.copy()
    
    def clear_history(self):
        """Efface l'historique"""
        with self.lock:
            self.game_states.clear()
            self.recommendations.clear()
            self.hand_history.clear()
            self.index_by_timestamp.clear()
            self.index_by_hand_id.clear()
            
            # Effacement SQLite
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM game_states')
            cursor.execute('DELETE FROM recommendations')
            cursor.execute('DELETE FROM statistics')
            self.conn.commit()
            
            self.logger.info("Historique effacé")
    
    def export_data(self, filename: str):
        """Exporte les données vers un fichier"""
        with self.lock:
            export_data = {
                'game_states': [state for state in self.game_states],
                'recommendations': [rec for rec in self.recommendations],
                'statistics': self.statistics,
                'export_timestamp': time.time()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Données exportées vers {filename}")
    
    def close(self):
        """Ferme la base de données"""
        self.conn.close()
        self.logger.info("Base de données fermée")