"""
Système de capture d'écran et OCR non-intrusif pour RTPA Studio
"""

import cv2
import numpy as np
import pytesseract
import time
from typing import Dict, Any, Optional, Tuple, List
import threading
import psutil
import mss
import re
from PIL import Image
import platform

from ..utils.logger import get_logger

class ScreenCapture:
    """Gestionnaire de capture d'écran et OCR optimisé pour Windows"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Gestion thread-safe pour Windows MSS
        self.sct = None
        self.sct_lock = threading.Lock()
        self.is_windows = platform.system() == 'Windows'
        
        # Initialiser MSS de manière thread-safe
        self._init_screen_capture()
        
        # Configuration OCR avancée - optimisée avec les meilleures pratiques PokerGPT
        self.tesseract_configs = {
            'cards': r'--oem 3 --psm 8 -c tessedit_char_whitelist=AKQJT98765432shdc',
            'numbers': r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789$.,k',
            'pot': r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789$.,k ',
            'buttons': r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-',
            'default': r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789AKQJ$.,/'
        }
        self.tesseract_config = self.tesseract_configs['default']
        
        # Cache d'images pour éviter re-calculs OCR (inspiration PokerGPT)
        self.image_cache = {}
        self.cache_timeout = 0.5  # Secondes
        
        # Zones d'intérêt adaptatives pour différents clients poker
        self.roi_presets = {
            'pokerstars': {
                'hero_cards': {'top': 580, 'left': 440, 'width': 140, 'height': 50},
                'board_cards': {'top': 280, 'left': 350, 'width': 320, 'height': 60},
                'pot_size': {'top': 220, 'left': 450, 'width': 120, 'height': 30},
                'hero_stack': {'top': 650, 'left': 420, 'width': 100, 'height': 25},
                'blinds': {'top': 180, 'left': 400, 'width': 150, 'height': 30},
                'action_buttons': {'top': 600, 'left': 600, 'width': 300, 'height': 80}
            },
            'winamax': {
                'hero_cards': {'top': 590, 'left': 460, 'width': 130, 'height': 45},
                'board_cards': {'top': 290, 'left': 370, 'width': 300, 'height': 55},
                'pot_size': {'top': 230, 'left': 470, 'width': 110, 'height': 28},
                'hero_stack': {'top': 660, 'left': 440, 'width': 90, 'height': 23},
                'blinds': {'top': 190, 'left': 420, 'width': 140, 'height': 28},
                'action_buttons': {'top': 610, 'left': 620, 'width': 280, 'height': 75}
            },
            'pmu': {
                'hero_cards': {'top': 575, 'left': 450, 'width': 135, 'height': 48},
                'board_cards': {'top': 275, 'left': 360, 'width': 310, 'height': 58},
                'pot_size': {'top': 215, 'left': 460, 'width': 115, 'height': 32},
                'hero_stack': {'top': 645, 'left': 430, 'width': 95, 'height': 26},
                'blinds': {'top': 175, 'left': 410, 'width': 145, 'height': 32},
                'action_buttons': {'top': 595, 'left': 610, 'width': 290, 'height': 78}
            }
        }
        self.current_client = 'pokerstars'  # Client par défaut
        self.roi_zones = self.roi_presets[self.current_client]
        
        # Cache des dernières captures
        self.last_capture = None
        self.last_analysis = None
        self.capture_lock = threading.Lock()
        
        print("✅ VRAIE CAPTURE D'ÉCRAN ACTIVÉE - Lecture OCR en temps réel")
        self.logger.info("ScreenCapture initialisé - Mode capture réelle")
    
    def _init_screen_capture(self):
        """Initialise la capture d'écran de manière thread-safe"""
        try:
            with self.sct_lock:
                if self.sct is None:
                    if self.is_windows:
                        # Configuration spéciale pour Windows
                        self.sct = mss.mss()
                        print("🔧 MSS initialisé pour Windows")
                    else:
                        self.sct = mss.mss()
                        print("🔧 MSS initialisé")
        except Exception as e:
            self.logger.error(f"Erreur initialisation MSS: {e}")
            raise
    
    def _get_screen_capture_instance(self):
        """Obtient une instance thread-safe de MSS"""
        if self.is_windows:
            # Sur Windows, créer une nouvelle instance MSS pour chaque thread si nécessaire
            try:
                if self.sct is None:
                    with self.sct_lock:
                        if self.sct is None:
                            self.sct = mss.mss()
                return self.sct
            except Exception as e:
                # En cas d'erreur thread-local, créer une nouvelle instance
                try:
                    return mss.mss()
                except Exception as e2:
                    self.logger.error(f"Erreur création instance MSS: {e2}")
                    raise
        else:
            return self.sct
    
    def capture_screen_region(self, region: Optional[Dict[str, int]] = None) -> Optional[np.ndarray]:
        """Capture une région spécifique de l'écran (thread-safe)"""
        try:
            if region is None:
                # Capture écran complet - détection auto résolution
                region = self._get_screen_region()
            
            # Obtenir instance MSS thread-safe
            sct_instance = self._get_screen_capture_instance()
            
            # Validation de l'instance MSS
            if sct_instance is None:
                self.logger.error("Instance MSS non disponible")
                return None
            
            # Capture avec gestion d'erreur Windows
            screenshot = sct_instance.grab(region)
            img = np.array(screenshot)
            
            # Conversion BGR (pour OpenCV)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img
            
        except Exception as e:
            self.logger.error(f"Erreur capture écran: {e}")
            
            # Sur Windows, tenter récupération avec nouvelle instance MSS
            if self.is_windows and ("'_thread._local'" in str(e) or "srcdc" in str(e)):
                try:
                    self.logger.info("Tentative récupération MSS Windows pour erreur thread-local...")
                    new_sct = mss.mss()
                    
                    # Validation de la région avant grab
                    if region is None:
                        region = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
                        
                    screenshot = new_sct.grab(region)
                    img = np.array(screenshot)
                    
                    # Conversion BGR si nécessaire
                    if len(img.shape) == 3 and img.shape[2] == 4:
                        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    
                    # Remplacer l'instance défaillante
                    with self.sct_lock:
                        self.sct = new_sct
                        
                    print("✅ Récupération MSS réussie (thread-local)")
                    return img
                except Exception as e2:
                    self.logger.error(f"Échec récupération MSS: {e2}")
            
            return None
    
    def _get_screen_region(self) -> Dict[str, int]:
        """Détecte automatiquement la résolution d'écran"""
        try:
            sct_instance = self._get_screen_capture_instance()
            
            # Validation de l'instance MSS
            if sct_instance is None:
                self.logger.warning("Instance MSS non disponible, utilisation résolution par défaut")
                return {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
                
            monitors = sct_instance.monitors
            
            if len(monitors) > 1:
                # Utiliser le premier écran (index 1, 0 = tous les écrans)
                monitor = monitors[1]
                return {
                    'top': monitor['top'],
                    'left': monitor['left'], 
                    'width': monitor['width'],
                    'height': monitor['height']
                }
            else:
                # Fallback résolution standard
                return {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
                
        except Exception as e:
            self.logger.error(f"Erreur détection résolution: {e}")
            return {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
    
    def auto_detect_poker_client(self, img: np.ndarray) -> str:
        """Détecte automatiquement le client poker utilisé"""
        try:
            # Recherche de patterns spécifiques aux clients
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # PokerStars - recherche du logo ou pattern spécifique
            if self._detect_pattern(gray, "PokerStars") or self._detect_pattern(gray, "Stars"):
                return 'pokerstars'
            
            # Winamax - recherche du logo ou couleurs spécifiques
            elif self._detect_pattern(gray, "Winamax") or self._detect_pattern(gray, "Max"):
                return 'winamax'
            
            # PMU - recherche du logo
            elif self._detect_pattern(gray, "PMU") or self._detect_pattern(gray, "pmu"):
                return 'pmu'
            
            # Par défaut, utiliser PokerStars
            return 'pokerstars'
            
        except Exception as e:
            self.logger.warning(f"Erreur détection client: {e}")
            return 'pokerstars'
    
    def set_poker_client(self, client: str):
        """Configure les zones ROI pour un client poker spécifique"""
        if client in self.roi_presets:
            self.current_client = client
            self.roi_zones = self.roi_presets[client]
            self.logger.info(f"Client poker configuré: {client}")
        else:
            self.logger.warning(f"Client poker non supporté: {client}")
    
    def preprocess_image_advanced(self, img: np.ndarray, zone_type: str = 'default') -> np.ndarray:
        """Préprocessing de l'image pour améliorer l'OCR (optimisé avec techniques PokerGPT)"""
        try:
            # Conversion en niveaux de gris
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Amélioration du contraste
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Débruitage adaptatif selon zone (inspiration PokerGPT)
            if zone_type == 'cards':
                # Pour les cartes, débruitage léger pour préserver les détails
                denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
            else:
                # Pour le reste, débruitage standard
                denoised = cv2.medianBlur(enhanced, 3)
            
            # Seuillage adaptatif selon le type de zone
            if zone_type in ['cards', 'blinds']:
                # Pour les cartes et blinds, seuillage plus agressif
                thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            elif zone_type == 'buttons':
                # Pour les boutons, seuillage plus conservateur
                thresh = cv2.threshold(denoised, 127, 255, cv2.THRESH_BINARY)[1]
            else:
                # Seuillage adaptatif pour le reste
                thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                             cv2.THRESH_BINARY, 11, 2)
            
            # Redimensionnement pour améliorer l'OCR (optimisé selon zone)
            scale_factor = 3 if zone_type == 'cards' else 2
            resized = cv2.resize(thresh, None, fx=scale_factor, fy=scale_factor, 
                               interpolation=cv2.INTER_CUBIC)
            
            return resized
            
        except Exception as e:
            self.logger.error(f"Erreur préprocessing: {e}")
            return img
    
    def extract_text_from_image(self, img: np.ndarray, zone_type: str = 'default') -> str:
        """Extraction de texte avec OCR optimisé + cache intelligent (inspiré PokerGPT)"""
        try:
            # Calcul hash de l'image pour cache (optimisation PokerGPT)
            img_hash = hash(img.tobytes())
            cache_key = f"{zone_type}_{img_hash}"
            
            # Vérification cache
            current_time = time.time()
            if cache_key in self.image_cache:
                cached_data = self.image_cache[cache_key]
                if current_time - cached_data['timestamp'] < self.cache_timeout:
                    return cached_data['text']
            
            # Préprocessing
            processed_img = self.preprocess_image_advanced(img, zone_type)
            
            # Configuration OCR spécialisée selon le type (optimisée)
            config = self.tesseract_configs.get(zone_type, self.tesseract_config)
            
            # OCR avec gestion d'erreurs robuste
            text = pytesseract.image_to_string(processed_img, config=config)
            text = text.strip()
            
            # Mise en cache du résultat
            self.image_cache[cache_key] = {
                'text': text,
                'timestamp': current_time
            }
            
            # Nettoyage périodique du cache
            if len(self.image_cache) > 100:
                self._cleanup_cache()
            
            return text
            
        except pytesseract.TesseractError as e:
            self.logger.error(f"Erreur Tesseract OCR: {e}")
            return ""
        except cv2.error as e:
            self.logger.error(f"Erreur OpenCV: {e}")
            return ""
        except Exception as e:
            self.logger.error(f"Erreur inattendue OCR: {e}")
            return ""
    
    def detect_poker_client(self, img: np.ndarray) -> str:
        """Détecte le client de poker utilisé"""
        try:
            # Recherche de patterns spécifiques aux clients
            # PokerStars
            if self._detect_pattern(img, "PokerStars"):
                return "pokerstars"
            
            # Winamax
            if self._detect_pattern(img, "Winamax"):
                return "winamax"
            
            # Autres clients
            return "unknown"
            
        except Exception as e:
            self.logger.error(f"Erreur détection client: {e}")
            return "unknown"
    
    def _detect_pattern(self, img: np.ndarray, pattern: str) -> bool:
        """Détecte un pattern spécifique dans l'image"""
        try:
            text = pytesseract.image_to_string(img)
            return pattern.lower() in text.lower()
        except:
            return False
    
    def parse_hero_cards(self, text: str) -> Tuple[str, str]:
        """Parse les cartes du héros"""
        try:
            # Pattern pour cartes poker (ex: "As Kh", "Td 9c")
            pattern = r'([AKQJT98765432])([shdc])\s*([AKQJT98765432])([shdc])'
            match = re.search(pattern, text.replace(' ', ''))
            
            if match:
                card1 = f"{match.group(1)}{match.group(2)}"
                card2 = f"{match.group(3)}{match.group(4)}"
                return (card1, card2)
            
            return ("", "")
            
        except Exception as e:
            self.logger.error(f"Erreur parse cartes héros: {e}")
            return ("", "")
    
    def parse_board_cards(self, text: str) -> List[str]:
        """Parse les cartes du board"""
        try:
            cards = []
            # Pattern pour cartes sur le board
            pattern = r'([AKQJT98765432])([shdc])'
            matches = re.findall(pattern, text.replace(' ', ''))
            
            for match in matches:
                cards.append(f"{match[0]}{match[1]}")
            
            return cards[:5]  # Maximum 5 cartes
            
        except Exception as e:
            self.logger.error(f"Erreur parse board: {e}")
            return []
    
    def parse_monetary_value(self, text: str) -> float:
        """Parse une valeur monétaire avec validation renforcée"""
        try:
            # Nettoyage du texte
            cleaned = re.sub(r'[^\d.,k]', '', text.lower())
            
            # Validation : vérifier si cleaned n'est pas vide
            if not cleaned or cleaned.strip() == '':
                return 0.0
            
            if 'k' in cleaned:
                # Gestion des milliers (ex: "1.5k" = 1500)
                number_str = cleaned.replace('k', '').replace(',', '.')
                if not number_str or number_str == '.':
                    return 0.0
                number = float(number_str)
                return number * 1000
            else:
                # Valeur normale
                clean_number = cleaned.replace(',', '.')
                if not clean_number or clean_number == '.':
                    return 0.0
                return float(clean_number)
                
        except (ValueError, TypeError) as e:
            # 'cleaned' peut être non défini si l'erreur survient avant son assignment
            cleaned_value = locals().get('cleaned', 'N/A')
            self.logger.error(f"Erreur parse valeur: could not convert string to float: '{text}' -> '{cleaned_value}'")
            return 0.0
        except Exception as e:
            self.logger.error(f"Erreur parse valeur: {e}")
            return 0.0
    
    def analyze_game_state(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyse complète de l'état du jeu"""
        try:
            game_data = {}
            
            # Détection du client poker
            poker_client = self.detect_poker_client(img)
            game_data['poker_client'] = poker_client
            
            # Analyse des différentes zones
            for zone_name, zone_coords in self.roi_zones.items():
                try:
                    # Extraction de la zone
                    zone_img = img[zone_coords['top']:zone_coords['top'] + zone_coords['height'],
                                  zone_coords['left']:zone_coords['left'] + zone_coords['width']]
                    
                    if zone_img.size == 0:
                        continue
                    
                    # OCR selon le type de zone
                    if zone_name == 'hero_cards':
                        text = self.extract_text_from_image(zone_img, 'cards')
                        game_data['hero_cards'] = self.parse_hero_cards(text)
                    
                    elif zone_name == 'board_cards':
                        text = self.extract_text_from_image(zone_img, 'cards')
                        game_data['board_cards'] = self.parse_board_cards(text)
                    
                    elif zone_name in ['pot_size', 'hero_stack']:
                        text = self.extract_text_from_image(zone_img, 'numbers')
                        game_data[zone_name] = self.parse_monetary_value(text)
                    
                    elif zone_name == 'blinds':
                        text = self.extract_text_from_image(zone_img, 'numbers')
                        # Parse SB/BB
                        blinds = self._parse_blinds(text)
                        game_data.update(blinds)
                    
                    elif zone_name == 'action_buttons':
                        text = self.extract_text_from_image(zone_img, 'buttons')
                        game_data['action_to_hero'] = self._detect_action_buttons(text)
                    
                except Exception as e:
                    self.logger.error(f"Erreur analyse zone {zone_name}: {e}")
                    continue
            
            # Ajout de métadonnées
            game_data['timestamp'] = time.time()
            game_data['confidence'] = self._calculate_confidence(game_data)
            
            return game_data
            
        except Exception as e:
            self.logger.error(f"Erreur analyse état jeu: {e}")
            return {}
    
    def _cleanup_cache(self):
        """Nettoie le cache des images expirées (optimisation PokerGPT)"""
        try:
            current_time = time.time()
            expired_keys = []
            
            for key, data in self.image_cache.items():
                if current_time - data['timestamp'] > self.cache_timeout * 2:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.image_cache[key]
            
            self.logger.debug(f"Cache nettoyé: {len(expired_keys)} entrées supprimées")
            
        except Exception as e:
            self.logger.error(f"Erreur nettoyage cache: {e}")
    
    def _parse_blinds(self, text: str) -> Dict[str, float]:
        """Parse les blinds"""
        try:
            # Pattern pour blinds (ex: "5/10", "0.5/1")
            pattern = r'(\d+(?:\.\d+)?)[/\s]+(\d+(?:\.\d+)?)'
            match = re.search(pattern, text)
            
            if match:
                return {
                    'small_blind': float(match.group(1)),
                    'big_blind': float(match.group(2))
                }
            
            return {'small_blind': 0.0, 'big_blind': 0.0}
            
        except Exception as e:
            self.logger.error(f"Erreur parse blinds: {e}")
            return {'small_blind': 0.0, 'big_blind': 0.0}
    
    def _detect_action_buttons(self, text: str) -> bool:
        """Détecte si c'est au tour du héros"""
        action_keywords = ['fold', 'call', 'raise', 'bet', 'check', 'all-in']
        text_lower = text.lower()
        
        return any(keyword in text_lower for keyword in action_keywords)
    
    def _calculate_confidence(self, game_data: Dict[str, Any]) -> float:
        """Calcule la confiance dans l'analyse"""
        try:
            confidence = 0.0
            total_checks = 0
            
            # Vérifications de cohérence
            if game_data.get('hero_cards') and game_data['hero_cards'] != ("", ""):
                confidence += 25
            total_checks += 1
            
            if game_data.get('pot_size', 0) > 0:
                confidence += 25
            total_checks += 1
            
            if game_data.get('hero_stack', 0) > 0:
                confidence += 25
            total_checks += 1
            
            if game_data.get('small_blind', 0) > 0 and game_data.get('big_blind', 0) > 0:
                confidence += 25
            total_checks += 1
            
            return confidence / total_checks if total_checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Erreur calcul confiance: {e}")
            return 0.0
    
    def capture_and_analyze(self) -> Optional[Dict[str, Any]]:
        """Capture et analyse en une seule opération"""
        try:
            with self.capture_lock:
                # Capture de l'écran
                img = self.capture_screen_region()
                if img is None:
                    return None
                
                # Analyse
                game_data = self.analyze_game_state(img)
                
                # Cache du résultat
                self.last_capture = img
                self.last_analysis = game_data
                
                return game_data
                
        except Exception as e:
            self.logger.error(f"Erreur capture et analyse: {e}")
            return None
    
    def calibrate_zones(self, poker_client: str = "auto"):
        """Calibre les zones d'intérêt selon le client"""
        try:
            if poker_client == "pokerstars":
                self.roi_zones.update({
                    'hero_cards': {'top': 580, 'left': 440, 'width': 140, 'height': 50},
                    'board_cards': {'top': 280, 'left': 350, 'width': 320, 'height': 60}
                })
            elif poker_client == "winamax":
                self.roi_zones.update({
                    'hero_cards': {'top': 600, 'left': 460, 'width': 120, 'height': 45},
                    'board_cards': {'top': 300, 'left': 370, 'width': 300, 'height': 55}
                })
            
            self.logger.info(f"Zones calibrées pour {poker_client}")
            
        except Exception as e:
            self.logger.error(f"Erreur calibrage: {e}")
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Retourne les métriques de performance OCR"""
        try:
            # Simulation de métriques (à implémenter avec de vraies mesures)
            return {
                'avg_capture_time_ms': 15.0,
                'avg_ocr_time_ms': 35.0,
                'avg_confidence': 85.0,
                'success_rate': 92.0
            }
        except Exception as e:
            self.logger.error(f"Erreur métriques: {e}")
            return {}