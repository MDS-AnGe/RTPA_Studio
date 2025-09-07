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
        """Création de l'onglet État du Jeu - Interface Moderne Style Poker"""
        
        # Container principal avec fond style poker
        main_container = tk.Frame(self.game_tab, bg='#0d4d20')  # Vert poker foncé
        main_container.pack(fill='both', expand=True)
        
        # Header avec titre stylé
        header_frame = tk.Frame(main_container, bg='#0d4d20', height=50)
        header_frame.pack(fill='x', pady=(10, 0))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🃏 TABLE DE POKER RTPA 🎯",
            font=('Arial', 18, 'bold'),
            fg='#ffdd44',
            bg='#0d4d20'
        )
        title_label.pack(pady=10)
        
        # Zone de jeu centrale style table elliptique
        game_area = tk.Frame(main_container, bg='#2d5a3d', relief='raised', bd=4)
        game_area.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Section Board (centre de la table)
        board_section = tk.Frame(game_area, bg='#2d5a3d')
        board_section.pack(pady=30)
        
        board_title = tk.Label(
            board_section,
            text="🎯 BOARD COMMUNAUTAIRE 🎯",
            font=('Arial', 14, 'bold'),
            fg='#ffdd44',
            bg='#2d5a3d'
        )
        board_title.pack(pady=(0, 15))
        
        self.board_cards_frame = tk.Frame(board_section, bg='#2d5a3d')
        self.board_cards_frame.pack()
        
        self.board_cards = []
        self.board_card_frames = []
        
        # Labels pour les streets
        street_names = ['FLOP', '', '', 'TURN', 'RIVER']
        
        for i in range(5):
            # Container pour carte + label
            card_container = tk.Frame(self.board_cards_frame, bg='#2d5a3d')
            card_container.pack(side='left', padx=8)
            
            # Label street
            if street_names[i]:
                street_label = tk.Label(
                    card_container, 
                    text=street_names[i], 
                    font=('Arial', 8, 'bold'), 
                    fg='#ffdd44', 
                    bg='#2d5a3d'
                )
                street_label.pack()
            
            # Frame carte avec effet 3D
            card_frame = tk.Frame(
                card_container,
                bg='white',
                relief='raised',
                bd=3,
                width=90,
                height=120
            )
            card_frame.pack(pady=2)
            card_frame.pack_propagate(False)
            
            # Label carte avec ombrage
            card_label = tk.Label(
                card_frame,
                text="🂠",
                font=('Arial', 32, 'bold'),
                fg='gray',
                bg='white',
                anchor='center'
            )
            card_label.pack(expand=True, fill='both')
            
            self.board_cards.append(card_label)
            self.board_card_frames.append(card_frame)
        
        # Section Hero Cards (en bas de la table)
        hero_section = tk.Frame(game_area, bg='#2d5a3d')
        hero_section.pack(side='bottom', pady=(20, 30))
        
        hero_title = tk.Label(
            hero_section,
            text="🂡 VOS CARTES 🂡",
            font=('Arial', 16, 'bold'),
            fg='#ff6b6b',
            bg='#2d5a3d'
        )
        hero_title.pack(pady=(0, 15))
        
        self.hero_cards_frame = tk.Frame(hero_section, bg='#2d5a3d')
        self.hero_cards_frame.pack()
        
        # Cartes Hero plus grandes et élégantes
        self.hero_card1_frame = tk.Frame(
            self.hero_cards_frame, 
            bg='white',
            relief='raised',
            bd=5,
            width=110,
            height=150
        )
        self.hero_card1_frame.pack(side='left', padx=20)
        self.hero_card1_frame.pack_propagate(False)
        
        self.hero_card1 = tk.Label(
            self.hero_card1_frame,
            text="🂠",
            font=('Arial', 40, 'bold'),
            fg='gray',
            bg='white',
            anchor='center'
        )
        self.hero_card1.pack(expand=True, fill='both')
        
        self.hero_card2_frame = tk.Frame(
            self.hero_cards_frame,
            bg='white',
            relief='raised',
            bd=5,
            width=110,
            height=150
        )
        self.hero_card2_frame.pack(side='left', padx=20)
        self.hero_card2_frame.pack_propagate(False)
        
        self.hero_card2 = tk.Label(
            self.hero_card2_frame,
            text="🂠",
            font=('Arial', 40, 'bold'),
            fg='gray',
            bg='white',
            anchor='center'
        )
        self.hero_card2.pack(expand=True, fill='both')
        
        # Section Informations de Jeu - Style Dashboard
        info_container = tk.Frame(main_container, bg='#1a1a1a')
        info_container.pack(fill='x', padx=20, pady=(0, 10))
        
        # Dashboard avec 4 colonnes d'informations
        dashboard = tk.Frame(info_container, bg='#1a1a1a', relief='raised', bd=2)
        dashboard.pack(fill='x', pady=10)
        
        # Pot (avec effet lumineux)
        pot_frame = tk.Frame(dashboard, bg='#2d5a3d', relief='raised', bd=3, width=150, height=80)
        pot_frame.pack(side='left', fill='y', padx=10, pady=10)
        pot_frame.pack_propagate(False)
        
        tk.Label(pot_frame, text="💰 POT", font=('Arial', 10, 'bold'), fg='#ffdd44', bg='#2d5a3d').pack(pady=5)
        self.pot_label = tk.Label(pot_frame, text="0.00€", font=('Arial', 16, 'bold'), fg='white', bg='#2d5a3d')
        self.pot_label.pack()
        
        # Stack
        stack_frame = tk.Frame(dashboard, bg='#2d5a3d', relief='raised', bd=3, width=150, height=80)
        stack_frame.pack(side='left', fill='y', padx=10, pady=10)
        stack_frame.pack_propagate(False)
        
        tk.Label(stack_frame, text="💵 STACK", font=('Arial', 10, 'bold'), fg='#ffdd44', bg='#2d5a3d').pack(pady=5)
        self.stack_label = tk.Label(stack_frame, text="0.00€", font=('Arial', 16, 'bold'), fg='white', bg='#2d5a3d')
        self.stack_label.pack()
        
        # Blinds
        blinds_frame = tk.Frame(dashboard, bg='#2d5a3d', relief='raised', bd=3, width=180, height=80)
        blinds_frame.pack(side='left', fill='y', padx=10, pady=10)
        blinds_frame.pack_propagate(False)
        
        tk.Label(blinds_frame, text="🎲 BLINDS", font=('Arial', 10, 'bold'), fg='#ffdd44', bg='#2d5a3d').pack(pady=5)
        self.blinds_label = tk.Label(blinds_frame, text="0.00€ / 0.00€", font=('Arial', 12, 'bold'), fg='white', bg='#2d5a3d')
        self.blinds_label.pack()
        self.antes_label = tk.Label(blinds_frame, text="", font=('Arial', 9), fg='#cccccc', bg='#2d5a3d')
        self.antes_label.pack()
        
        # Type de table
        type_frame = tk.Frame(dashboard, bg='#2d5a3d', relief='raised', bd=3, width=120, height=80)
        type_frame.pack(side='right', fill='y', padx=10, pady=10)
        type_frame.pack_propagate(False)
        
        tk.Label(type_frame, text="🏟️ TYPE", font=('Arial', 10, 'bold'), fg='#ffdd44', bg='#2d5a3d').pack(pady=5)
        self.table_type_label = tk.Label(type_frame, text="Cash Game", font=('Arial', 12, 'bold'), fg='white', bg='#2d5a3d')
        self.table_type_label.pack()
        
        # SECTION RECOMMANDATIONS MODERNISÉE
        recommendations_frame = tk.Frame(main_container, bg='#1a1a1a', relief='raised', bd=3)
        recommendations_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Header recommandations
        rec_header = tk.Frame(recommendations_frame, bg='#333333', height=40)
        rec_header.pack(fill='x')
        rec_header.pack_propagate(False)
        
        tk.Label(
            rec_header, 
            text="🎯 RECOMMANDATION NASH-CFR", 
            font=('Arial', 14, 'bold'), 
            fg='#ffdd44', 
            bg='#333333'
        ).pack(pady=10)
        
        # Action principale avec glow effect
        action_container = tk.Frame(recommendations_frame, bg='#1a1a1a')
        action_container.pack(fill='x', pady=20)
        
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
        
        # Couleurs personnalisées
        ttk.Label(interface_grid, text="Couleur d'accent:", style='Heading.TLabel').grid(row=2, column=0, sticky='w', pady=5)
        
        self.accent_color_var = tk.StringVar(value="blue")
        self.accent_combo = ttk.Combobox(
            interface_grid,
            textvariable=self.accent_color_var,
            values=["blue - Bleu", "green - Vert", "red - Rouge", "purple - Violet", "orange - Orange"],
            state="readonly",
            width=20
        )
        self.accent_combo.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        self.accent_combo.bind('<<ComboboxSelected>>', self.change_accent_color)
        
        ttk.Label(interface_grid, text="Couleur des boutons et éléments d'interface", font=('Arial', 9), foreground='gray').grid(row=2, column=2, sticky='w', padx=10, pady=5)
        
        # Opacité interface
        ttk.Label(interface_grid, text="Opacité Interface:", style='Heading.TLabel').grid(row=3, column=0, sticky='w', pady=5)
        
        self.opacity_var = tk.DoubleVar(value=1.0)
        self.opacity_scale = ttk.Scale(interface_grid, from_=0.7, to=1.0, orient='horizontal', variable=self.opacity_var, length=150, command=self.update_opacity_display)
        self.opacity_scale.grid(row=3, column=1, padx=10, pady=5)
        
        self.opacity_display = ttk.Label(interface_grid, text="100%", style='Card.TLabel')
        self.opacity_display.grid(row=3, column=2, sticky='w', padx=10, pady=5)
        
        # Police interface
        ttk.Label(interface_grid, text="Police Interface:", style='Heading.TLabel').grid(row=4, column=0, sticky='w', pady=5)
        
        self.font_var = tk.StringVar(value="arial")
        self.font_combo = ttk.Combobox(
            interface_grid,
            textvariable=self.font_var,
            values=["arial - Arial", "helvetica - Helvetica", "times - Times", "courier - Courier"],
            state="readonly",
            width=20
        )
        self.font_combo.grid(row=4, column=1, padx=10, pady=5, sticky='w')
        self.font_combo.bind('<<ComboboxSelected>>', self.change_font)
        
        ttk.Label(interface_grid, text="Arial recommandé pour lisibilité", font=('Arial', 9), foreground='gray').grid(row=4, column=2, sticky='w', padx=10, pady=5)
        
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
        
        # GPU avec gestion PyTorch
        gpu_frame = ttk.Frame(res_grid)
        gpu_frame.grid(row=2, column=0, columnspan=4, sticky='ew', pady=5)
        
        self.gpu_enabled_var = tk.BooleanVar(value=True)
        self.gpu_check = ttk.Checkbutton(
            gpu_frame, 
            text="🎮 GPU Activé",
            variable=self.gpu_enabled_var,
            command=self.toggle_gpu
        )
        self.gpu_check.pack(side='left')
        
        # Status PyTorch
        self.pytorch_status_label = ttk.Label(gpu_frame, text="Vérification PyTorch...", font=('Arial', 9))
        self.pytorch_status_label.pack(side='left', padx=(10, 5))
        
        # Bouton installation PyTorch
        self.pytorch_install_button = ttk.Button(
            gpu_frame,
            text="Installer PyTorch",
            command=self.install_pytorch,
            style='Accent.TButton'
        )
        self.pytorch_install_button.pack(side='left', padx=5)
        
        # Vérification initiale PyTorch
        self.check_pytorch_status()
        
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
        
        ttk.Label(cfr_grid, text="Monte Carlo simulations par décision. Plus élevé = précision ↑, vitesse ↓", font=('Arial', 9), foreground='gray').grid(row=0, column=2, sticky='w', padx=10, pady=5)
        
        # Buckets d'abstraction
        ttk.Label(cfr_grid, text="Buckets d'Abstraction:", style='Heading.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        
        self.buckets_var = tk.StringVar(value="64")
        self.buckets_entry = ttk.Entry(cfr_grid, textvariable=self.buckets_var, width=10)
        self.buckets_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(cfr_grid, text="Regroupement mains similaires. 64 = équilibre optimal performance/précision", font=('Arial', 9), foreground='gray').grid(row=1, column=2, sticky='w', padx=10, pady=5)
        
        # Profondeur CFR
        ttk.Label(cfr_grid, text="Profondeur CFR:", style='Heading.TLabel').grid(row=2, column=0, sticky='w', pady=5)
        
        self.cfr_depth_var = tk.StringVar(value="3")
        self.cfr_depth_combo = ttk.Combobox(cfr_grid, textvariable=self.cfr_depth_var, values=["1", "2", "3", "4", "5"], width=8, state="readonly")
        self.cfr_depth_combo.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(cfr_grid, text="Streets à analyser (1=Flop, 3=jusqu'à River). Plus = précis mais lent", font=('Arial', 9), foreground='gray').grid(row=2, column=2, sticky='w', padx=10, pady=5)
        
        # Epsilon exploration
        ttk.Label(cfr_grid, text="Epsilon Exploration:", style='Heading.TLabel').grid(row=3, column=0, sticky='w', pady=5)
        
        self.epsilon_var = tk.DoubleVar(value=0.1)
        self.epsilon_scale = ttk.Scale(cfr_grid, from_=0.01, to=0.5, orient='horizontal', variable=self.epsilon_var, length=150, command=self.update_epsilon_display)
        self.epsilon_scale.grid(row=3, column=1, padx=10, pady=5)
        
        self.epsilon_display = ttk.Label(cfr_grid, text="0.10", style='Card.TLabel')
        self.epsilon_display.grid(row=3, column=2, sticky='w', padx=10, pady=5)
        
        # Deep CFR
        self.deep_cfr_var = tk.BooleanVar(value=False)
        self.deep_cfr_check = ttk.Checkbutton(
            cfr_grid, 
            text="🤖 Deep CFR (Neural Networks)",
            variable=self.deep_cfr_var,
            command=self.toggle_deep_cfr
        )
        self.deep_cfr_check.grid(row=4, column=0, columnspan=2, sticky='w', pady=5)
        
        ttk.Label(cfr_grid, text="Réseaux neuronaux pour approximation. Nécessite PyTorch + beaucoup RAM", font=('Arial', 9), foreground='gray').grid(row=4, column=2, sticky='w', padx=10, pady=5)
        
        # CFR+
        self.cfr_plus_var = tk.BooleanVar(value=True)
        self.cfr_plus_check = ttk.Checkbutton(
            cfr_grid, 
            text="⚡ CFR+ (Linear CFR)",
            variable=self.cfr_plus_var,
            command=self.toggle_cfr_plus
        )
        self.cfr_plus_check.grid(row=5, column=0, columnspan=2, sticky='w', pady=5)
        
        ttk.Label(cfr_grid, text="Amélioration CFR standard. Convergence plus rapide, recommandé", font=('Arial', 9), foreground='gray').grid(row=5, column=2, sticky='w', padx=10, pady=5)
        
        # Section Export/Import
        data_frame = ttk.LabelFrame(main_container, text="📁 Gestion des Données", style='Card.TFrame')
        data_frame.pack(fill='x', pady=(0, 20))
        
        data_grid = ttk.Frame(data_frame)
        data_grid.pack(fill='x', padx=15, pady=15)
        
        # Export données complètes
        ttk.Label(data_grid, text="Export Base CFR:", style='Heading.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        
        export_frame = ttk.Frame(data_grid)
        export_frame.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky='w')
        
        ttk.Button(
            export_frame,
            text="📤 Exporter Tout",
            command=self.export_database,
            style='Accent.TButton'
        ).pack(side='left', padx=(0, 5))
        
        ttk.Label(export_frame, text="Sauvegarde complète (CFR + données + stats)", font=('Arial', 9), foreground='gray').pack(side='left', padx=5)
        
        # Import données complètes
        ttk.Label(data_grid, text="Import Base CFR:", style='Heading.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        
        import_frame = ttk.Frame(data_grid)
        import_frame.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky='w')
        
        ttk.Button(
            import_frame,
            text="📥 Importer Tout",
            command=self.import_database,
            style='Accent.TButton'
        ).pack(side='left', padx=(0, 5))
        
        ttk.Label(import_frame, text="Restaure apprentissage CFR complet d'une session précédente", font=('Arial', 9), foreground='gray').pack(side='left', padx=5)
        
        # Statistiques export
        ttk.Label(data_grid, text="Statut Données:", style='Heading.TLabel').grid(row=2, column=0, sticky='w', pady=5)
        
        self.data_status_label = ttk.Label(data_grid, text="Prêt pour export/import", font=('Arial', 9), foreground='blue')
        self.data_status_label.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
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
                # Cartes héros avec couleurs
                if game_state.hero_cards and game_state.hero_cards != ("", ""):
                    card1_text, card1_color = self.card_to_visual(game_state.hero_cards[0])
                    self.hero_card1.configure(text=card1_text, foreground=card1_color)
                    
                    card2_text, card2_color = self.card_to_visual(game_state.hero_cards[1])
                    self.hero_card2.configure(text=card2_text, foreground=card2_color)
                
                # Board avec couleurs
                for i, card_label in enumerate(self.board_cards):
                    if i < len(game_state.board_cards) and game_state.board_cards[i]:
                        card_text, card_color = self.card_to_visual(game_state.board_cards[i])
                        card_label.configure(text=card_text, foreground=card_color)
                    else:
                        card_label.configure(text="[ ? ]", foreground="black")
                
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
    
    def card_to_visual(self, card_str):
        """Convertit une carte string en affichage visuel réaliste"""
        if not card_str or len(card_str) != 2:
            return "[ ? ]", "black"
        
        rank = card_str[0].upper()
        suit = card_str[1].lower()
        
        # Symboles des couleurs
        suit_symbols = {
            's': '♠',  # Piques (noir)
            'h': '♥',  # Coeurs (rouge)
            'd': '♦',  # Carreaux (rouge)
            'c': '♣'   # Trèfles (noir)
        }
        
        # Couleurs
        suit_colors = {
            's': 'black',
            'h': 'red',
            'd': 'red',
            'c': 'black'
        }
        
        # Conversion des rangs
        rank_display = {
            'T': '10'
        }.get(rank, rank)
        
        if suit in suit_symbols:
            symbol = suit_symbols[suit]
            color = suit_colors[suit]
            return f"{rank_display}{symbol}", color
        
        return "[ ? ]", "black"
    
    def card_to_emoji(self, card: str) -> str:
        """Conversion carte vers format texte pour compatibilité"""
        card_text, color = self.card_to_visual(card)
        return card_text
    
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
        """Change le thème de l'interface"""
        try:
            theme = self.theme_var.get()
            
            # Application du thème
            if theme == "dark":
                # Thème sombre
                self.style.theme_use('clam')  # Base theme
                self.style.configure('TFrame', background='#2b2b2b')
                self.style.configure('TLabel', background='#2b2b2b', foreground='white')
                self.style.configure('TLabelFrame', background='#2b2b2b', foreground='white')
                self.style.configure('TButton', background='#404040', foreground='white')
                self.style.configure('TEntry', foreground='white', fieldbackground='#404040')
                self.style.configure('TCombobox', foreground='white', fieldbackground='#404040')
                self.style.configure('TCheckbutton', background='#2b2b2b', foreground='white')
                self.style.configure('TScale', background='#2b2b2b')
                
                # Configuration de la fenêtre principale
                self.root.configure(bg='#2b2b2b')
                
            else:  # light theme
                # Thème clair
                self.style.theme_use('default')
                self.style.configure('TFrame', background='white')
                self.style.configure('TLabel', background='white', foreground='black')
                self.style.configure('TLabelFrame', background='white', foreground='black')
                self.style.configure('TButton', background='#e0e0e0', foreground='black')
                self.style.configure('TEntry', foreground='black', fieldbackground='white')
                self.style.configure('TCombobox', foreground='black', fieldbackground='white')
                self.style.configure('TCheckbutton', background='white', foreground='black')
                self.style.configure('TScale', background='white')
                
                # Configuration de la fenêtre principale
                self.root.configure(bg='white')
            
            self.logger.info(f"Thème changé vers: {theme}")
            
        except Exception as e:
            self.logger.error(f"Erreur changement thème: {e}")
    
    def change_accent_color(self, event=None):
        """Change la couleur d'accent de l'interface"""
        try:
            color = self.accent_color_var.get().split(' - ')[0]
            
            # Mapping des couleurs
            color_map = {
                'blue': '#0078d4',
                'green': '#00b294',
                'red': '#d13438',
                'purple': '#8764b8',
                'orange': '#ff8c00'
            }
            
            accent_color = color_map.get(color, '#0078d4')
            
            # Application de la couleur d'accent
            self.style.configure('Accent.TButton', background=accent_color, foreground='white')
            self.style.configure('Success.TButton', background=accent_color, foreground='white')
            self.style.configure('Card.TFrame', borderwidth=1, relief='solid')
            self.style.configure('Heading.TLabel', foreground=accent_color, font=('Arial', 10, 'bold'))
            
            # Sauvegarde de la préférence
            self.app_manager.update_settings({'accent_color': color})
            
            self.logger.info(f"Couleur d'accent changée vers: {color}")
            
        except Exception as e:
            self.logger.error(f"Erreur changement couleur d'accent: {e}")
    
    def change_font(self, event=None):
        """Change la police de l'interface"""
        try:
            font_name = self.font_var.get().split(' - ')[0]
            
            # Application de la nouvelle police
            self.style.configure('TLabel', font=(font_name, 9))
            self.style.configure('TButton', font=(font_name, 9))
            self.style.configure('TEntry', font=(font_name, 9))
            self.style.configure('TCombobox', font=(font_name, 9))
            self.style.configure('Heading.TLabel', font=(font_name, 10, 'bold'))
            
            # Sauvegarde de la préférence
            self.app_manager.update_settings({'interface_font': font_name})
            
            self.logger.info(f"Police changée vers: {font_name}")
            
        except Exception as e:
            self.logger.error(f"Erreur changement police: {e}")
    
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
    
    def check_pytorch_status(self):
        """Vérifie si PyTorch est installé et détecte CUDA"""
        gpu_info = []
        pytorch_info = []
        
        # Vérification PyTorch
        try:
            import torch
            version = torch.__version__
            pytorch_info.append(f"PyTorch {version}")
            
            # Vérification CUDA PyTorch
            if torch.cuda.is_available():
                cuda_version = torch.version.cuda
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "GPU Inconnu"
                
                pytorch_info.append(f"CUDA {cuda_version}")
                gpu_info.append(f"{gpu_count}x {gpu_name}")
                
                status_text = f"✅ {' + '.join(pytorch_info)}"
                self.pytorch_status_label.configure(text=status_text, foreground='green')
                self.pytorch_install_button.configure(text="✅ Installé", state='disabled')
            else:
                # PyTorch installé mais pas CUDA
                status_text = f"⚠️ PyTorch {version} (CPU seulement)"
                self.pytorch_status_label.configure(text=status_text, foreground='orange')
                self.pytorch_install_button.configure(text="Installer CUDA", state='normal')
                
        except ImportError:
            # PyTorch pas installé
            self.pytorch_status_label.configure(text="❌ PyTorch non installé", foreground='red')
            self.pytorch_install_button.configure(text="Installer PyTorch", state='normal')
            
        except Exception as e:
            self.pytorch_status_label.configure(text="⚠️ Erreur vérification", foreground='gray')
            self.pytorch_install_button.configure(text="Réessayer", state='normal')
        
        # Vérification système CUDA (sans PyTorch)
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # NVIDIA GPU détecté, extraire version CUDA
                output_lines = result.stdout.split('\n')
                cuda_line = next((line for line in output_lines if 'CUDA Version:' in line), None)
                if cuda_line:
                    cuda_version = cuda_line.split('CUDA Version: ')[1].split()[0]
                    gpu_info.append(f"Driver CUDA {cuda_version}")
                    
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # Pas de GPU NVIDIA ou pas de drivers
            pass
        
        # Affichage détaillé des infos GPU si disponibles
        if gpu_info:
            gpu_details = " | ".join(gpu_info)
            # Optionnel: afficher dans un label séparé ou tooltip
    
    def install_pytorch(self):
        """Installe PyTorch"""
        def install_thread():
            try:
                self.pytorch_install_button.configure(text="Installation...", state='disabled')
                self.pytorch_status_label.configure(text="Installation en cours...", foreground='blue')
                
                import subprocess
                import sys
                
                # Installation PyTorch CPU par défaut
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio"
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    self.root.after(0, self._pytorch_install_success)
                else:
                    error_msg = result.stderr or "Erreur inconnue"
                    self.root.after(0, lambda: self._pytorch_install_error(error_msg))
                    
            except subprocess.TimeoutExpired:
                self.root.after(0, lambda: self._pytorch_install_error("Timeout lors de l'installation"))
            except Exception as e:
                self.root.after(0, lambda: self._pytorch_install_error(str(e)))
        
        import threading
        install_th = threading.Thread(target=install_thread, daemon=True)
        install_th.start()
    
    def _pytorch_install_success(self):
        """Callback succès installation PyTorch"""
        self.pytorch_status_label.configure(text="✅ Installation réussie", foreground='green')
        self.pytorch_install_button.configure(text="Installé", state='disabled')
        messagebox.showinfo("Succès", "PyTorch installé avec succès! Redémarrez l'application pour activer Deep CFR.")
        
        # Re-vérification
        self.root.after(2000, self.check_pytorch_status)
    
    def _pytorch_install_error(self, error_msg):
        """Callback erreur installation PyTorch"""
        self.pytorch_status_label.configure(text="❌ Échec installation", foreground='red')
        self.pytorch_install_button.configure(text="Réessayer", state='normal')
        messagebox.showerror("Erreur", f"Échec installation PyTorch:\n{error_msg}")
    
    def toggle_cfr_plus(self):
        try:
            cfr_plus = self.cfr_plus_var.get()
            self.app_manager.update_settings({'cfr_plus_enabled': cfr_plus})
        except Exception as e:
            self.logger.error(f"Erreur activation CFR+: {e}")
    
    def change_accent_color(self, event=None):
        try:
            color = self.accent_color_var.get().split(' - ')[0]
            # Implémentation changement couleur d'accent
            self.app_manager.update_settings({'accent_color': color})
        except Exception as e:
            self.logger.error(f"Erreur changement couleur: {e}")
    
    def update_epsilon_display(self, value):
        self.epsilon_display.configure(text=f"{float(value):.2f}")
    
    def update_opacity_display(self, value):
        opacity_percent = int(float(value) * 100)
        self.opacity_display.configure(text=f"{opacity_percent}%")
        # Appliquer l'opacité à la fenêtre
        try:
            self.root.attributes('-alpha', float(value))
        except Exception:
            pass  # Certains systèmes ne supportent pas l'opacité
    
    def export_database(self):
        """Exporte la base de données complète"""
        try:
            from tkinter import filedialog
            
            # Sélection du fichier de destination
            filename = filedialog.asksaveasfilename(
                title="Exporter Base de Données CFR",
                defaultextension=".json",
                filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
            )
            
            if filename:
                self.data_status_label.configure(text="Export en cours...", foreground='orange')
                
                # Export avec moteur CFR
                cfr_engine = getattr(self.app_manager, 'cfr_engine', None)
                success = self.app_manager.database.export_complete_data(filename, cfr_engine)
                
                if success:
                    self.data_status_label.configure(text="✅ Export réussi", foreground='green')
                    messagebox.showinfo("Succès", f"Base de données exportée vers:\n{filename}\n\nCette sauvegarde contient tous vos apprentissages CFR!")
                else:
                    self.data_status_label.configure(text="❌ Export échoué", foreground='red')
                    messagebox.showerror("Erreur", "Échec de l'export de la base de données")
            else:
                self.data_status_label.configure(text="Export annulé", foreground='gray')
                
        except Exception as e:
            self.logger.error(f"Erreur export database: {e}")
            self.data_status_label.configure(text="❌ Erreur export", foreground='red')
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")
    
    def import_database(self):
        """Importe une base de données complète"""
        try:
            from tkinter import filedialog
            
            # Confirmation avant import
            result = messagebox.askyesno(
                "Import Base CFR",
                "⚠️ Cette opération va remplacer toutes vos données actuelles par celles du fichier d'import.\n\nVoulez-vous continuer?"
            )
            
            if not result:
                return
            
            # Sélection du fichier source
            filename = filedialog.askopenfilename(
                title="Importer Base de Données CFR",
                filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
            )
            
            if filename:
                self.data_status_label.configure(text="Import en cours...", foreground='orange')
                
                # Import avec moteur CFR
                cfr_engine = getattr(self.app_manager, 'cfr_engine', None)
                success = self.app_manager.database.import_complete_data(filename, cfr_engine)
                
                if success:
                    self.data_status_label.configure(text="✅ Import réussi", foreground='green')
                    messagebox.showinfo("Succès", f"Base de données importée depuis:\n{filename}\n\nTous vos apprentissages CFR ont été restaurés!")
                else:
                    self.data_status_label.configure(text="❌ Import échoué", foreground='red')
                    messagebox.showerror("Erreur", "Échec de l'import de la base de données")
            else:
                self.data_status_label.configure(text="Import annulé", foreground='gray')
                
        except Exception as e:
            self.logger.error(f"Erreur import database: {e}")
            self.data_status_label.configure(text="❌ Erreur import", foreground='red')
            messagebox.showerror("Erreur", f"Erreur lors de l'import: {e}")
    
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