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
            
            # Protection contre données corrompues
            if game_state.hero_cards is None:
                game_state.hero_cards = ("", "")
            if game_state.board_cards is None:
                game_state.board_cards = []
            
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
    
    def store_recommendation(self, recommendation: Dict[str, Any], game_state=None):
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
    
    def export_complete_data(self, filename: str, cfr_engine=None):
        """Exporte toutes les données incluant CFR et Nash"""
        with self.lock:
            export_data = {
                'metadata': {
                    'version': '1.0',
                    'export_timestamp': time.time(),
                    'rtpa_version': 'RTPA Studio v1.0'
                },
                'game_data': {
                    'game_states': [state for state in self.game_states],
                    'recommendations': [rec for rec in self.recommendations],
                    'statistics': self.statistics
                },
                'cfr_data': {},
                'settings': {}
            }
            
            # Export des données CFR si moteur fourni
            if cfr_engine:
                try:
                    export_data['cfr_data'] = {
                        'regret_sum': dict(cfr_engine.regret_sum),
                        'strategy_sum': dict(cfr_engine.strategy_sum),
                        'iterations_count': getattr(cfr_engine, 'iterations_count', 0),
                        'total_training_time': getattr(cfr_engine, 'total_training_time', 0.0)
                    }
                    self.logger.info("Données CFR ajoutées à l'export")
                except Exception as e:
                    self.logger.warning(f"Impossible d'exporter les données CFR: {e}")
            
            # Export SQLite complet
            try:
                cursor = self.conn.cursor()
                
                # Toutes les tables
                tables_data = {}
                for table_name in ['game_states', 'recommendations', 'statistics']:
                    cursor.execute(f'SELECT * FROM {table_name}')
                    rows = cursor.fetchall()
                    cursor.execute(f'PRAGMA table_info({table_name})')
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    tables_data[table_name] = {
                        'columns': columns,
                        'rows': rows
                    }
                
                export_data['sql_backup'] = tables_data
                self.logger.info("Sauvegarde SQL ajoutée à l'export")
                
            except Exception as e:
                self.logger.warning(f"Erreur export SQL: {e}")
            
            # Écriture du fichier
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
                
                self.logger.info(f"Export complet réussi vers {filename}")
                return True
                
            except Exception as e:
                self.logger.error(f"Erreur écriture fichier: {e}")
                return False
    
    def import_complete_data(self, filename: str, cfr_engine=None):
        """Importe toutes les données incluant CFR et Nash"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            with self.lock:
                # Vérification version
                if 'metadata' not in import_data:
                    self.logger.warning("Fichier d'import ancien format")
                    return self._import_legacy_format(import_data, cfr_engine)
                
                # Import des données de jeu
                if 'game_data' in import_data:
                    game_data = import_data['game_data']
                    
                    # Clear et import game states
                    self.game_states.clear()
                    for state_data in game_data.get('game_states', []):
                        self.game_states.append(state_data)
                    
                    # Clear et import recommendations
                    self.recommendations.clear()
                    for rec_data in game_data.get('recommendations', []):
                        self.recommendations.append(rec_data)
                    
                    # Import statistics
                    if 'statistics' in game_data:
                        self.statistics.update(game_data['statistics'])
                    
                    self.logger.info("Données de jeu importées")
                
                # Import des données CFR
                if 'cfr_data' in import_data and cfr_engine:
                    try:
                        cfr_data = import_data['cfr_data']
                        
                        # Restauration regret_sum et strategy_sum
                        if 'regret_sum' in cfr_data:
                            cfr_engine.regret_sum.clear()
                            for info_set, actions in cfr_data['regret_sum'].items():
                                cfr_engine.regret_sum[info_set].update(actions)
                        
                        if 'strategy_sum' in cfr_data:
                            cfr_engine.strategy_sum.clear()
                            for info_set, actions in cfr_data['strategy_sum'].items():
                                cfr_engine.strategy_sum[info_set].update(actions)
                        
                        # Restauration métadonnées CFR
                        if hasattr(cfr_engine, 'iterations_count'):
                            cfr_engine.iterations_count = cfr_data.get('iterations_count', 0)
                        if hasattr(cfr_engine, 'total_training_time'):
                            cfr_engine.total_training_time = cfr_data.get('total_training_time', 0.0)
                        
                        self.logger.info("Données CFR restaurées avec succès")
                        
                    except Exception as e:
                        self.logger.error(f"Erreur import CFR: {e}")
                
                # Reconstruction des index
                self._rebuild_indexes()
                
                self.logger.info(f"Import complet réussi depuis {filename}")
                return True
                
        except Exception as e:
            self.logger.error(f"Erreur import fichier {filename}: {e}")
            return False
    
    def _import_legacy_format(self, data, cfr_engine):
        """Import ancien format pour compatibilité"""
        try:
            # Ancien format direct
            if 'game_states' in data:
                self.game_states.clear()
                for state_data in data['game_states']:
                    self.game_states.append(state_data)
            
            if 'recommendations' in data:
                self.recommendations.clear()
                for rec_data in data['recommendations']:
                    self.recommendations.append(rec_data)
            
            if 'statistics' in data:
                self.statistics.update(data['statistics'])
            
            self._rebuild_indexes()
            self.logger.info("Import legacy réussi")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur import legacy: {e}")
            return False
    
    def _rebuild_indexes(self):
        """Reconstruit les index après import"""
        self.index_by_timestamp.clear()
        self.index_by_hand_id.clear()
        
        for i, state_data in enumerate(self.game_states):
            if 'timestamp' in state_data:
                self.index_by_timestamp[state_data['timestamp']] = i
    
    def export_data(self, filename: str):
        """Exporte les données vers un fichier (legacy)"""
        return self.export_complete_data(filename)
    
    def close(self):
        """Ferme la base de données"""
        self.conn.close()
        self.logger.info("Base de données fermée")