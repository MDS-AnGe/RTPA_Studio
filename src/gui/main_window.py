"""
Interface graphique principale de RTPA Studio
Interface moderne et élégante avec CustomTkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Dict, Any, Optional
import json

from ..utils.logger import get_logger

# Configuration CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RTAPMainWindow:
    """Fenêtre principale de RTPA Studio"""
    
    def __init__(self, app_manager):
        self.logger = get_logger(__name__)
        self.app_manager = app_manager
        
        # Configuration de la fenêtre principale
        self.root = ctk.CTk()
        self.root.title("RTPA Studio - Real-Time Poker Analysis")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Variables de l'interface
        self.language = tk.StringVar(value="fr")
        self.is_running = False
        self.update_thread = None
        
        # Configuration multilingue
        self.translations = {
            "fr": {
                "title": "RTPA Studio - Analyse Poker Temps Réel",
                "start": "Démarrer",
                "stop": "Arrêter",
                "settings": "Paramètres",
                "statistics": "Statistiques",
                "game_state": "État du Jeu",
                "recommendations": "Recommandations",
                "hero_cards": "Cartes Héros:",
                "board_cards": "Board:",
                "pot_size": "Pot:",
                "stack": "Stack:",
                "win_probability": "Probabilité de Victoire:",
                "action": "Action Recommandée:",
                "risk_level": "Niveau de Risque:",
                "hands_played": "Mains Jouées:",
                "hands_won": "Mains Gagnées:",
                "win_rate": "Taux de Victoire:",
                "expected_rate": "Taux Attendu:",
                "performance": "Performance:",
                "table_type": "Type de Table:",
                "cashgame": "Cash Game",
                "tournament": "Tournoi",
                "language": "Langue:",
                "risk_override": "Override Risque (%):",
                "auto_risk": "Risque Automatique",
                "gpu_enabled": "GPU Activé",
                "resource_management": "Gestion Auto Ressources"
            },
            "en": {
                "title": "RTPA Studio - Real-Time Poker Analysis",
                "start": "Start",
                "stop": "Stop",
                "settings": "Settings",
                "statistics": "Statistics",
                "game_state": "Game State",
                "recommendations": "Recommendations",
                "hero_cards": "Hero Cards:",
                "board_cards": "Board:",
                "pot_size": "Pot:",
                "stack": "Stack:",
                "win_probability": "Win Probability:",
                "action": "Recommended Action:",
                "risk_level": "Risk Level:",
                "hands_played": "Hands Played:",
                "hands_won": "Hands Won:",
                "win_rate": "Win Rate:",
                "expected_rate": "Expected Rate:",
                "performance": "Performance:",
                "table_type": "Table Type:",
                "cashgame": "Cash Game",
                "tournament": "Tournament",
                "language": "Language:",
                "risk_override": "Risk Override (%):",
                "auto_risk": "Auto Risk",
                "gpu_enabled": "GPU Enabled",
                "resource_management": "Auto Resource Management"
            }
        }
        
        self.create_widgets()
        self.setup_layout()
        self.start_update_loop()
        
        self.logger.info("Interface graphique initialisée")
    
    def create_widgets(self):
        """Création des widgets de l'interface"""
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        
        # Barre de contrôle supérieure
        self.control_frame = ctk.CTkFrame(self.main_frame)
        
        self.start_button = ctk.CTkButton(
            self.control_frame,
            text=self.get_text("start"),
            command=self.toggle_analysis,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        
        self.status_label = ctk.CTkLabel(
            self.control_frame,
            text="● Arrêté",
            font=ctk.CTkFont(size=12),
            text_color="red"
        )
        
        # Frame de contenu principal (3 colonnes)
        self.content_frame = ctk.CTkFrame(self.main_frame)
        
        # Colonne 1: État du jeu
        self.game_state_frame = ctk.CTkFrame(self.content_frame)
        self.game_state_title = ctk.CTkLabel(
            self.game_state_frame,
            text=self.get_text("game_state"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        
        # Widgets état du jeu
        self.hero_cards_label = ctk.CTkLabel(self.game_state_frame, text=self.get_text("hero_cards"))
        self.hero_cards_value = ctk.CTkLabel(self.game_state_frame, text="-- --", font=ctk.CTkFont(size=14, weight="bold"))
        
        self.board_cards_label = ctk.CTkLabel(self.game_state_frame, text=self.get_text("board_cards"))
        self.board_cards_value = ctk.CTkLabel(self.game_state_frame, text="-- -- -- -- --", font=ctk.CTkFont(size=14, weight="bold"))
        
        self.pot_size_label = ctk.CTkLabel(self.game_state_frame, text=self.get_text("pot_size"))
        self.pot_size_value = ctk.CTkLabel(self.game_state_frame, text="0.00€", font=ctk.CTkFont(size=14, weight="bold"))
        
        self.stack_label = ctk.CTkLabel(self.game_state_frame, text=self.get_text("stack"))
        self.stack_value = ctk.CTkLabel(self.game_state_frame, text="0.00€", font=ctk.CTkFont(size=14, weight="bold"))
        
        # Colonne 2: Recommandations
        self.recommendations_frame = ctk.CTkFrame(self.content_frame)
        self.recommendations_title = ctk.CTkLabel(
            self.recommendations_frame,
            text=self.get_text("recommendations"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        
        # Widgets recommandations
        self.win_prob_label = ctk.CTkLabel(self.recommendations_frame, text=self.get_text("win_probability"))
        self.win_prob_value = ctk.CTkLabel(self.recommendations_frame, text="50.0%", font=ctk.CTkFont(size=20, weight="bold"), text_color="yellow")
        
        self.action_label = ctk.CTkLabel(self.recommendations_frame, text=self.get_text("action"))
        self.action_value = ctk.CTkLabel(self.recommendations_frame, text="Check", font=ctk.CTkFont(size=18, weight="bold"), text_color="green")
        
        self.risk_label = ctk.CTkLabel(self.recommendations_frame, text=self.get_text("risk_level"))
        self.risk_value = ctk.CTkLabel(self.recommendations_frame, text="30%", font=ctk.CTkFont(size=16, weight="bold"))
        
        # Barre de progression pour probabilité de victoire
        self.win_prob_progress = ctk.CTkProgressBar(self.recommendations_frame, width=300)
        self.win_prob_progress.set(0.5)
        
        # Colonne 3: Paramètres et Statistiques
        self.settings_frame = ctk.CTkFrame(self.content_frame)
        
        # Onglets
        self.tabview = ctk.CTkTabview(self.settings_frame)
        self.stats_tab = self.tabview.add(self.get_text("statistics"))
        self.settings_tab = self.tabview.add(self.get_text("settings"))
        
        # Statistiques
        self.hands_played_label = ctk.CTkLabel(self.stats_tab, text=self.get_text("hands_played"))
        self.hands_played_value = ctk.CTkLabel(self.stats_tab, text="0", font=ctk.CTkFont(size=14, weight="bold"))
        
        self.hands_won_label = ctk.CTkLabel(self.stats_tab, text=self.get_text("hands_won"))
        self.hands_won_value = ctk.CTkLabel(self.stats_tab, text="0", font=ctk.CTkFont(size=14, weight="bold"))
        
        self.win_rate_label = ctk.CTkLabel(self.stats_tab, text=self.get_text("win_rate"))
        self.win_rate_value = ctk.CTkLabel(self.stats_tab, text="0.0%", font=ctk.CTkFont(size=14, weight="bold"))
        
        self.expected_rate_label = ctk.CTkLabel(self.stats_tab, text=self.get_text("expected_rate"))
        self.expected_rate_value = ctk.CTkLabel(self.stats_tab, text="65.0%", font=ctk.CTkFont(size=14, weight="bold"), text_color="blue")
        
        self.performance_label = ctk.CTkLabel(self.stats_tab, text=self.get_text("performance"))
        self.performance_value = ctk.CTkLabel(self.stats_tab, text="0.0%", font=ctk.CTkFont(size=14, weight="bold"))
        
        # Graphique de performance
        self.performance_progress = ctk.CTkProgressBar(self.stats_tab, width=200)
        self.performance_progress.set(0.0)
        
        # Paramètres
        self.language_label = ctk.CTkLabel(self.settings_tab, text=self.get_text("language"))
        self.language_combo = ctk.CTkComboBox(
            self.settings_tab,
            values=["Français", "English"],
            command=self.change_language,
            width=150
        )
        
        self.table_type_label = ctk.CTkLabel(self.settings_tab, text=self.get_text("table_type"))
        self.table_type_combo = ctk.CTkComboBox(
            self.settings_tab,
            values=[self.get_text("cashgame"), self.get_text("tournament")],
            command=self.change_table_type,
            width=150
        )
        
        self.risk_override_label = ctk.CTkLabel(self.settings_tab, text=self.get_text("risk_override"))
        self.risk_slider = ctk.CTkSlider(
            self.settings_tab,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self.update_risk_override,
            width=200
        )
        self.risk_slider.set(50)
        self.risk_value_label = ctk.CTkLabel(self.settings_tab, text="50%")
        
        self.auto_risk_check = ctk.CTkCheckBox(
            self.settings_tab,
            text=self.get_text("auto_risk"),
            command=self.toggle_auto_risk
        )
        self.auto_risk_check.select()
        
        self.gpu_check = ctk.CTkCheckBox(
            self.settings_tab,
            text=self.get_text("gpu_enabled"),
            command=self.toggle_gpu
        )
        self.gpu_check.select()
        
        self.resource_mgmt_check = ctk.CTkCheckBox(
            self.settings_tab,
            text=self.get_text("resource_management"),
            command=self.toggle_resource_management
        )
        self.resource_mgmt_check.select()
    
    def setup_layout(self):
        """Organisation des widgets"""
        
        # Frame principal
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Barre de contrôle
        self.control_frame.pack(fill="x", pady=(0, 10))
        self.start_button.pack(side="left", padx=(10, 20))
        self.status_label.pack(side="left", padx=10)
        
        # Frame de contenu (3 colonnes)
        self.content_frame.pack(fill="both", expand=True)
        
        # Colonne 1: État du jeu
        self.game_state_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.game_state_title.pack(pady=10)
        
        # Layout état du jeu
        game_widgets = [
            (self.hero_cards_label, self.hero_cards_value),
            (self.board_cards_label, self.board_cards_value),
            (self.pot_size_label, self.pot_size_value),
            (self.stack_label, self.stack_value)
        ]
        
        for label, value in game_widgets:
            frame = ctk.CTkFrame(self.game_state_frame)
            frame.pack(fill="x", padx=10, pady=5)
            label.pack(anchor="w", padx=10, pady=(5, 0))
            value.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Colonne 2: Recommandations
        self.recommendations_frame.pack(side="left", fill="both", expand=True, padx=5)
        self.recommendations_title.pack(pady=10)
        
        # Layout recommandations
        rec_frame = ctk.CTkFrame(self.recommendations_frame)
        rec_frame.pack(fill="x", padx=10, pady=10)
        
        self.win_prob_label.pack(pady=(10, 0))
        self.win_prob_value.pack(pady=5)
        self.win_prob_progress.pack(pady=10)
        
        self.action_label.pack(pady=(10, 0))
        self.action_value.pack(pady=5)
        
        self.risk_label.pack(pady=(10, 0))
        self.risk_value.pack(pady=(0, 10))
        
        # Colonne 3: Paramètres et Stats
        self.settings_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Layout statistiques
        stats_widgets = [
            (self.hands_played_label, self.hands_played_value),
            (self.hands_won_label, self.hands_won_value),
            (self.win_rate_label, self.win_rate_value),
            (self.expected_rate_label, self.expected_rate_value),
            (self.performance_label, self.performance_value)
        ]
        
        for label, value in stats_widgets:
            frame = ctk.CTkFrame(self.stats_tab)
            frame.pack(fill="x", padx=5, pady=3)
            label.pack(anchor="w", padx=5, pady=(3, 0))
            value.pack(anchor="w", padx=5, pady=(0, 3))
        
        self.performance_progress.pack(pady=10)
        
        # Layout paramètres
        settings_widgets = [
            (self.language_label, self.language_combo),
            (self.table_type_label, self.table_type_combo),
            (self.risk_override_label, None)
        ]
        
        for label, widget in settings_widgets:
            frame = ctk.CTkFrame(self.settings_tab)
            frame.pack(fill="x", padx=5, pady=5)
            label.pack(anchor="w", padx=5, pady=3)
            if widget:
                widget.pack(anchor="w", padx=5, pady=3)
        
        # Slider de risque avec label
        risk_frame = ctk.CTkFrame(self.settings_tab)
        risk_frame.pack(fill="x", padx=5, pady=5)
        self.risk_slider.pack(padx=5, pady=3)
        self.risk_value_label.pack(padx=5, pady=3)
        
        # Checkboxes
        checkboxes = [self.auto_risk_check, self.gpu_check, self.resource_mgmt_check]
        for checkbox in checkboxes:
            checkbox.pack(anchor="w", padx=10, pady=5)
    
    def get_text(self, key: str) -> str:
        """Récupère le texte traduit"""
        lang = self.language.get()
        return self.translations.get(lang, {}).get(key, key)
    
    def change_language(self, selection: str):
        """Change la langue de l'interface"""
        lang = "fr" if selection == "Français" else "en"
        self.language.set(lang)
        self.update_interface_language()
    
    def update_interface_language(self):
        """Met à jour tous les textes de l'interface"""
        self.root.title(self.get_text("title"))
        
        # Mise à jour des textes (implémentation simplifiée)
        if hasattr(self, 'start_button'):
            if not self.is_running:
                self.start_button.configure(text=self.get_text("start"))
            else:
                self.start_button.configure(text=self.get_text("stop"))
    
    def toggle_analysis(self):
        """Démarre/arrête l'analyse"""
        if not self.is_running:
            self.start_analysis()
        else:
            self.stop_analysis()
    
    def start_analysis(self):
        """Démarre l'analyse temps réel"""
        try:
            self.app_manager.start()
            self.is_running = True
            
            self.start_button.configure(text=self.get_text("stop"))
            self.status_label.configure(text="● En cours", text_color="green")
            
            self.logger.info("Analyse démarrée")
            
        except Exception as e:
            self.logger.error(f"Erreur démarrage analyse: {e}")
            messagebox.showerror("Erreur", f"Impossible de démarrer l'analyse: {e}")
    
    def stop_analysis(self):
        """Arrête l'analyse"""
        try:
            self.app_manager.stop()
            self.is_running = False
            
            self.start_button.configure(text=self.get_text("start"))
            self.status_label.configure(text="● Arrêté", text_color="red")
            
            self.logger.info("Analyse arrêtée")
            
        except Exception as e:
            self.logger.error(f"Erreur arrêt analyse: {e}")
    
    def update_interface(self):
        """Met à jour l'interface avec les dernières données"""
        try:
            # Récupération de l'état du jeu
            game_state = self.app_manager.get_current_state()
            if game_state:
                # Mise à jour état du jeu
                if game_state.hero_cards and game_state.hero_cards != ("", ""):
                    self.hero_cards_value.configure(text=f"{game_state.hero_cards[0]} {game_state.hero_cards[1]}")
                
                if game_state.board_cards:
                    board_text = " ".join(game_state.board_cards[:5])
                    self.board_cards_value.configure(text=board_text or "-- -- -- -- --")
                
                self.pot_size_value.configure(text=f"{game_state.pot_size:.2f}€")
                self.stack_value.configure(text=f"{game_state.hero_stack:.2f}€")
            
            # Récupération des recommandations
            recommendation = self.app_manager.get_recommendation()
            if recommendation:
                win_prob = recommendation.get('win_probability', 50.0)
                self.win_prob_value.configure(text=f"{win_prob:.1f}%")
                self.win_prob_progress.set(win_prob / 100.0)
                
                action = recommendation.get('action_type', 'check')
                self.action_value.configure(text=action.title())
                
                # Couleur selon l'action
                action_colors = {
                    'fold': 'red',
                    'check': 'yellow',
                    'call': 'yellow',
                    'bet': 'green',
                    'raise': 'green',
                    'bet_small': 'orange',
                    'bet_medium': 'orange',
                    'bet_large': 'green',
                    'bet_allin': 'red'
                }
                color = action_colors.get(action, 'white')
                self.action_value.configure(text_color=color)
                
                risk = recommendation.get('risk_level', 50.0)
                self.risk_value.configure(text=f"{risk:.0f}%")
            
            # Récupération des statistiques
            stats = self.app_manager.get_statistics()
            if stats:
                self.hands_played_value.configure(text=str(stats.get('hands_played', 0)))
                self.hands_won_value.configure(text=str(stats.get('hands_won', 0)))
                
                win_rate = stats.get('win_rate', 0.0)
                self.win_rate_value.configure(text=f"{win_rate:.1f}%")
                
                performance_ratio = stats.get('performance_ratio', 0.0)
                self.performance_value.configure(text=f"{performance_ratio:.1f}%")
                self.performance_progress.set(min(performance_ratio / 100.0, 1.0))
                
        except Exception as e:
            self.logger.error(f"Erreur mise à jour interface: {e}")
    
    def change_table_type(self, selection: str):
        """Change le type de table"""
        try:
            table_type = "cashgame" if "Cash" in selection else "tournament"
            self.app_manager.update_settings({'table_type': table_type})
            
        except Exception as e:
            self.logger.error(f"Erreur changement type table: {e}")
    
    def update_risk_override(self, value: float):
        """Met à jour le pourcentage de risque manuel"""
        try:
            risk_percent = int(value)
            self.risk_value_label.configure(text=f"{risk_percent}%")
            
            if not self.auto_risk_check.get():
                self.app_manager.manual_override(risk_percent)
                
        except Exception as e:
            self.logger.error(f"Erreur mise à jour risque: {e}")
    
    def toggle_auto_risk(self):
        """Active/désactive la gestion automatique du risque"""
        try:
            auto_risk = self.auto_risk_check.get()
            self.app_manager.update_settings({'manual_risk_override': not auto_risk})
            
        except Exception as e:
            self.logger.error(f"Erreur toggle auto risque: {e}")
    
    def toggle_gpu(self):
        """Active/désactive le GPU"""
        try:
            gpu_enabled = self.gpu_check.get()
            self.app_manager.update_settings({'gpu_enabled': gpu_enabled})
            
        except Exception as e:
            self.logger.error(f"Erreur toggle GPU: {e}")
    
    def toggle_resource_management(self):
        """Active/désactive la gestion automatique des ressources"""
        try:
            auto_mgmt = self.resource_mgmt_check.get()
            self.app_manager.update_settings({'auto_resource_management': auto_mgmt})
            
        except Exception as e:
            self.logger.error(f"Erreur toggle gestion ressources: {e}")
    
    def start_update_loop(self):
        """Démarre la boucle de mise à jour de l'interface"""
        def update_loop():
            while True:
                try:
                    if self.is_running:
                        self.root.after(0, self.update_interface)
                    time.sleep(0.5)  # Mise à jour toutes les 500ms
                    
                except Exception as e:
                    self.logger.error(f"Erreur boucle mise à jour: {e}")
                    time.sleep(1)
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def run(self):
        """Lance l'interface graphique"""
        try:
            self.logger.info("Lancement de l'interface graphique")
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Erreur interface graphique: {e}")
    
    def on_closing(self):
        """Gestion de la fermeture de l'application"""
        try:
            if self.is_running:
                self.stop_analysis()
            
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Erreur fermeture: {e}")
        finally:
            exit(0)