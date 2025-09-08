"""
Gestionnaire de données optimisé pour génération continue
Gestion intelligente de l'espace disque et compactage automatique
"""

import os
import time
import threading
import json
import gzip
import pickle
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import deque
import numpy as np

from .hand_parser import ParsedHand
from ..utils.logger import get_logger

@dataclass
class StorageSettings:
    """Configuration de la gestion du stockage"""
    max_memory_hands: int = 50000  # Mains max en mémoire
    max_disk_size_mb: int = 500   # Taille max sur disque (MB)
    compression_level: int = 6    # Niveau compression gzip
    archive_threshold: int = 100000  # Seuil d'archivage
    cleanup_interval: float = 300.0  # Nettoyage toutes les 5 minutes
    export_format: str = "compressed"  # "json", "pickle", "compressed"
    retention_days: int = 7  # Rétention des archives (jours)

class DataManager:
    """Gestionnaire de données avec compactage et gestion d'espace"""
    
    def __init__(self, storage_settings: Optional[StorageSettings] = None):
        self.logger = get_logger(__name__)
        self.settings = storage_settings or StorageSettings()
        
        # Stockage en mémoire (circulaire)
        self.active_hands = deque(maxlen=self.settings.max_memory_hands)
        self.archived_hands_count = 0
        
        # Données CFR compactées
        self.compressed_cfr_data = {}
        self.cfr_snapshots = deque(maxlen=10)  # 10 snapshots max
        
        # Gestion des fichiers
        self.data_directory = "data"
        self.archive_directory = "data/archives"
        self.temp_directory = "data/temp"
        self._ensure_directories()
        
        # Thread de nettoyage automatique
        self.cleanup_thread = None
        self.cleanup_running = False
        
        # Statistiques de stockage
        self.storage_stats = {
            'memory_usage_mb': 0.0,
            'disk_usage_mb': 0.0,
            'compression_ratio': 0.0,
            'hands_in_memory': 0,
            'hands_archived': 0,
            'last_cleanup': 0.0
        }
        
        self.logger.info("DataManager initialisé avec gestion d'espace optimisée")
    
    def _ensure_directories(self):
        """Crée les répertoires nécessaires"""
        for directory in [self.data_directory, self.archive_directory, self.temp_directory]:
            os.makedirs(directory, exist_ok=True)
    
    def start_cleanup_service(self):
        """Démarre le service de nettoyage automatique"""
        if not self.cleanup_running:
            self.cleanup_running = True
            self.cleanup_thread = threading.Thread(
                target=self._cleanup_loop,
                daemon=True,
                name="DataCleanup"
            )
            self.cleanup_thread.start()
            self.logger.info("Service de nettoyage automatique démarré")
    
    def stop_cleanup_service(self):
        """Arrête le service de nettoyage"""
        self.cleanup_running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=2.0)
        self.logger.info("Service de nettoyage arrêté")
    
    def add_hands(self, hands: List[ParsedHand]) -> bool:
        """Ajoute des mains avec gestion automatique de l'espace"""
        try:
            # Vérification espace disponible
            if not self._check_storage_capacity():
                self.logger.warning("Espace insuffisant, déclenchement nettoyage")
                self._emergency_cleanup()
            
            # Ajout en mémoire
            self.active_hands.extend(hands)
            
            # Archivage automatique si nécessaire
            if len(self.active_hands) >= self.settings.max_memory_hands * 0.8:
                self._archive_oldest_hands()
            
            # Mise à jour statistiques
            self._update_storage_stats()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur ajout mains: {e}")
            return False
    
    def add_cfr_snapshot(self, regret_sum: Dict, strategy_sum: Dict, metadata: Dict):
        """Ajoute un snapshot CFR compressé"""
        try:
            snapshot = {
                'timestamp': time.time(),
                'regret_sum': self._compress_cfr_tables(regret_sum),
                'strategy_sum': self._compress_cfr_tables(strategy_sum),
                'metadata': metadata
            }
            
            self.cfr_snapshots.append(snapshot)
            
        except Exception as e:
            self.logger.error(f"Erreur snapshot CFR: {e}")
    
    def _compress_cfr_tables(self, tables: Dict) -> bytes:
        """Compresse les tables CFR avec optimisation"""
        try:
            # Conversion en format compact
            compact_data = {}
            for info_set, actions in tables.items():
                if actions:  # Seulement les non-vides
                    compact_data[info_set] = dict(actions)
            
            # Sérialisation et compression
            data_bytes = pickle.dumps(compact_data, protocol=pickle.HIGHEST_PROTOCOL)
            compressed = gzip.compress(data_bytes, compresslevel=self.settings.compression_level)
            
            # Calcul ratio compression
            if len(data_bytes) > 0:
                ratio = len(compressed) / len(data_bytes)
                self.storage_stats['compression_ratio'] = ratio
            
            return compressed
            
        except Exception as e:
            self.logger.error(f"Erreur compression CFR: {e}")
            return b''
    
    def _decompress_cfr_tables(self, compressed_data: bytes) -> Dict:
        """Décompresse les tables CFR"""
        try:
            if not compressed_data:
                return {}
            
            decompressed = gzip.decompress(compressed_data)
            return pickle.loads(decompressed)
            
        except Exception as e:
            self.logger.error(f"Erreur décompression CFR: {e}")
            return {}
    
    def _archive_oldest_hands(self):
        """Archive les mains les plus anciennes"""
        try:
            if len(self.active_hands) < 1000:
                return
            
            # Extraction des mains à archiver
            hands_to_archive = []
            archive_count = min(10000, len(self.active_hands) // 2)
            
            for _ in range(archive_count):
                if self.active_hands:
                    hands_to_archive.append(self.active_hands.popleft())
            
            if hands_to_archive:
                # Sauvegarde compressée
                archive_file = self._create_archive_file(hands_to_archive)
                if archive_file:
                    self.archived_hands_count += len(hands_to_archive)
                    self.logger.info(f"Archivé {len(hands_to_archive)} mains dans {archive_file}")
            
        except Exception as e:
            self.logger.error(f"Erreur archivage: {e}")
    
    def _create_archive_file(self, hands: List[ParsedHand]) -> Optional[str]:
        """Crée un fichier d'archive compressé"""
        try:
            timestamp = int(time.time())
            filename = f"hands_archive_{timestamp}.gz"
            filepath = os.path.join(self.archive_directory, filename)
            
            # Conversion en format compact
            compact_hands = []
            for hand in hands:
                compact_hands.append({
                    'actions': hand.actions,
                    'board': hand.board_cards,
                    'hero_cards': hand.hero_cards,
                    'pot': hand.pot_size,
                    'positions': hand.positions
                })
            
            # Sauvegarde compressée
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                json.dump(compact_hands, f, separators=(',', ':'))
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Erreur création archive: {e}")
            return None
    
    def _check_storage_capacity(self) -> bool:
        """Vérifie la capacité de stockage disponible"""
        try:
            # Taille disque utilisée
            total_size = 0
            for root, dirs, files in os.walk(self.data_directory):
                for file in files:
                    filepath = os.path.join(root, file)
                    total_size += os.path.getsize(filepath)
            
            size_mb = total_size / (1024 * 1024)
            self.storage_stats['disk_usage_mb'] = size_mb
            
            # Vérification limite
            return size_mb < self.settings.max_disk_size_mb
            
        except Exception as e:
            self.logger.error(f"Erreur vérification espace: {e}")
            return True  # Par sécurité, autoriser par défaut
    
    def _emergency_cleanup(self):
        """Nettoyage d'urgence en cas d'espace insuffisant"""
        try:
            # Suppression des archives les plus anciennes
            archive_files = []
            for file in os.listdir(self.archive_directory):
                if file.endswith('.gz'):
                    filepath = os.path.join(self.archive_directory, file)
                    mtime = os.path.getmtime(filepath)
                    archive_files.append((filepath, mtime))
            
            # Tri par ancienneté
            archive_files.sort(key=lambda x: x[1])
            
            # Suppression des plus anciens (50%)
            files_to_delete = len(archive_files) // 2
            for filepath, _ in archive_files[:files_to_delete]:
                os.remove(filepath)
                self.logger.info(f"Supprimé archive: {os.path.basename(filepath)}")
            
            # Compactage mémoire
            if len(self.active_hands) > self.settings.max_memory_hands // 2:
                target_size = self.settings.max_memory_hands // 2
                hands_to_remove = len(self.active_hands) - target_size
                for _ in range(hands_to_remove):
                    if self.active_hands:
                        self.active_hands.popleft()
            
        except Exception as e:
            self.logger.error(f"Erreur nettoyage d'urgence: {e}")
    
    def _cleanup_loop(self):
        """Boucle de nettoyage automatique"""
        while self.cleanup_running:
            try:
                # Nettoyage périodique
                self._periodic_cleanup()
                self._update_storage_stats()
                
                # Attente jusqu'au prochain nettoyage
                time.sleep(self.settings.cleanup_interval)
                
            except Exception as e:
                self.logger.error(f"Erreur boucle nettoyage: {e}")
                time.sleep(60)  # Attente en cas d'erreur
    
    def _periodic_cleanup(self):
        """Nettoyage périodique automatique"""
        try:
            current_time = time.time()
            
            # Suppression archives expirées
            retention_seconds = self.settings.retention_days * 24 * 3600
            
            for file in os.listdir(self.archive_directory):
                if file.endswith('.gz'):
                    filepath = os.path.join(self.archive_directory, file)
                    if os.path.getmtime(filepath) < current_time - retention_seconds:
                        os.remove(filepath)
            
            # Archivage automatique si mémoire pleine
            if len(self.active_hands) >= self.settings.max_memory_hands * 0.9:
                self._archive_oldest_hands()
            
            # Vérification espace disque
            if not self._check_storage_capacity():
                self._emergency_cleanup()
            
            self.storage_stats['last_cleanup'] = current_time
            
        except Exception as e:
            self.logger.error(f"Erreur nettoyage périodique: {e}")
    
    def _update_storage_stats(self):
        """Met à jour les statistiques de stockage"""
        try:
            import sys
            
            # Mémoire utilisée
            memory_mb = sys.getsizeof(self.active_hands) / (1024 * 1024)
            self.storage_stats['memory_usage_mb'] = memory_mb
            self.storage_stats['hands_in_memory'] = len(self.active_hands)
            self.storage_stats['hands_archived'] = self.archived_hands_count
            
        except Exception as e:
            self.logger.error(f"Erreur stats: {e}")
    
    def export_database(self, export_path: str, include_archives: bool = False) -> bool:
        """Exporte la base de données complète"""
        try:
            export_data = {
                'timestamp': time.time(),
                'version': '1.0',
                'active_hands': len(self.active_hands),
                'archived_hands': self.archived_hands_count,
                'cfr_snapshots': len(self.cfr_snapshots),
                'storage_stats': self.storage_stats
            }
            
            # Export mains actives
            if self.active_hands:
                hands_data = []
                for hand in list(self.active_hands):
                    hands_data.append({
                        'actions': hand.actions,
                        'board': hand.board_cards,
                        'hero_cards': hand.hero_cards,
                        'pot': hand.pot_size,
                        'positions': hand.positions
                    })
                export_data['hands'] = hands_data
            
            # Export snapshots CFR
            if self.cfr_snapshots:
                cfr_data = []
                for snapshot in list(self.cfr_snapshots):
                    cfr_data.append({
                        'timestamp': snapshot['timestamp'],
                        'metadata': snapshot['metadata'],
                        'regret_compressed': len(snapshot.get('regret_sum', b'')),
                        'strategy_compressed': len(snapshot.get('strategy_sum', b''))
                    })
                export_data['cfr_snapshots_info'] = cfr_data
            
            # Sauvegarde compressée
            with gzip.open(export_path, 'wt', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Base de données exportée: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur export: {e}")
            return False
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques détaillées de stockage"""
        self._update_storage_stats()
        
        stats = self.storage_stats.copy()
        stats.update({
            'active_hands_count': len(self.active_hands),
            'cfr_snapshots_count': len(self.cfr_snapshots),
            'disk_usage_percent': (stats['disk_usage_mb'] / self.settings.max_disk_size_mb) * 100,
            'memory_limit_mb': self.settings.max_memory_hands * 0.001,  # Estimation
            'compression_enabled': True,
            'cleanup_active': self.cleanup_running
        })
        
        return stats
    
    def configure_storage(self, new_settings: Dict[str, Any]):
        """Configure les paramètres de stockage"""
        try:
            for key, value in new_settings.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
                    self.logger.info(f"Paramètre {key} mis à jour: {value}")
            
            # Redémarrage nettoyage si nécessaire
            if 'cleanup_interval' in new_settings and self.cleanup_running:
                self.stop_cleanup_service()
                self.start_cleanup_service()
            
        except Exception as e:
            self.logger.error(f"Erreur configuration: {e}")