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
import os

from ..utils.logger import get_logger

# Configuration CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RTAPMainWindow:
    """Fenêtre principale de RTPA Studio"""
    
    def __init__(self, app_manager):
        self.logger = get_logger(__name__)
        self.app_manager = app_manager
        
        # Chargement des informations de version
        self.version_info = self._load_version_info()
        
        # Configuration de la fenêtre principale
        self.root = ctk.CTk()
        title = f"RTPA Studio v{self.version_info['version']} - Real-Time Poker Analysis"
        self.root.title(title)
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Configuration du logo et icône
        try:
            # Utiliser le logo comme icône si disponible
            self.root.iconbitmap("attached_assets/RTPA_Studio_icon_1757250204909.ico")
        except:
            # Fallback si l'icône n'est pas trouvée
            pass
        
        # Variables de l'interface
        self.language = tk.StringVar(value="fr")
        self.is_running = False
        self.update_thread = None
        self.system_status = "waiting"  # waiting, active, paused
        
        # Callback pour les changements d'état automatiques
        self.app_manager.add_status_callback(self._on_system_status_change)
        
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
        
        # En-tête avec logo et indicateur d'état
        self.header_frame = ctk.CTkFrame(self.main_frame)
        
        # Logo RTPA Studio
        try:
            from PIL import Image
            logo_image = Image.open("attached_assets/RTPA_Studio_logo_1757250204909.png")
            logo_image = logo_image.resize((200, 60), Image.Resampling.LANCZOS)
            self.logo_ctk = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(200, 60))
            self.logo_label = ctk.CTkLabel(self.header_frame, image=self.logo_ctk, text="")
        except:
            # Fallback texte si logo non trouvé
            self.logo_label = ctk.CTkLabel(
                self.header_frame,
                text="🎯 RTPA STUDIO",
                font=ctk.CTkFont(size=20, weight="bold")
            )
        
        # Panel d'informations système (sera ajouté plus tard dans setup_layout)
        self.info_panel = None

        # Indicateur d'état automatique (haut droite)
        self.status_indicator = ctk.CTkFrame(self.header_frame)
        self.status_icon = ctk.CTkLabel(
            self.status_indicator,
            text="⏸️",
            font=ctk.CTkFont(size=20)
        )
        self.status_text = ctk.CTkLabel(
            self.status_indicator,
            text="En attente de plateforme poker",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="orange"
        )
        self.platform_label = ctk.CTkLabel(
            self.status_indicator,
            text="Aucune plateforme détectée",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        
        # Frame de contenu principal (3 colonnes)
        self.content_frame = ctk.CTkFrame(self.main_frame)
        
        # Colonne 1: État du jeu
        self.game_state_frame = ctk.CTkFrame(self.content_frame)
        self.game_state_title = ctk.CTkLabel(
            self.game_state_frame,
            text="▶ " + self.get_text("game_state"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        
        # Widgets état du jeu
        self.hero_cards_label = ctk.CTkLabel(self.game_state_frame, text="♠ " + self.get_text("hero_cards"))
        self.hero_cards_value = ctk.CTkLabel(self.game_state_frame, text="-- --", font=ctk.CTkFont(size=14, weight="bold"))
        
        self.board_cards_label = ctk.CTkLabel(self.game_state_frame, text="♦ " + self.get_text("board_cards"))
        self.board_cards_value = ctk.CTkLabel(self.game_state_frame, text="-- -- -- -- --", font=ctk.CTkFont(size=14, weight="bold"))
        
        self.pot_size_label = ctk.CTkLabel(self.game_state_frame, text="● " + self.get_text("pot_size"))
        self.pot_size_value = ctk.CTkLabel(self.game_state_frame, text="0.00€", font=ctk.CTkFont(size=14, weight="bold"))
        
        self.stack_label = ctk.CTkLabel(self.game_state_frame, text="■ " + self.get_text("stack"))
        self.stack_value = ctk.CTkLabel(self.game_state_frame, text="0.00€", font=ctk.CTkFont(size=14, weight="bold"))
        
        # Colonne 2: Recommandations
        self.recommendations_frame = ctk.CTkFrame(self.content_frame)
        self.recommendations_title = ctk.CTkLabel(
            self.recommendations_frame,
            text="▶ " + self.get_text("recommendations"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        
        # Widgets recommandations
        self.win_prob_label = ctk.CTkLabel(self.recommendations_frame, text="▲ " + self.get_text("win_probability"))
        self.win_prob_value = ctk.CTkLabel(self.recommendations_frame, text="50.0%", font=ctk.CTkFont(size=20, weight="bold"), text_color="yellow")
        
        self.action_label = ctk.CTkLabel(self.recommendations_frame, text="► " + self.get_text("action"))
        self.action_value = ctk.CTkLabel(self.recommendations_frame, text="Check", font=ctk.CTkFont(size=18, weight="bold"), text_color="green")
        
        self.risk_label = ctk.CTkLabel(self.recommendations_frame, text="▼ " + self.get_text("risk_level"))
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
        self.hands_played_label = ctk.CTkLabel(self.stats_tab, text="♠ " + self.get_text("hands_played"))
        self.hands_played_value = ctk.CTkLabel(self.stats_tab, text="0", font=ctk.CTkFont(size=14, weight="bold"))
        
        self.hands_won_label = ctk.CTkLabel(self.stats_tab, text="▲ " + self.get_text("hands_won"))
        self.hands_won_value = ctk.CTkLabel(self.stats_tab, text="0", font=ctk.CTkFont(size=14, weight="bold"))
        
        self.win_rate_label = ctk.CTkLabel(self.stats_tab, text="► " + self.get_text("win_rate"))
        self.win_rate_value = ctk.CTkLabel(self.stats_tab, text="0.0%", font=ctk.CTkFont(size=14, weight="bold"))
        
        self.expected_rate_label = ctk.CTkLabel(self.stats_tab, text="● " + self.get_text("expected_rate"))
        self.expected_rate_value = ctk.CTkLabel(self.stats_tab, text="65.0%", font=ctk.CTkFont(size=14, weight="bold"), text_color="blue")
        
        self.performance_label = ctk.CTkLabel(self.stats_tab, text="■ " + self.get_text("performance"))
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
        
        # En-tête avec logo et status
        self.header_frame.pack(fill="x", pady=(0, 10))
        self.logo_label.pack(side="left", padx=(10, 0))
        
        # Indicateur d'état à droite
        self.status_indicator.pack(side="right", padx=(0, 10))
        self.status_icon.pack(side="left", padx=(10, 5))
        
        # Textes de status en colonne
        status_text_frame = ctk.CTkFrame(self.status_indicator, fg_color="transparent")
        status_text_frame.pack(side="left", padx=(0, 10))
        self.status_text.pack(anchor="w")
        self.platform_label.pack(anchor="w")
        
        # Création du panel d'informations système à droite
        self.info_panel = ctk.CTkFrame(self.main_frame)
        self.info_panel.pack(side="right", fill="y", padx=(5, 0))
        self.info_panel.configure(width=280)
        
        # Titre du panel
        self.info_panel_title = ctk.CTkLabel(
            self.info_panel,
            text="📋 Informations Système",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.info_panel_title.pack(pady=(10, 5))
        
        
        # Onglet Version (dédié à droite)
        self.version_tabview = ctk.CTkTabview(self.info_panel)
        self.version_tabview.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.version_tab = self.version_tabview.add("Version")
        
        # Contenu de l'onglet Version
        self.version_current_label = ctk.CTkLabel(
            self.version_tab,
            text=f"Version Actuelle: {self.version_info['version']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="cyan"
        )
        self.version_current_label.pack(pady=(10, 5))
        
        self.version_date_label = ctk.CTkLabel(
            self.version_tab,
            text=f"Dernière MAJ: {self.version_info['last_update']}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.version_date_label.pack(pady=2)
        
        self.version_build_label = ctk.CTkLabel(
            self.version_tab,
            text=f"Build: {self.version_info['build']}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.version_build_label.pack(pady=2)
        
        self.version_status_label = ctk.CTkLabel(
            self.version_tab,
            text="Status: " + self.version_info['status'].title(),
            font=ctk.CTkFont(size=12),
            text_color="green"
        )
        self.version_status_label.pack(pady=2)
        
        # Boutons de mise à jour
        self.check_update_button = ctk.CTkButton(
            self.version_tab,
            text="🔄 Vérifier les mises à jour",
            command=self.check_for_updates,
            font=ctk.CTkFont(size=12)
        )
        self.check_update_button.pack(pady=(15, 5))
        
        self.update_button = ctk.CTkButton(
            self.version_tab,
            text="⬇️ Mettre à jour",
            command=self.perform_update,
            font=ctk.CTkFont(size=12),
            state="disabled"
        )
        self.update_button.pack(pady=5)
        
        # Zone de statut des mises à jour
        self.update_status_frame = ctk.CTkFrame(self.version_tab)
        self.update_status_frame.pack(fill="x", pady=(10, 5))
        
        self.update_status_label = ctk.CTkLabel(
            self.update_status_frame,
            text="Prêt pour vérification",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.update_status_label.pack(pady=5)
        
        # Section système (déplacée sous version)
        self.system_info_frame = ctk.CTkFrame(self.info_panel)
        self.system_info_frame.pack(fill="x", padx=10, pady=5)
        
        self.system_title = ctk.CTkLabel(
            self.system_info_frame,
            text="⚙️ Système",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.system_title.pack(pady=(5, 2))
        
        self.cpu_label = ctk.CTkLabel(
            self.system_info_frame,
            text="CPU: --",
            font=ctk.CTkFont(size=10)
        )
        self.cpu_label.pack(pady=1)
        
        self.memory_label = ctk.CTkLabel(
            self.system_info_frame,
            text="RAM: --",
            font=ctk.CTkFont(size=10)
        )
        self.memory_label.pack(pady=1)
        
        self.cfr_status_label = ctk.CTkLabel(
            self.system_info_frame,
            text="CFR: Initialisation...",
            font=ctk.CTkFont(size=10),
            text_color="orange"
        )
        self.cfr_status_label.pack(pady=1)

        # Frame de contenu principal (réduit pour laisser place au panel)
        self.main_content_frame = ctk.CTkFrame(self.main_frame)
        self.main_content_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Frame de contenu (3 colonnes dans main_content_frame)
        self.content_frame = ctk.CTkFrame(self.main_content_frame)
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
        
        # Mise à jour des textes de l'interface
        # Les boutons ont été remplacés par l'indicateur automatique
        pass
    
    def check_for_updates(self):
        """Vérifie les mises à jour disponibles sur GitHub"""
        try:
            self.update_status_label.configure(text="Vérification en cours...", text_color="orange")
            self.check_update_button.configure(state="disabled")
            
            # Utilisation d'un thread pour éviter de bloquer l'interface
            import threading
            thread = threading.Thread(target=self._check_github_updates, daemon=True)
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Erreur vérification mises à jour: {e}")
            self.update_status_label.configure(text="Erreur lors de la vérification", text_color="red")
            self.check_update_button.configure(state="normal")

    def _check_github_updates(self):
        """Vérifie les mises à jour sur GitHub (thread séparé)"""
        try:
            import requests
            import json
            from packaging import version
            
            # Récupération des releases GitHub
            url = "https://api.github.com/repos/MDS-AnGe/RTPA_Studio/releases/latest"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data['tag_name'].lstrip('v')
                current_version = self.version_info['version']
                
                # Comparaison des versions
                if version.parse(latest_version) > version.parse(current_version):
                    # Mise à jour disponible
                    self.root.after(0, lambda: self._update_ui_new_version_available(latest_version, release_data))
                else:
                    # Déjà à jour
                    self.root.after(0, lambda: self.update_status_label.configure(
                        text="Vous avez la dernière version", text_color="green"
                    ))
                    self.root.after(0, lambda: self.check_update_button.configure(state="normal"))
            else:
                self.root.after(0, lambda: self.update_status_label.configure(
                    text="Impossible de vérifier les mises à jour", text_color="red"
                ))
                self.root.after(0, lambda: self.check_update_button.configure(state="normal"))
                
        except Exception as e:
            self.logger.error(f"Erreur GitHub API: {e}")
            self.root.after(0, lambda: self.update_status_label.configure(
                text="Erreur de connexion", text_color="red"
            ))
            self.root.after(0, lambda: self.check_update_button.configure(state="normal"))

    def _update_ui_new_version_available(self, latest_version, release_data):
        """Met à jour l'interface quand une nouvelle version est disponible"""
        self.update_status_label.configure(
            text=f"Nouvelle version disponible: v{latest_version}", 
            text_color="cyan"
        )
        self.update_button.configure(state="normal")
        self.check_update_button.configure(state="normal")
        
        # Stocker les données de release pour la mise à jour
        self.latest_release_data = release_data

    def perform_update(self):
        """Lance la mise à jour du logiciel"""
        try:
            from tkinter import messagebox
            
            # Confirmation avec l'utilisateur
            result = messagebox.askyesno(
                "Confirmation de mise à jour",
                "La mise à jour va redémarrer l'application.\n\n"
                "Vos données (base de données et entraînements CFR) seront préservées.\n\n"
                "Continuer ?",
                icon='question'
            )
            
            if result:
                self.update_status_label.configure(text="Préparation de la mise à jour...", text_color="orange")
                self.update_button.configure(state="disabled")
                
                # Lance la mise à jour en arrière-plan
                import threading
                thread = threading.Thread(target=self._perform_git_update, daemon=True)
                thread.start()
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour: {e}")
            self.update_status_label.configure(text="Erreur de mise à jour", text_color="red")

    def _perform_git_update(self):
        """Effectue la mise à jour Git (thread séparé)"""
        try:
            import subprocess
            import os
            import shutil
            import time
            
            self.root.after(0, lambda: self.update_status_label.configure(
                text="Sauvegarde en cours...", text_color="orange"
            ))
            
            # Sauvegarde des données importantes
            backup_files = []
            important_dirs = ['database/', 'config/', 'attached_assets/']
            
            for dir_name in important_dirs:
                if os.path.exists(dir_name):
                    backup_name = f"{dir_name.rstrip('/')}_backup_{int(time.time())}"
                    shutil.copytree(dir_name, backup_name)
                    backup_files.append(backup_name)
                    self.logger.info(f"Sauvegarde créée: {backup_name}")
            
            # Sauvegarde du fichier version.json
            if os.path.exists('version.json'):
                shutil.copy2('version.json', 'version_backup.json')
                backup_files.append('version_backup.json')
            
            self.root.after(0, lambda: self.update_status_label.configure(
                text="Téléchargement des mises à jour...", text_color="orange"
            ))
            
            # Mise à jour Git
            result = subprocess.run(['git', 'pull', 'origin', 'main'], 
                                  capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                self.root.after(0, lambda: self.update_status_label.configure(
                    text="Mise à jour réussie! Redémarrage...", text_color="green"
                ))
                
                # Restauration des données utilisateur
                for backup in backup_files:
                    if backup.endswith('_backup.json'):
                        continue  # Garde la nouvelle version
                    original = backup.replace(f'_backup_{int(time.time())}', '').replace('_backup', '')
                    if os.path.exists(backup) and not backup.endswith('.json'):
                        if os.path.exists(original):
                            shutil.rmtree(original)
                        shutil.move(backup, original)
                        self.logger.info(f"Données restaurées: {original}")
                
                # Attendre un peu puis redémarrer
                time.sleep(2)
                self.root.after(0, self._restart_application)
                
            else:
                self.root.after(0, lambda: self.update_status_label.configure(
                    text="Erreur lors de la mise à jour", text_color="red"
                ))
                self.logger.error(f"Erreur Git: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"Erreur mise à jour Git: {e}")
            self.root.after(0, lambda: self.update_status_label.configure(
                text="Erreur de mise à jour", text_color="red"
            ))

    def _restart_application(self):
        """Redémarre l'application après mise à jour"""
        try:
            import sys
            import subprocess
            
            # Fermeture propre
            if hasattr(self.app_manager, 'cleanup'):
                self.app_manager.cleanup()
            
            # Redémarrage
            subprocess.Popen([sys.executable] + sys.argv)
            self.root.quit()
            
        except Exception as e:
            self.logger.error(f"Erreur redémarrage: {e}")

    def _update_system_info(self):
        """Met à jour les informations système dans le panel"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_label.configure(text=f"CPU: {cpu_percent:.1f}%")
            
            # Memory usage  
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_gb = memory.used / (1024**3)
            self.memory_label.configure(text=f"RAM: {memory_gb:.1f}GB ({memory_percent:.1f}%)")
            
            # CFR Status
            if hasattr(self.app_manager, 'cfr_engine') and self.app_manager.cfr_engine:
                if hasattr(self.app_manager.cfr_engine, 'training_active') and self.app_manager.cfr_engine.training_active:
                    self.cfr_status_label.configure(text="CFR: Entraînement actif", text_color="green")
                else:
                    self.cfr_status_label.configure(text="CFR: Prêt", text_color="cyan")
            else:
                self.cfr_status_label.configure(text="CFR: Initialisation...", text_color="orange")
                
        except Exception as e:
            self.logger.warning(f"Erreur mise à jour infos système: {e}")

    def _load_version_info(self):
        """Charge les informations de version depuis le fichier version.json"""
        try:
            version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'version.json')
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Impossible de charger version.json: {e}")
        
        # Valeurs par défaut si le fichier n'est pas trouvé
        return {
            "version": "1.0.0",
            "release_date": "2025-09-07",
            "last_update": "2025-09-07",
            "build": "1000",
            "status": "stable"
        }

    def _on_system_status_change(self, status, details):
        """Callback appelé lors des changements d'état du système"""
        try:
            self.system_status = status
            
            # Mise à jour de l'indicateur visuel
            if status == "active":
                self.status_icon.configure(text="▶️")
                self.status_text.configure(text="Analyse en cours", text_color="green")
                if details and 'platform' in details:
                    platform_name = details['platform'] or "Inconnue"
                    platform_info = self.app_manager.platform_detector.supported_platforms.get(
                        platform_name, {'name': platform_name}
                    )
                    self.platform_label.configure(
                        text=f"Plateforme: {platform_info['name']}", 
                        text_color="lightgreen"
                    )
                
            elif status == "waiting":
                self.status_icon.configure(text="⏸️")
                self.status_text.configure(text="En attente de plateforme poker", text_color="orange")
                self.platform_label.configure(text="Aucune plateforme détectée", text_color="gray")
            
            elif status == "paused":
                self.status_icon.configure(text="⏸️")
                self.status_text.configure(text="En pause", text_color="yellow")
                self.platform_label.configure(text="Plateforme fermée", text_color="gray")
            
            self.logger.info(f"État système mis à jour: {status}")
            
        except Exception as e:
            self.logger.error(f"Erreur mise à jour status: {e}")
    
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
                
                # Utiliser le formatage approprié selon le type de table
                table_type = getattr(game_state, 'table_type', 'cashgame')
                if table_type == "tournament":
                    self.pot_size_value.configure(text=f"{game_state.pot_size:.0f}")
                    self.stack_value.configure(text=f"{game_state.hero_stack:.0f}")
                else:
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
            
            # Mise à jour des informations système dans le panel
            self._update_system_info()
                
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
                if hasattr(self, 'is_running') and self.is_running:
                    self.is_running = False
            
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Erreur fermeture: {e}")
        finally:
            exit(0)

# Alias pour compatibilité
MainWindow = RTAPMainWindow