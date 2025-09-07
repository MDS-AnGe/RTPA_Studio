#!/usr/bin/env python3
"""
Interface graphique RTPA Studio - Version moderne avec onglets
Interface visuelle ergonomique et dynamique
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Dict, Any, Optional
import math

from ..utils.logger import get_logger

class RTAPGUIWindow:
    """Interface graphique moderne RTPA Studio avec onglets"""
    
    def __init__(self, app_manager):
        self.logger = get_logger(__name__)
        self.app_manager = app_manager
        
        # Fenêtre principale
        self.root = tk.Tk()
        self.root.title("🎯 RTPA Studio - Real-Time Poker Analysis")
        self.root.geometry("1600x1000")
        self.root.minsize(1400, 900)
        
        # Configuration du style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.is_running = False
        self.language = tk.StringVar(value="fr")
        self.current_theme = "dark"
        
        # Configuration des couleurs
        self.colors = {
            'dark': {
                'bg': '#1e1e1e',
                'fg': '#ffffff',
                'accent': '#0078d4',
                'success': '#16c60c',
                'warning': '#ffaa44',
                'danger': '#d13438',
                'card_bg': '#2d2d2d',
                'tab_bg': '#252525'
            },
            'light': {
                'bg': '#ffffff',
                'fg': '#000000',
                'accent': '#0078d4',
                'success': '#16c60c',
                'warning': '#ffaa44',
                'danger': '#d13438',
                'card_bg': '#f5f5f5',
                'tab_bg': '#f0f0f0'
            }
        }
        
        self.setup_styles()
        self.create_widgets()
        self.setup_layout()
        self.start_update_thread()
        
        self.logger.info("Interface graphique RTPA Studio initialisée")
    
    def setup_styles(self):
        """Configuration des styles"""
        colors = self.colors[self.current_theme]
        
        # Configuration générale
        self.style.configure('TNotebook', background=colors['bg'])
        self.style.configure('TNotebook.Tab', padding=[20, 10])
        
        # Boutons
        self.style.configure('Accent.TButton', foreground='white', background=colors['accent'])
        self.style.configure('Success.TButton', foreground='white', background=colors['success'])
        self.style.configure('Warning.TButton', foreground='white', background=colors['warning'])
        self.style.configure('Danger.TButton', foreground='white', background=colors['danger'])
        
        # Labels
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Big.TLabel', font=('Arial', 20, 'bold'))
        self.style.configure('Card.TLabel', font=('Arial', 14, 'bold'))
        
        # Frames
        self.style.configure('Card.TFrame', relief='raised', borderwidth=2)
    
    def create_widgets(self):
        """Création des widgets de l'interface"""
        
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        
        # Barre de titre avec contrôles
        self.title_frame = ttk.Frame(self.main_frame)
        
        # Logo et titre
        self.title_label = ttk.Label(
            self.title_frame, 
            text="🎯 RTPA Studio", 
            style='Title.TLabel'
        )
        
        # Contrôles principaux
        self.controls_frame = ttk.Frame(self.title_frame)
        
        self.start_stop_btn = ttk.Button(
            self.controls_frame,
            text="🚀 Démarrer",
            style='Success.TButton',
            command=self.toggle_analysis,
            width=15
        )
        
        self.status_label = ttk.Label(
            self.controls_frame,
            text="⏹ Arrêté",
            style='Heading.TLabel'
        )
        
        # Notebook avec onglets
        self.notebook = ttk.Notebook(self.main_frame)
        
        # Onglet 1: État du Jeu
        self.game_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.game_tab, text="🎮 État du Jeu")
        self.create_game_tab()
        
        # Onglet 2: Recommandations
        self.recommendations_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.recommendations_tab, text="🎯 Recommandations")
        self.create_recommendations_tab()
        
        # Onglet 3: Statistiques
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="📊 Statistiques")
        self.create_stats_tab()
        
        # Onglet 4: Options
        self.options_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.options_tab, text="⚙️ Options")
        self.create_options_tab()
        
        # Onglet 5: Paramètres
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="🔧 Paramètres")
        self.create_settings_tab()
        
        # Onglet 6: Performance
        self.performance_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.performance_tab, text="⚡ Performance")
        self.create_performance_tab()
    
    def create_game_tab(self):
        """Création de l'onglet État du Jeu avec recommandations intégrées"""
        
        # Frame principal
        main_container = ttk.Frame(self.game_tab)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Partie haute : Cartes et informations
        top_container = ttk.Frame(main_container)
        top_container.pack(fill='x', pady=(0, 15))
        
        # Section Cartes du Héros
        hero_frame = ttk.LabelFrame(top_container, text="🂡 Cartes du Héros", style='Card.TFrame')
        hero_frame.pack(fill='x', pady=(0, 15))
        
        self.hero_cards_frame = ttk.Frame(hero_frame)
        self.hero_cards_frame.pack(pady=15)
        
        self.hero_card1 = ttk.Label(self.hero_cards_frame, text="🂠", font=('Arial', 48))
        self.hero_card1.pack(side='left', padx=10)
        
        self.hero_card2 = ttk.Label(self.hero_cards_frame, text="🂠", font=('Arial', 48))
        self.hero_card2.pack(side='left', padx=10)
        
        # Section Board
        board_frame = ttk.LabelFrame(top_container, text="🃏 Board", style='Card.TFrame')
        board_frame.pack(fill='x', pady=(0, 15))
        
        self.board_cards_frame = ttk.Frame(board_frame)
        self.board_cards_frame.pack(pady=15)
        
        self.board_cards = []
        for i in range(5):
            card = ttk.Label(self.board_cards_frame, text="🂠", font=('Arial', 36))
            card.pack(side='left', padx=5)
            self.board_cards.append(card)
        
        # Section Informations de Jeu
        info_container = ttk.Frame(top_container)
        info_container.pack(fill='x', pady=(0, 15))
        
        # Colonne gauche
        left_info = ttk.Frame(info_container)
        left_info.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Pot
        pot_frame = ttk.LabelFrame(left_info, text="💰 Pot", style='Card.TFrame')
        pot_frame.pack(fill='x', pady=(0, 10))
        
        self.pot_label = ttk.Label(pot_frame, text="0.00€", style='Big.TLabel')
        self.pot_label.pack(pady=15)
        
        # Stack
        stack_frame = ttk.LabelFrame(left_info, text="💵 Stack", style='Card.TFrame')
        stack_frame.pack(fill='x', pady=(0, 10))
        
        self.stack_label = ttk.Label(stack_frame, text="0.00€", style='Big.TLabel')
        self.stack_label.pack(pady=15)
        
        # Colonne droite
        right_info = ttk.Frame(info_container)
        right_info.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Blinds & Antes
        blinds_frame = ttk.LabelFrame(right_info, text="🎲 Blinds & Antes", style='Card.TFrame')
        blinds_frame.pack(fill='x', pady=(0, 10))
        
        self.blinds_label = ttk.Label(blinds_frame, text="0.00€ / 0.00€", style='Big.TLabel')
        self.blinds_label.pack(pady=10)
        
        self.antes_label = ttk.Label(blinds_frame, text="", style='Card.TLabel')
        self.antes_label.pack(pady=(0, 10))
        
        # Type de Table (petit, dans le coin)
        self.table_type_label = ttk.Label(right_info, text="Cash Game", font=('Arial', 9), foreground='gray')
        self.table_type_label.pack(anchor='ne', pady=5)
        
        # SECTION RECOMMANDATIONS INTÉGRÉES
        recommendations_frame = ttk.LabelFrame(main_container, text="🎯 RECOMMANDATIONS", style='Card.TFrame')
        recommendations_frame.pack(fill='x', pady=(0, 15))
        
        # Action principale (grande)
        action_container = ttk.Frame(recommendations_frame)
        action_container.pack(fill='x', pady=15)
        
        self.main_action_display = ttk.Label(
            action_container, 
            text="ATTENDRE", 
            font=('Arial', 28, 'bold'),
            foreground='orange'
        )
        self.main_action_display.pack()
        
        self.main_bet_size_label = ttk.Label(action_container, text="", style='Heading.TLabel')
        self.main_bet_size_label.pack(pady=(5, 0))
        
        # Détails en ligne
        details_container = ttk.Frame(recommendations_frame)
        details_container.pack(fill='x', padx=15, pady=(0, 15))
        
        # Probabilité de victoire
        prob_frame = ttk.Frame(details_container)
        prob_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(prob_frame, text="💪 Prob. Victoire:", style='Heading.TLabel').pack(anchor='w')
        self.main_win_prob_label = ttk.Label(prob_frame, text="50%", font=('Arial', 16, 'bold'))
        self.main_win_prob_label.pack(anchor='w')
        
        # Risque
        risk_frame = ttk.Frame(details_container)
        risk_frame.pack(side='left', fill='x', expand=True, padx=(20, 0))
        
        ttk.Label(risk_frame, text="⚠️ Niveau Risque:", style='Heading.TLabel').pack(anchor='w')
        self.main_risk_label = ttk.Label(risk_frame, text="50%", font=('Arial', 16, 'bold'))
        self.main_risk_label.pack(anchor='w')
        
        # Confiance
        conf_frame = ttk.Frame(details_container)
        conf_frame.pack(side='left', fill='x', expand=True, padx=(20, 0))
        
        ttk.Label(conf_frame, text="🎯 Confiance:", style='Heading.TLabel').pack(anchor='w')
        self.main_confidence_label = ttk.Label(conf_frame, text="85%", font=('Arial', 16, 'bold'))
        self.main_confidence_label.pack(anchor='w')
        
        # Raisonnement
        reasoning_frame = ttk.Frame(recommendations_frame)
        reasoning_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        ttk.Label(reasoning_frame, text="🧠 Raisonnement:", style='Heading.TLabel').pack(anchor='w')
        self.main_reasoning_label = ttk.Label(
            reasoning_frame, 
            text="En attente d'analyse...", 
            font=('Arial', 11),
            wraplength=800,
            justify='left'
        )
        self.main_reasoning_label.pack(anchor='w', pady=(5, 0))
        
        # SECTION STATISTIQUES EN BAS
        stats_frame = ttk.LabelFrame(main_container, text="📊 STATISTIQUES", style='Card.TFrame')
        stats_frame.pack(fill='x', pady=(0, 0))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x', padx=15, pady=10)
        
        # Ligne de statistiques
        stats_left = ttk.Frame(stats_grid)
        stats_left.pack(side='left', fill='x', expand=True)
        
        stats_right = ttk.Frame(stats_grid)
        stats_right.pack(side='right', fill='x', expand=True)
        
        # Mains jouées/gagnées
        ttk.Label(stats_left, text="Mains:", style='Heading.TLabel').grid(row=0, column=0, sticky='w', padx=5)
        self.main_hands_label = ttk.Label(stats_left, text="0 / 0", style='Card.TLabel')
        self.main_hands_label.grid(row=0, column=1, sticky='w', padx=5)
        
        # Taux victoire
        ttk.Label(stats_left, text="Taux Victoire:", style='Heading.TLabel').grid(row=0, column=2, sticky='w', padx=(15, 5))
        self.main_winrate_label = ttk.Label(stats_left, text="0%", style='Card.TLabel')
        self.main_winrate_label.grid(row=0, column=3, sticky='w', padx=5)
        
        # Performance vs Pro
        ttk.Label(stats_right, text="Performance vs Pro (68%):", style='Heading.TLabel').pack(side='left', padx=5)
        self.main_performance_label = ttk.Label(stats_right, text="0%", style='Card.TLabel')
        self.main_performance_label.pack(side='left', padx=5)
    
    def create_recommendations_tab(self):
        """Création de l'onglet Recommandations"""
        
        main_container = ttk.Frame(self.recommendations_tab)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Action Recommandée (Grand affichage)
        action_frame = ttk.LabelFrame(main_container, text="🎯 Action Recommandée", style='Card.TFrame')
        action_frame.pack(fill='x', pady=(0, 20))
        
        self.action_display = ttk.Label(
            action_frame, 
            text="CHECK", 
            font=('Arial', 32, 'bold'),
            foreground='green'
        )
        self.action_display.pack(pady=20)
        
        self.bet_size_label = ttk.Label(action_frame, text="Taille: 0.00€", style='Heading.TLabel')
        self.bet_size_label.pack(pady=(0, 15))
        
        # Probabilités et Risques
        prob_container = ttk.Frame(main_container)
        prob_container.pack(fill='both', expand=True)
        
        # Probabilité de Victoire
        prob_frame = ttk.LabelFrame(prob_container, text="🎲 Probabilité de Victoire", style='Card.TFrame')
        prob_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.win_prob_label = ttk.Label(prob_frame, text="50.0%", font=('Arial', 28, 'bold'))
        self.win_prob_label.pack(pady=15)
        
        # Barre de progression pour probabilité
        self.win_prob_progress = ttk.Progressbar(
            prob_frame, 
            mode='determinate', 
            length=250,
            style='TProgressbar'
        )
        self.win_prob_progress.pack(pady=10)
        self.win_prob_progress['value'] = 50
        
        # Niveau de Risque
        risk_frame = ttk.LabelFrame(prob_container, text="⚠️ Niveau de Risque", style='Card.TFrame')
        risk_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.risk_label = ttk.Label(risk_frame, text="30%", font=('Arial', 28, 'bold'))
        self.risk_label.pack(pady=15)
        
        # Barre de progression pour risque
        self.risk_progress = ttk.Progressbar(
            risk_frame, 
            mode='determinate', 
            length=250,
            style='TProgressbar'
        )
        self.risk_progress.pack(pady=10)
        self.risk_progress['value'] = 30
        
        # Raisonnement
        reasoning_frame = ttk.LabelFrame(main_container, text="🧠 Raisonnement", style='Card.TFrame')
        reasoning_frame.pack(fill='x', pady=(20, 0))
        
        self.reasoning_text = tk.Text(
            reasoning_frame, 
            height=4, 
            wrap='word',
            font=('Arial', 11),
            state='disabled'
        )
        self.reasoning_text.pack(fill='x', padx=15, pady=15)
    
    def create_stats_tab(self):
        """Création de l'onglet Statistiques"""
        
        main_container = ttk.Frame(self.stats_tab)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Section Performance
        perf_frame = ttk.LabelFrame(main_container, text="📈 Performance", style='Card.TFrame')
        perf_frame.pack(fill='x', pady=(0, 20))
        
        # Grille de statistiques
        stats_grid = ttk.Frame(perf_frame)
        stats_grid.pack(fill='x', padx=15, pady=15)
        
        # Mains Jouées
        ttk.Label(stats_grid, text="Mains Jouées:", style='Heading.TLabel').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.hands_played_value = ttk.Label(stats_grid, text="0", style='Card.TLabel')
        self.hands_played_value.grid(row=0, column=1, sticky='e', padx=5, pady=5)
        
        # Mains Gagnées
        ttk.Label(stats_grid, text="Mains Gagnées:", style='Heading.TLabel').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.hands_won_value = ttk.Label(stats_grid, text="0", style='Card.TLabel')
        self.hands_won_value.grid(row=1, column=1, sticky='e', padx=5, pady=5)
        
        # Taux de Victoire
        ttk.Label(stats_grid, text="Taux de Victoire:", style='Heading.TLabel').grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.win_rate_value = ttk.Label(stats_grid, text="0.0%", style='Card.TLabel')
        self.win_rate_value.grid(row=2, column=1, sticky='e', padx=5, pady=5)
        
        # Taux Attendu (Pro)
        ttk.Label(stats_grid, text="Taux Attendu (Pro):", style='Heading.TLabel').grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.expected_rate_value = ttk.Label(stats_grid, text="65.0%", style='Card.TLabel', foreground='blue')
        self.expected_rate_value.grid(row=3, column=1, sticky='e', padx=5, pady=5)
        
        # Performance Ratio
        ttk.Label(stats_grid, text="Ratio Performance:", style='Heading.TLabel').grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.performance_ratio_value = ttk.Label(stats_grid, text="0.0%", style='Card.TLabel')
        self.performance_ratio_value.grid(row=4, column=1, sticky='e', padx=5, pady=5)
        
        # Graphique de Performance
        chart_frame = ttk.LabelFrame(main_container, text="📊 Évolution", style='Card.TFrame')
        chart_frame.pack(fill='both', expand=True)
        
        # Placeholder pour graphique (à implémenter avec matplotlib)
        self.chart_label = ttk.Label(chart_frame, text="📊 Graphique de performance\n(En cours de développement)", style='Heading.TLabel')
        self.chart_label.pack(expand=True)
    
    def create_options_tab(self):
        """Création de l'onglet Options"""
        
        main_container = ttk.Frame(self.options_tab)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Section Objectifs
        objectives_frame = ttk.LabelFrame(main_container, text="🎯 Objectifs de Jeu", style='Card.TFrame')
        objectives_frame.pack(fill='x', pady=(0, 20))
        
        obj_grid = ttk.Frame(objectives_frame)
        obj_grid.pack(fill='x', padx=15, pady=15)
        
        # Objectif de mains gagnées (optimisé)
        ttk.Label(obj_grid, text="Objectif Mains Gagnées (/100):", style='Heading.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        
        self.hands_target_var = tk.StringVar(value="68")
        self.hands_target_entry = ttk.Entry(obj_grid, textvariable=self.hands_target_var, width=10)
        self.hands_target_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(obj_grid, text="(Optimal: 68% pour joueur expérimenté)", font=('Arial', 9), foreground='gray').grid(row=0, column=2, sticky='w', padx=10, pady=5)
        
        self.auto_target_var = tk.BooleanVar(value=True)
        self.auto_target_check = ttk.Checkbutton(
            obj_grid, 
            text="Gestion Automatique",
            variable=self.auto_target_var,
            command=self.toggle_auto_target
        )
        self.auto_target_check.grid(row=0, column=3, padx=10, pady=5)
        
        # Override Risque (optimisé)
        ttk.Label(obj_grid, text="Override Risque (%):", style='Heading.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        
        self.risk_var = tk.DoubleVar(value=35.0)
        self.risk_scale = ttk.Scale(
            obj_grid, 
            from_=0, 
            to=100, 
            orient='horizontal', 
            variable=self.risk_var,
            length=200,
            command=self.update_risk_display
        )
        self.risk_scale.grid(row=1, column=1, padx=10, pady=5)
        
        self.risk_display = ttk.Label(obj_grid, text="35%", style='Card.TLabel')
        self.risk_display.grid(row=1, column=2, padx=10, pady=5)
        
        ttk.Label(obj_grid, text="(Optimal: 30-40% pour équilibre)", font=('Arial', 9), foreground='gray').grid(row=1, column=3, sticky='w', padx=10, pady=5)
        
        # Auto Risk
        self.auto_risk_var = tk.BooleanVar(value=True)
        self.auto_risk_check = ttk.Checkbutton(
            obj_grid, 
            text="Risque Automatique",
            variable=self.auto_risk_var,
            command=self.toggle_auto_risk
        )
        self.auto_risk_check.grid(row=2, column=0, columnspan=2, sticky='w', pady=5)
        
        # Section Recaves
        rebuy_frame = ttk.LabelFrame(main_container, text="💰 Gestion des Recaves", style='Card.TFrame')
        rebuy_frame.pack(fill='x', pady=(0, 20))
        
        rebuy_grid = ttk.Frame(rebuy_frame)
        rebuy_grid.pack(fill='x', padx=15, pady=15)
        
        ttk.Label(rebuy_grid, text="Nombre de Recaves Disponibles:", style='Heading.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        
        self.rebuys_var = tk.StringVar(value="3")
        self.rebuys_entry = ttk.Entry(rebuy_grid, textvariable=self.rebuys_var, width=10)
        self.rebuys_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Actions
        actions_frame = ttk.Frame(main_container)
        actions_frame.pack(fill='x', pady=(20, 0))
        
        self.reset_stats_btn = ttk.Button(
            actions_frame,
            text="🔄 Reset Statistiques",
            style='Warning.TButton',
            command=self.reset_statistics
        )
        self.reset_stats_btn.pack(side='left', padx=5)
        
        self.export_data_btn = ttk.Button(
            actions_frame,
            text="💾 Exporter Données",
            style='Accent.TButton',
            command=self.export_data
        )
        self.export_data_btn.pack(side='left', padx=5)
    
    def create_settings_tab(self):
        """Création de l'onglet Paramètres"""
        
        main_container = ttk.Frame(self.settings_tab)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Section Interface
        interface_frame = ttk.LabelFrame(main_container, text="🖥️ Interface", style='Card.TFrame')
        interface_frame.pack(fill='x', pady=(0, 20))
        
        interface_grid = ttk.Frame(interface_frame)
        interface_grid.pack(fill='x', padx=15, pady=15)
        
        # Langue
        ttk.Label(interface_grid, text="Langue:", style='Heading.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        
        self.language_combo = ttk.Combobox(
            interface_grid, 
            textvariable=self.language,
            values=["fr - Français", "en - English"],
            state="readonly",
            width=20
        )
        self.language_combo.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        self.language_combo.bind('<<ComboboxSelected>>', self.change_language)
        
        ttk.Label(interface_grid, text="Choisir la langue des menus et recommandations", font=('Arial', 9), foreground='gray').grid(row=0, column=2, sticky='w', padx=10, pady=5)
        
        # Thème
        ttk.Label(interface_grid, text="Thème:", style='Heading.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        
        self.theme_var = tk.StringVar(value="dark")
        self.theme_combo = ttk.Combobox(
            interface_grid, 
            textvariable=self.theme_var,
            values=["dark - Sombre", "light - Clair"],
            state="readonly",
            width=20
        )
        self.theme_combo.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        self.theme_combo.bind('<<ComboboxSelected>>', self.change_theme)
        
        ttk.Label(interface_grid, text="Mode sombre recommandé pour sessions longues", font=('Arial', 9), foreground='gray').grid(row=1, column=2, sticky='w', padx=10, pady=5)
        
        # Section OCR
        ocr_frame = ttk.LabelFrame(main_container, text="👁️ OCR & Capture", style='Card.TFrame')
        ocr_frame.pack(fill='x', pady=(0, 20))
        
        ocr_grid = ttk.Frame(ocr_frame)
        ocr_grid.pack(fill='x', padx=15, pady=15)
        
        # Intervalle OCR
        ttk.Label(ocr_grid, text="Intervalle OCR (ms):", style='Heading.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        
        self.ocr_interval_var = tk.StringVar(value="100")
        self.ocr_interval_entry = ttk.Entry(ocr_grid, textvariable=self.ocr_interval_var, width=10)
        self.ocr_interval_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(ocr_grid, text="Fréquence de capture d'écran (50-200ms optimal)", font=('Arial', 9), foreground='gray').grid(row=0, column=2, sticky='w', padx=10, pady=5)
        
        # Confiance OCR
        ttk.Label(ocr_grid, text="Seuil de Confiance (%):", style='Heading.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        
        self.ocr_confidence_var = tk.StringVar(value="80")
        self.ocr_confidence_entry = ttk.Entry(ocr_grid, textvariable=self.ocr_confidence_var, width=10)
        self.ocr_confidence_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(ocr_grid, text="Précision minimum requise (75-90% recommandé)", font=('Arial', 9), foreground='gray').grid(row=1, column=2, sticky='w', padx=10, pady=5)
        
        # Section Type de Table
        table_frame = ttk.LabelFrame(main_container, text="🏓 Type de Table", style='Card.TFrame')
        table_frame.pack(fill='x', pady=(0, 20))
        
        self.table_type_var = tk.StringVar(value="cashgame")
        
        cash_radio = ttk.Radiobutton(
            table_frame, 
            text="💰 Cash Game", 
            variable=self.table_type_var, 
            value="cashgame",
            command=self.change_table_type
        )
        cash_radio.pack(anchor='w', padx=15, pady=5)
        
        ttk.Label(table_frame, text="Partie d'argent classique sans élimination", font=('Arial', 9), foreground='gray').pack(anchor='w', padx=30, pady=(0, 5))
        
        tournament_radio = ttk.Radiobutton(
            table_frame, 
            text="🏆 Tournoi", 
            variable=self.table_type_var, 
            value="tournament",
            command=self.change_table_type
        )
        tournament_radio.pack(anchor='w', padx=15, pady=5)
        
        ttk.Label(table_frame, text="Utilise les calculs ICM pour élimination", font=('Arial', 9), foreground='gray').pack(anchor='w', padx=30, pady=(0, 5))
    
    def create_performance_tab(self):
        """Création de l'onglet Performance"""
        
        main_container = ttk.Frame(self.performance_tab)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Section Ressources
        resources_frame = ttk.LabelFrame(main_container, text="💻 Gestion des Ressources", style='Card.TFrame')
        resources_frame.pack(fill='x', pady=(0, 20))
        
        res_grid = ttk.Frame(resources_frame)
        res_grid.pack(fill='x', padx=15, pady=15)
        
        # CPU
        ttk.Label(res_grid, text="Limite CPU (%):", style='Heading.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        
        self.cpu_var = tk.DoubleVar(value=80.0)
        self.cpu_scale = ttk.Scale(res_grid, from_=10, to=100, orient='horizontal', variable=self.cpu_var, length=200)
        self.cpu_scale.grid(row=0, column=1, padx=10, pady=5)
        
        self.cpu_display = ttk.Label(res_grid, text="80%", style='Card.TLabel')
        self.cpu_display.grid(row=0, column=2, padx=10, pady=5)
        
        ttk.Label(res_grid, text="Usage CPU max pour calculs CFR (70-85% optimal)", font=('Arial', 9), foreground='gray').grid(row=0, column=3, sticky='w', padx=10, pady=5)
        
        # RAM
        ttk.Label(res_grid, text="Limite RAM (%):", style='Heading.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        
        self.ram_var = tk.DoubleVar(value=70.0)
        self.ram_scale = ttk.Scale(res_grid, from_=10, to=100, orient='horizontal', variable=self.ram_var, length=200)
        self.ram_scale.grid(row=1, column=1, padx=10, pady=5)
        
        self.ram_display = ttk.Label(res_grid, text="70%", style='Card.TLabel')
        self.ram_display.grid(row=1, column=2, padx=10, pady=5)
        
        ttk.Label(res_grid, text="Mémoire max pour base de données (60-80% optimal)", font=('Arial', 9), foreground='gray').grid(row=1, column=3, sticky='w', padx=10, pady=5)
        
        # GPU
        self.gpu_enabled_var = tk.BooleanVar(value=True)
        self.gpu_check = ttk.Checkbutton(
            res_grid, 
            text="🎮 GPU Activé",
            variable=self.gpu_enabled_var,
            command=self.toggle_gpu
        )
        self.gpu_check.grid(row=2, column=0, columnspan=2, sticky='w', pady=5)
        
        ttk.Label(res_grid, text="Accélération GPU pour Deep CFR (si PyTorch installé)", font=('Arial', 9), foreground='gray').grid(row=2, column=2, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Auto Resource Management
        self.auto_resource_var = tk.BooleanVar(value=True)
        self.auto_resource_check = ttk.Checkbutton(
            res_grid, 
            text="🤖 Gestion Automatique des Ressources",
            variable=self.auto_resource_var,
            command=self.toggle_auto_resources
        )
        self.auto_resource_check.grid(row=3, column=0, columnspan=2, sticky='w', pady=5)
        
        ttk.Label(res_grid, text="Ajuste automatiquement selon la charge système", font=('Arial', 9), foreground='gray').grid(row=3, column=2, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Section CFR
        cfr_frame = ttk.LabelFrame(main_container, text="🧠 Paramètres CFR", style='Card.TFrame')
        cfr_frame.pack(fill='x', pady=(0, 20))
        
        cfr_grid = ttk.Frame(cfr_frame)
        cfr_grid.pack(fill='x', padx=15, pady=15)
        
        # Itérations CFR
        ttk.Label(cfr_grid, text="Itérations CFR:", style='Heading.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        
        self.cfr_iterations_var = tk.StringVar(value="1000")
        self.cfr_iterations_entry = ttk.Entry(cfr_grid, textvariable=self.cfr_iterations_var, width=10)
        self.cfr_iterations_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(cfr_grid, text="Nombre de simulations par calcul (500-2000 optimal)", font=('Arial', 9), foreground='gray').grid(row=0, column=2, sticky='w', padx=10, pady=5)
        
        # Buckets d'abstraction
        ttk.Label(cfr_grid, text="Buckets d'Abstraction:", style='Heading.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        
        self.buckets_var = tk.StringVar(value="64")
        self.buckets_entry = ttk.Entry(cfr_grid, textvariable=self.buckets_var, width=10)
        self.buckets_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(cfr_grid, text="Groupes de mains similaires (32-128, 64 optimal)", font=('Arial', 9), foreground='gray').grid(row=1, column=2, sticky='w', padx=10, pady=5)
        
        # Deep CFR
        self.deep_cfr_var = tk.BooleanVar(value=False)
        self.deep_cfr_check = ttk.Checkbutton(
            cfr_grid, 
            text="🤖 Deep CFR (PyTorch)",
            variable=self.deep_cfr_var,
            command=self.toggle_deep_cfr
        )
        self.deep_cfr_check.grid(row=2, column=0, columnspan=2, sticky='w', pady=5)
        
        ttk.Label(cfr_grid, text="IA neuronale avancée (plus lent mais précis)", font=('Arial', 9), foreground='gray').grid(row=2, column=2, sticky='w', padx=10, pady=5)
        
        # Bouton Appliquer
        apply_frame = ttk.Frame(main_container)
        apply_frame.pack(fill='x', pady=(20, 0))
        
        self.apply_settings_btn = ttk.Button(
            apply_frame,
            text="✅ Appliquer les Paramètres",
            style='Success.TButton',
            command=self.apply_settings
        )
        self.apply_settings_btn.pack(pady=10)
    
    def setup_layout(self):
        """Organisation du layout"""
        
        # Layout principal
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Barre de titre
        self.title_frame.pack(fill='x', pady=(0, 15))
        self.title_label.pack(side='left')
        
        self.controls_frame.pack(side='right')
        self.start_stop_btn.pack(side='left', padx=5)
        self.status_label.pack(side='left', padx=15)
        
        # Notebook
        self.notebook.pack(fill='both', expand=True)
    
    def toggle_analysis(self):
        """Démarre/arrête l'analyse"""
        if not self.is_running:
            self.start_analysis()
        else:
            self.stop_analysis()
    
    def start_analysis(self):
        """Démarre l'analyse"""
        try:
            self.app_manager.start()
            self.is_running = True
            
            self.start_stop_btn.configure(text="⏹ Arrêter", style='Danger.TButton')
            self.status_label.configure(text="🟢 En cours", foreground='green')
            
            self.logger.info("Analyse démarrée depuis l'interface")
            
        except Exception as e:
            self.logger.error(f"Erreur démarrage: {e}")
            messagebox.showerror("Erreur", f"Impossible de démarrer l'analyse: {e}")
    
    def stop_analysis(self):
        """Arrête l'analyse"""
        try:
            self.app_manager.stop()
            self.is_running = False
            
            self.start_stop_btn.configure(text="🚀 Démarrer", style='Success.TButton')
            self.status_label.configure(text="🔴 Arrêté", foreground='red')
            
            self.logger.info("Analyse arrêtée depuis l'interface")
            
        except Exception as e:
            self.logger.error(f"Erreur arrêt: {e}")
    
    def update_interface_data(self):
        """Met à jour toutes les données de l'interface"""
        try:
            # État du jeu
            game_state = self.app_manager.get_current_state()
            if game_state:
                # Cartes héros
                if game_state.hero_cards and game_state.hero_cards != ("", ""):
                    self.hero_card1.configure(text=self.card_to_emoji(game_state.hero_cards[0]))
                    self.hero_card2.configure(text=self.card_to_emoji(game_state.hero_cards[1]))
                
                # Board
                for i, card_label in enumerate(self.board_cards):
                    if i < len(game_state.board_cards):
                        card_label.configure(text=self.card_to_emoji(game_state.board_cards[i]))
                    else:
                        card_label.configure(text="🂠")
                
                # Informations
                self.pot_label.configure(text=f"{game_state.pot_size:.2f}€")
                self.stack_label.configure(text=f"{game_state.hero_stack:.2f}€")
                
                # Blinds et antes
                blinds_text = f"{game_state.small_blind:.2f}€ / {game_state.big_blind:.2f}€"
                self.blinds_label.configure(text=blinds_text)
                
                # Antes si présentes
                if hasattr(game_state, 'ante') and game_state.ante > 0:
                    self.antes_label.configure(text=f"Ante: {game_state.ante:.2f}€")
                else:
                    self.antes_label.configure(text="")
                
                self.table_type_label.configure(text=game_state.table_type.title())
            
            # Recommandations dans l'onglet principal
            recommendation = self.app_manager.get_recommendation()
            if recommendation:
                action = recommendation.get('action_type', 'check').upper()
                self.main_action_display.configure(text=action)
                
                # Couleur selon l'action
                if action in ['FOLD']:
                    self.main_action_display.configure(foreground='red')
                elif action in ['CHECK', 'CALL']:
                    self.main_action_display.configure(foreground='orange')
                else:
                    self.main_action_display.configure(foreground='green')
                
                bet_size = recommendation.get('bet_size', 0.0)
                if bet_size > 0:
                    self.main_bet_size_label.configure(text=f"Taille: {bet_size:.2f}€")
                else:
                    self.main_bet_size_label.configure(text="")
                
                win_prob = recommendation.get('win_probability', 50.0)
                self.main_win_prob_label.configure(text=f"{win_prob:.1f}%")
                
                risk_level = recommendation.get('risk_level', 50.0)
                self.main_risk_label.configure(text=f"{risk_level:.0f}%")
                
                confidence = recommendation.get('confidence', 85.0)
                self.main_confidence_label.configure(text=f"{confidence:.0f}%")
                
                # Raisonnement
                reasoning = recommendation.get('reasoning', 'Analyse en cours...')
                self.main_reasoning_label.configure(text=reasoning)
                
                # Aussi mettre à jour l'onglet recommandations pour compatibilité
                if hasattr(self, 'action_display'):
                    self.action_display.configure(text=action)
                    if action in ['FOLD']:
                        self.action_display.configure(foreground='red')
                    elif action in ['CHECK', 'CALL']:
                        self.action_display.configure(foreground='orange')
                    else:
                        self.action_display.configure(foreground='green')
                    
                    self.bet_size_label.configure(text=f"Taille: {bet_size:.2f}€")
                    self.win_prob_label.configure(text=f"{win_prob:.1f}%")
                    self.win_prob_progress['value'] = win_prob
                    self.risk_label.configure(text=f"{risk_level:.0f}%")
                    self.risk_progress['value'] = risk_level
                    
                    self.reasoning_text.configure(state='normal')
                    self.reasoning_text.delete(1.0, tk.END)
                    self.reasoning_text.insert(1.0, reasoning)
                    self.reasoning_text.configure(state='disabled')
            
            # Statistiques dans l'onglet principal et onglet dédié
            stats = self.app_manager.get_statistics()
            if stats:
                hands_played = stats.get('hands_played', 0)
                hands_won = stats.get('hands_won', 0)
                win_rate = stats.get('win_rate', 0.0)
                performance_ratio = stats.get('performance_ratio', 0.0)
                
                # Statistiques onglet principal
                self.main_hands_label.configure(text=f"{hands_won} / {hands_played}")
                self.main_winrate_label.configure(text=f"{win_rate:.1f}%")
                self.main_performance_label.configure(text=f"{performance_ratio:.1f}%")
                
                # Statistiques onglet dédié pour compatibilité
                if hasattr(self, 'hands_played_value'):
                    self.hands_played_value.configure(text=str(hands_played))
                    self.hands_won_value.configure(text=str(hands_won))
                    self.win_rate_value.configure(text=f"{win_rate:.1f}%")
                    self.performance_ratio_value.configure(text=f"{performance_ratio:.1f}%")
            
        except Exception as e:
            self.logger.error(f"Erreur mise à jour interface: {e}")
    
    def card_to_emoji(self, card: str) -> str:
        """Convertit une carte en emoji"""
        if not card or len(card) < 2:
            return "🂠"
        
        rank = card[0].upper()
        suit = card[1].lower()
        
        # Mapping simplfiié
        if suit == 's':  # Spades
            return "♠️"
        elif suit == 'h':  # Hearts
            return "♥️"
        elif suit == 'd':  # Diamonds
            return "♦️"
        elif suit == 'c':  # Clubs
            return "♣️"
        
        return "🂠"
    
    def start_update_thread(self):
        """Démarre le thread de mise à jour"""
        def update_loop():
            while True:
                try:
                    if self.is_running:
                        self.root.after(0, self.update_interface_data)
                    time.sleep(0.5)  # Mise à jour toutes les 500ms
                except Exception as e:
                    self.logger.error(f"Erreur thread mise à jour: {e}")
                    time.sleep(1)
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    # Méthodes des callbacks
    def toggle_auto_target(self):
        state = 'disabled' if self.auto_target_var.get() else 'normal'
        self.hands_target_entry.configure(state=state)
    
    def update_risk_display(self, value):
        self.risk_display.configure(text=f"{float(value):.0f}%")
    
    def toggle_auto_risk(self):
        state = 'disabled' if self.auto_risk_var.get() else 'normal'
        self.risk_scale.configure(state=state)
    
    def change_language(self, event=None):
        # Implémentation du changement de langue
        pass
    
    def change_theme(self, event=None):
        # Implémentation du changement de thème
        pass
    
    def change_table_type(self):
        try:
            table_type = self.table_type_var.get()
            self.app_manager.update_settings({'table_type': table_type})
        except Exception as e:
            self.logger.error(f"Erreur changement type table: {e}")
    
    def toggle_gpu(self):
        try:
            gpu_enabled = self.gpu_enabled_var.get()
            self.app_manager.update_settings({'gpu_enabled': gpu_enabled})
        except Exception as e:
            self.logger.error(f"Erreur toggle GPU: {e}")
    
    def toggle_auto_resources(self):
        try:
            auto_mgmt = self.auto_resource_var.get()
            self.app_manager.update_settings({'auto_resource_management': auto_mgmt})
        except Exception as e:
            self.logger.error(f"Erreur toggle auto ressources: {e}")
    
    def toggle_deep_cfr(self):
        try:
            deep_cfr = self.deep_cfr_var.get()
            self.app_manager.update_settings({'deep_cfr_enabled': deep_cfr})
        except Exception as e:
            self.logger.error(f"Erreur toggle Deep CFR: {e}")
    
    def apply_settings(self):
        try:
            settings = {
                'cpu_usage_limit': self.cpu_var.get(),
                'ram_usage_limit': self.ram_var.get(),
                'gpu_enabled': self.gpu_enabled_var.get(),
                'auto_resource_management': self.auto_resource_var.get(),
                'cfr_iterations': int(self.cfr_iterations_var.get()),
                'abstraction_buckets': int(self.buckets_var.get()),
                'deep_cfr_enabled': self.deep_cfr_var.get(),
                'ocr_interval_ms': int(self.ocr_interval_var.get()),
                'ocr_confidence_threshold': float(self.ocr_confidence_var.get()) / 100.0
            }
            
            self.app_manager.update_settings(settings)
            messagebox.showinfo("Succès", "Paramètres appliqués avec succès!")
            
        except Exception as e:
            self.logger.error(f"Erreur application paramètres: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de l'application des paramètres: {e}")
    
    def reset_statistics(self):
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir remettre à zéro les statistiques?"):
            try:
                self.app_manager.database.clear_history()
                messagebox.showinfo("Succès", "Statistiques remises à zéro!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {e}")
    
    def export_data(self):
        try:
            filename = f"rtpa_export_{int(time.time())}.json"
            self.app_manager.database.export_data(filename)
            messagebox.showinfo("Succès", f"Données exportées vers {filename}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'export: {e}")
    
    def run(self):
        """Lance l'interface graphique"""
        try:
            self.logger.info("Lancement de l'interface graphique RTPA Studio")
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Erreur interface: {e}")
    
    def on_closing(self):
        """Gestion de la fermeture"""
        try:
            if self.is_running:
                self.stop_analysis()
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            self.logger.error(f"Erreur fermeture: {e}")
        finally:
            exit(0)