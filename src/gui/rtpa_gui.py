"""
Interface graphique de RTPA Studio
Utilise CustomTkinter pour une interface moderne
"""

import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import threading
import time
from typing import Dict, Any, Optional, List

# Configuration CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RTAPGUIWindow:
    """Interface graphique principale de RTPA Studio"""
    
    def __init__(self, app_manager):
        """Initialise l'interface graphique"""
        self.app_manager = app_manager
        self.running = False
        self.update_thread = None
        
        # Variables pour le stockage des éléments GUI
        self.players_list_frame = None
        self.active_players_count = None
        self.hero_name_label = None
        self.hero_stack_label = None
        self.hero_position_label = None
        
        # Fenêtre principale
        self.root = ctk.CTk()
        self.root.title("RTPA Studio - Real-Time Poker Assistant")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Variables de contrôle pour les sliders
        self.cpu_limit = None
        self.ram_limit = None
        self.cpu_value_label = None
        self.ram_value_label = None
        
        # Interface utilisateur
        self.create_interface()
        
        # Configuration de l'événement de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_interface(self):
        """Crée tous les éléments de l'interface"""
        
        # Container principal pour l'affichage structuré
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame de contrôle compact en haut
        self.controls_frame = ctk.CTkFrame(self.main_frame, height=80)
        self.controls_frame.pack(fill='x', pady=(0, 10))
        
        # Ligne 1: Statut principal - Plus compact
        self.status_label = ctk.CTkLabel(
            self.controls_frame,
            text="🎯 Real-Time Poker Assistant (CFR/Nash)",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.status_label.pack(pady=(10, 2))
        
        # Ligne 2: Activité du système - Espacement ultra-réduit
        self.activity_status_label = ctk.CTkLabel(
            self.controls_frame,
            text="Surveillance active",
            font=ctk.CTkFont(size=13),
            text_color="#666666"  # Gris plus foncé pour meilleure lisibilité
        )
        self.activity_status_label.pack(pady=(1, 0))
        
        # Ligne 3: Temps restant CFR - Collé à la ligne précédente
        self.cfr_time_label = ctk.CTkLabel(
            self.controls_frame,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="black"  # Noir pour meilleure lisibilité
        )
        self.cfr_time_label.pack(pady=(1, 3))
        
        # Notebook avec onglets
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Onglet 1: Tableau de Bord (principal)
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="📊 Tableau de Bord")
        self.create_dashboard_tab()
        
        # Onglet 2: Options
        self.options_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.options_tab, text="⚙️ Options")
        self.create_options_tab()
        
        # Onglet 3: Paramètres
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="🔧 Paramètres")
        self.create_settings_tab()
        
        # Onglet 4: Performance
        self.performance_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.performance_tab, text="⚡ Performance")
        self.create_performance_tab()
        
        # Onglet 5: Version (dernier à droite)
        self.version_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.version_tab, text="📌 Version")
        self.create_version_tab()
        
        # Charger les paramètres sauvegardés après création des éléments
        self.load_saved_settings()
    
    def create_dashboard_tab(self):
        """Création de l'onglet Tableau de Bord complet (état du jeu + recommandations + statistiques)"""
        
        # Frame principal optimisé (plus compact)
        main_container = ttk.Frame(self.dashboard_tab)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # SECTION 1: CARTES (Main et Board côte à côte)
        cards_container = ttk.Frame(main_container)
        cards_container.pack(fill='x', pady=(0, 10))
        
        # Section Main (compacte, à gauche)
        hero_frame = ttk.LabelFrame(cards_container, text="🂡 Main", style='Card.TFrame')
        hero_frame.pack(side='left', padx=(0, 10), fill='y')
        
        self.hero_cards_frame = tk.Frame(hero_frame, bg='#dbdbdb')
        self.hero_cards_frame.pack(padx=8, pady=10)
        
        # Cartes visuelles Main
        self.hero_card1_frame = tk.Frame(
            self.hero_cards_frame, 
            bg='#dbdbdb', relief='raised', bd=2, width=90, height=120
        )
        self.hero_card1_frame.pack(side='left', padx=5)
        self.hero_card1_frame.pack_propagate(False)
        
        self.hero_card1 = tk.Label(
            self.hero_card1_frame, text="🂠", font=('Arial', 28, 'bold'),
            fg='#5a5a5a', bg='#dbdbdb', anchor='center'
        )
        self.hero_card1.pack(expand=True, fill='both')
        
        self.hero_card2_frame = tk.Frame(
            self.hero_cards_frame, 
            bg='#dbdbdb', relief='raised', bd=2, width=90, height=120
        )
        self.hero_card2_frame.pack(side='left', padx=5)
        self.hero_card2_frame.pack_propagate(False)
        
        self.hero_card2 = tk.Label(
            self.hero_card2_frame, text="🂠", font=('Arial', 28, 'bold'),
            fg='#5a5a5a', bg='#dbdbdb', anchor='center'
        )
        self.hero_card2.pack(expand=True, fill='both')
        
        # Section Board (compacte, au milieu)
        board_frame = ttk.LabelFrame(cards_container, text="🃏 Board", style='Card.TFrame')
        board_frame.pack(side='left', padx=(0, 10), fill='both', expand=True)
        
        # Layout horizontal pour les 5 cartes du board
        self.board_cards_frame = tk.Frame(board_frame, bg='#dbdbdb')
        self.board_cards_frame.pack(padx=8, pady=10)
        
        # Créer 5 cartes du board (plus petites que les cartes main)
        self.board_cards = []
        for i in range(5):
            card_frame = tk.Frame(
                self.board_cards_frame, 
                bg='#dbdbdb', relief='raised', bd=2, width=70, height=95
            )
            card_frame.pack(side='left', padx=3)
            card_frame.pack_propagate(False)
            
            card_label = tk.Label(
                card_frame, text="🂠", font=('Arial', 20, 'bold'),
                fg='#5a5a5a', bg='#dbdbdb', anchor='center'
            )
            card_label.pack(expand=True, fill='both')
            self.board_cards.append(card_label)
        
        # SECTION 2: LAYOUT PRINCIPAL AVEC COLONNES
        columns_container = ttk.Frame(main_container)
        columns_container.pack(fill='both', expand=True)
        
        # Colonne gauche: Informations principales
        left_column = ttk.Frame(columns_container)
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # SECTION 2A: INFORMATIONS DE TABLE
        table_info_frame = ttk.LabelFrame(left_column, text="💰 POT ACTUEL", style='Card.TFrame')
        table_info_frame.pack(fill='x', pady=(0, 10))
        
        # Pot size centré et gros
        self.pot_value = tk.Label(table_info_frame, text="0.0", font=('Arial', 32, 'bold'),
                                 fg='#00b300', bg='#f0f0f0')
        self.pot_value.pack(pady=15)
        
        # Infos complémentaires en ligne
        info_line = tk.Frame(table_info_frame, bg='#f0f0f0')
        info_line.pack(fill='x', padx=15, pady=(0, 15))
        
        tk.Label(info_line, text="Blinds:", font=('Arial', 9), bg='#f0f0f0').pack(side='left')
        self.blinds_label = tk.Label(info_line, text="0.00€ / 0.00€", font=('Arial', 9, 'bold'), 
                                    bg='#f0f0f0', fg='#666')
        self.blinds_label.pack(side='left', padx=(5, 20))
        
        tk.Label(info_line, text="Antes:", font=('Arial', 9), bg='#f0f0f0').pack(side='left')
        self.antes_label = tk.Label(info_line, text="0.00€", font=('Arial', 9, 'bold'), 
                                   bg='#f0f0f0', fg='#666')
        self.antes_label.pack(side='left', padx=(5, 20))
        
        # Type de jeu à droite
        type_frame = tk.Frame(info_line, bg='#f0f0f0')
        type_frame.pack(side='right')
        self.game_type_label = tk.Label(type_frame, text="cashgame", font=('Arial', 9, 'italic'), 
                                       bg='#f0f0f0', fg='#666')
        self.game_type_label.pack()
        
        # SECTION 2B: RECOMMANDATION
        rec_frame = ttk.LabelFrame(left_column, text="🎯 RECOMMANDATION", style='Card.TFrame')
        rec_frame.pack(fill='x', pady=(0, 10))
        
        # Action recommandée en gros
        self.action_label = tk.Label(rec_frame, text="---", font=('Arial', 24, 'bold'),
                                    fg='#ff6600', bg='#f0f0f0')
        self.action_label.pack(pady=(10, 5))
        
        # Détails recommandation en ligne
        rec_details = tk.Frame(rec_frame, bg='#f0f0f0')
        rec_details.pack(fill='x', padx=15, pady=(0, 15))
        
        # Probabilité de victoire et taille de mise
        left_rec = tk.Frame(rec_details, bg='#f0f0f0')
        left_rec.pack(side='left')
        
        tk.Label(left_rec, text="Victoire:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w')
        self.win_prob_label = tk.Label(left_rec, text="--", font=('Arial', 10, 'bold'), 
                                      fg='#00b300', bg='#f0f0f0')
        self.win_prob_label.pack(anchor='w')
        
        # Niveau de risque au centre
        center_rec = tk.Frame(rec_details, bg='#f0f0f0')
        center_rec.pack(side='left', padx=30)
        
        tk.Label(center_rec, text="Risque:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w')
        self.risk_label = tk.Label(center_rec, text="--", font=('Arial', 10, 'bold'), 
                                  fg='#ff3300', bg='#f0f0f0')
        self.risk_label.pack(anchor='w')
        
        # Confiance à droite
        right_rec = tk.Frame(rec_details, bg='#f0f0f0')
        right_rec.pack(side='right')
        
        tk.Label(right_rec, text="Confiance:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w')
        self.confidence_label = tk.Label(right_rec, text="--", font=('Arial', 10, 'bold'), 
                                        fg='#0066ff', bg='#f0f0f0')
        self.confidence_label.pack(anchor='w')
        
        # Raisonnement (séparé et plus visible)
        reasoning_frame = tk.Frame(rec_frame, bg='#f8f8f8', relief='sunken', bd=1)
        reasoning_frame.pack(fill='x', padx=15, pady=(5, 15))
        
        tk.Label(reasoning_frame, text="💭 Raisonnement:", font=('Arial', 9, 'bold'),
                bg='#f8f8f8').pack(anchor='w', padx=8, pady=(5, 2))
        
        self.reasoning_label = tk.Label(reasoning_frame, text="En attente d'analyse...", 
                                      font=('Arial', 9), bg='#f8f8f8', fg='#444', 
                                      wraplength=400, justify='left')
        self.reasoning_label.pack(anchor='w', padx=8, pady=(0, 8))
        
        # Colonne droite: Informations joueurs
        right_column = ttk.Frame(columns_container)
        right_column.pack(side='right', fill='y', padx=(0, 0))
        
        # SECTION 4A: MES INFORMATIONS
        hero_info_frame = ttk.LabelFrame(right_column, text="👤 MOI", style='Card.TFrame')
        hero_info_frame.pack(fill='x', pady=(0, 10))
        
        # Pseudo
        pseudo_frame = tk.Frame(hero_info_frame, bg='#f0f0f0')
        pseudo_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(pseudo_frame, text="Pseudo:", font=('Arial', 10), bg='#f0f0f0').pack(side='left')
        self.hero_name_label = tk.Label(pseudo_frame, text="---", font=('Arial', 10, 'bold'), 
                                       bg='#f0f0f0')
        self.hero_name_label.pack(side='left', padx=(10, 0))
        
        # Stack
        stack_frame = tk.Frame(hero_info_frame, bg='#f0f0f0')
        stack_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(stack_frame, text="Mon Stack:", font=('Arial', 10), bg='#f0f0f0').pack(side='left')
        self.hero_stack_label = tk.Label(stack_frame, text="0.00€", font=('Arial', 10, 'bold'), 
                                        bg='#f0f0f0')
        self.hero_stack_label.pack(side='left', padx=(10, 0))
        
        # Position
        pos_frame = tk.Frame(hero_info_frame, bg='#f0f0f0')
        pos_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(pos_frame, text="Position:", font=('Arial', 10), bg='#f0f0f0').pack(side='left')
        self.hero_position_label = tk.Label(pos_frame, text="---", font=('Arial', 10, 'bold'), 
                                           bg='#f0f0f0')
        self.hero_position_label.pack(side='left', padx=(10, 0))
        
        # SECTION 4B: AUTRES JOUEURS ACTIFS
        players_frame = ttk.LabelFrame(right_column, text="👥 AUTRES JOUEURS", style='Card.TFrame')
        players_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Compteur de joueurs actifs en haut
        players_header = tk.Frame(players_frame, bg='#f0f0f0')
        players_header.pack(fill='x', padx=5, pady=5)
        
        tk.Label(players_header, text="Actifs:", font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(side='left')
        self.active_players_count = tk.Label(players_header, text="0/9", font=('Arial', 10, 'bold'), 
                                            fg='#00b300', bg='#f0f0f0')
        self.active_players_count.pack(side='left', padx=(5, 0))
        
        # Frame simple pour la liste des joueurs (sans scroll)
        self.players_list_frame = tk.Frame(players_frame, bg='#f0f0f0')
        self.players_list_frame.pack(fill='both', expand=True, padx=5, pady=(0, 10))
        
        # Créer la liste des joueurs (vide par défaut)
        self.create_players_display()
        
        # SECTION 4C: STATISTIQUES
        stats_frame = ttk.LabelFrame(right_column, text="📊 STATISTIQUES", style='Card.TFrame')
        stats_frame.pack(fill='x')
        
        # Ligne 1: Taux de victoire
        win_rate_frame = tk.Frame(stats_frame, bg='#f0f0f0')
        win_rate_frame.pack(fill='x', padx=10, pady=2)
        tk.Label(win_rate_frame, text="TAUX DE VICTOIRE", font=('Arial', 8, 'bold'), bg='#f0f0f0').pack()
        self.win_rate_value = tk.Label(win_rate_frame, text="0.0%", font=('Arial', 12, 'bold'), 
                                      fg='#00b300', bg='#f0f0f0')
        self.win_rate_value.pack()
        
        # Ligne 2: Mains
        hands_frame = tk.Frame(stats_frame, bg='#f0f0f0')
        hands_frame.pack(fill='x', padx=10, pady=2)
        
        played_frame = tk.Frame(hands_frame, bg='#f0f0f0')
        played_frame.pack(side='left', fill='x', expand=True)
        tk.Label(played_frame, text="🎮 Jouées", font=('Arial', 8), bg='#f0f0f0').pack()
        self.hands_played = tk.Label(played_frame, text="0", font=('Arial', 10, 'bold'), bg='#f0f0f0')
        self.hands_played.pack()
        
        won_frame = tk.Frame(hands_frame, bg='#f0f0f0')
        won_frame.pack(side='right', fill='x', expand=True)
        tk.Label(won_frame, text="✅ Gagnées", font=('Arial', 8), bg='#f0f0f0').pack()
        self.hands_won = tk.Label(won_frame, text="0", font=('Arial', 10, 'bold'), fg='#00b300', bg='#f0f0f0')
        self.hands_won.pack()
        
        # Ligne 3: Performance vs attendu
        perf_frame = tk.Frame(stats_frame, bg='#f0f0f0')
        perf_frame.pack(fill='x', padx=10, pady=(2, 10))
        
        expected_frame = tk.Frame(perf_frame, bg='#f0f0f0')
        expected_frame.pack(side='left', fill='x', expand=True)
        tk.Label(expected_frame, text="🎯 Attendu", font=('Arial', 8), bg='#f0f0f0').pack()
        self.expected_rate = tk.Label(expected_frame, text="0.7%", font=('Arial', 10, 'bold'), 
                                     fg='#666', bg='#f0f0f0')
        self.expected_rate.pack()
        
        performance_frame = tk.Frame(perf_frame, bg='#f0f0f0')
        performance_frame.pack(side='right', fill='x', expand=True)
        tk.Label(performance_frame, text="📈 Performance", font=('Arial', 8), bg='#f0f0f0').pack()
        self.performance_value = tk.Label(performance_frame, text="0.0%", font=('Arial', 10, 'bold'), 
                                         fg='#0066ff', bg='#f0f0f0')
        self.performance_value.pack()
    
    def create_options_tab(self):
        """Création de l'onglet Options avec contrôles avancés"""
        
        # Container principal
        options_container = ctk.CTkScrollableFrame(self.options_tab)
        options_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # === SECTION CFR ===
        cfr_frame = ctk.CTkFrame(options_container)
        cfr_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(cfr_frame, text="🧠 Paramètres CFR", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Itérations CFR
        iter_frame = ctk.CTkFrame(cfr_frame)
        iter_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(iter_frame, text="Itérations CFR:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.cfr_iterations = ctk.CTkSlider(iter_frame, from_=1000, to=100000, command=self.update_cfr_iterations)
        self.cfr_iterations.pack(side='left', padx=10, fill='x', expand=True)
        self.cfr_iterations.set(10000)
        
        self.cfr_iter_label = ctk.CTkLabel(iter_frame, text="10000", font=ctk.CTkFont(weight="bold"))
        self.cfr_iter_label.pack(side='left', padx=10)
        
        # Description
        ctk.CTkLabel(iter_frame, text="Plus d'itérations = meilleure précision mais plus lent", 
                    font=ctk.CTkFont(size=10), text_color="gray").pack(side='right', padx=10)
        
        # Sampling CFR
        sampling_frame = ctk.CTkFrame(cfr_frame)
        sampling_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        self.cfr_sampling = ctk.CTkCheckBox(sampling_frame, text="Sampling CFR (plus rapide)", 
                                           command=self.toggle_cfr_sampling)
        self.cfr_sampling.pack(side='left', padx=20, pady=15)
        self.cfr_sampling.select()  # Activé par défaut
        
        # === SECTION OCR ===
        ocr_frame = ctk.CTkFrame(options_container)
        ocr_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(ocr_frame, text="👁️ Paramètres OCR", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Intervalle OCR
        ocr_interval_frame = ctk.CTkFrame(ocr_frame)
        ocr_interval_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(ocr_interval_frame, text="Intervalle capture:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.ocr_interval = ctk.CTkSlider(ocr_interval_frame, from_=50, to=500, command=self.update_ocr_interval)
        self.ocr_interval.pack(side='left', padx=10, fill='x', expand=True)
        self.ocr_interval.set(100)
        
        self.ocr_interval_label = ctk.CTkLabel(ocr_interval_frame, text="100ms", font=ctk.CTkFont(weight="bold"))
        self.ocr_interval_label.pack(side='left', padx=10)
        
        # Confiance OCR
        confidence_frame = ctk.CTkFrame(ocr_frame)
        confidence_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        ctk.CTkLabel(confidence_frame, text="Confiance minimale:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.ocr_confidence = ctk.CTkSlider(confidence_frame, from_=0.1, to=1.0, command=self.update_ocr_confidence)
        self.ocr_confidence.pack(side='left', padx=10, fill='x', expand=True)
        self.ocr_confidence.set(0.8)
        
        self.ocr_confidence_label = ctk.CTkLabel(confidence_frame, text="80%", font=ctk.CTkFont(weight="bold"))
        self.ocr_confidence_label.pack(side='left', padx=10)
        
        # === SECTION INTERFACE ===
        ui_frame = ctk.CTkFrame(options_container)
        ui_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(ui_frame, text="🖥️ Interface utilisateur", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Langue
        lang_frame = ctk.CTkFrame(ui_frame)
        lang_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(lang_frame, text="Langue:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.language_combo = ctk.CTkComboBox(lang_frame, values=["Français", "English"], 
                                             command=self.change_language)
        self.language_combo.pack(side='left', padx=10)
        self.language_combo.set("Français")
        
        # Checkboxes d'affichage
        checkboxes_frame = ctk.CTkFrame(ui_frame)
        checkboxes_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        self.show_probabilities = ctk.CTkCheckBox(checkboxes_frame, text="Afficher probabilités")
        self.show_probabilities.pack(side='left', padx=20, pady=10)
        self.show_probabilities.select()
        
        self.show_recommendations = ctk.CTkCheckBox(checkboxes_frame, text="Afficher recommandations")
        self.show_recommendations.pack(side='left', padx=20, pady=10)
        self.show_recommendations.select()
        
        self.show_statistics = ctk.CTkCheckBox(checkboxes_frame, text="Afficher statistiques")
        self.show_statistics.pack(side='left', padx=20, pady=10)
        self.show_statistics.select()
        
        # === SECTION JEU ===
        game_frame = ctk.CTkFrame(options_container)
        game_frame.pack(fill='x')
        
        ctk.CTkLabel(game_frame, text="🎰 Paramètres de jeu", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Type de table par défaut
        table_type_frame = ctk.CTkFrame(game_frame)
        table_type_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(table_type_frame, text="Type de table:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.table_type_combo = ctk.CTkComboBox(table_type_frame, values=["Cash Game", "Tournament"], 
                                               command=self.change_table_type)
        self.table_type_combo.pack(side='left', padx=10)
        self.table_type_combo.set("Cash Game")
        
        # Objectif de mains
        target_frame = ctk.CTkFrame(game_frame)
        target_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        ctk.CTkLabel(target_frame, text="Objectif mains/100:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.target_hands = ctk.CTkSlider(target_frame, from_=50, to=80, command=self.update_target_hands)
        self.target_hands.pack(side='left', padx=10, fill='x', expand=True)
        self.target_hands.set(65)
        
        self.target_hands_label = ctk.CTkLabel(target_frame, text="65", font=ctk.CTkFont(weight="bold"))
        self.target_hands_label.pack(side='left', padx=10)

    def create_settings_tab(self):
        """Création de l'onglet Paramètres avec gestion des ressources"""
        
        # Container principal avec scroll
        settings_container = ctk.CTkScrollableFrame(self.settings_tab)
        settings_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # === SECTION RESSOURCES ===
        resource_frame = ctk.CTkFrame(settings_container)
        resource_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(resource_frame, text="⚡ Gestion des ressources", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 15))
        
        # Limite CPU
        cpu_frame = ctk.CTkFrame(resource_frame)
        cpu_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(cpu_frame, text="Limite CPU:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.cpu_limit = ctk.CTkSlider(cpu_frame, from_=10, to=100, command=self.update_cpu_value)
        self.cpu_limit.pack(side='left', padx=10, fill='x', expand=True)
        self.cpu_limit.set(80)
        
        # Affichage valeur
        self.cpu_value_label = ctk.CTkLabel(cpu_frame, text="80%", font=ctk.CTkFont(weight="bold"))
        self.cpu_value_label.pack(side='left', padx=10)
        
        # Description
        ctk.CTkLabel(cpu_frame, text="Limite d'usage CPU pour préserver les performances", 
                    font=ctk.CTkFont(size=10), text_color="gray").pack(side='right', padx=10)
        
        # Limite RAM
        ram_frame = ctk.CTkFrame(resource_frame)
        ram_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        ctk.CTkLabel(ram_frame, text="Limite RAM:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.ram_limit = ctk.CTkSlider(ram_frame, from_=1, to=16, command=self.update_ram_value)
        self.ram_limit.pack(side='left', padx=10, fill='x', expand=True)
        self.ram_limit.set(8)
        
        # Affichage valeur
        self.ram_value_label = ctk.CTkLabel(ram_frame, text="8.0 GB", font=ctk.CTkFont(weight="bold"))
        self.ram_value_label.pack(side='left', padx=10)
        
        # Description
        ctk.CTkLabel(ram_frame, text="Limite mémoire pour les calculs CFR et données", 
                    font=ctk.CTkFont(size=10), text_color="gray").pack(side='right', padx=10)
        
        # === SECTION GPU ===
        gpu_frame = ctk.CTkFrame(settings_container)
        gpu_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(gpu_frame, text="🎮 Paramètres GPU", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 15))
        
        # Activation GPU
        gpu_enable_frame = ctk.CTkFrame(gpu_frame)
        gpu_enable_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.gpu_enabled = ctk.CTkCheckBox(gpu_enable_frame, text="Activer l'accélération GPU", 
                                          command=self.toggle_gpu)
        self.gpu_enabled.pack(side='left', padx=20, pady=15)
        
        # Limite mémoire GPU
        gpu_mem_frame = ctk.CTkFrame(gpu_frame)
        gpu_mem_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        ctk.CTkLabel(gpu_mem_frame, text="Limite mémoire GPU:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.gpu_memory = ctk.CTkSlider(gpu_mem_frame, from_=20, to=95, command=self.update_gpu_memory)
        self.gpu_memory.pack(side='left', padx=10, fill='x', expand=True)
        self.gpu_memory.set(80)
        
        self.gpu_mem_label = ctk.CTkLabel(gpu_mem_frame, text="80%", font=ctk.CTkFont(weight="bold"))
        self.gpu_mem_label.pack(side='left', padx=10)
        
        # === SECTION AVANCÉ ===
        advanced_frame = ctk.CTkFrame(settings_container)
        advanced_frame.pack(fill='x')
        
        ctk.CTkLabel(advanced_frame, text="🔧 Paramètres avancés", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 15))
        
        # Gestion automatique des ressources
        auto_mgmt_frame = ctk.CTkFrame(advanced_frame)
        auto_mgmt_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.auto_resource_mgmt = ctk.CTkCheckBox(auto_mgmt_frame, text="Gestion automatique des ressources", 
                                                 command=self.toggle_auto_resource_mgmt)
        self.auto_resource_mgmt.pack(side='left', padx=20, pady=15)
        self.auto_resource_mgmt.select()  # Activé par défaut
        
        # Vitesse de génération
        gen_rate_frame = ctk.CTkFrame(advanced_frame)
        gen_rate_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        ctk.CTkLabel(gen_rate_frame, text="Vitesse génération:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.generation_rate = ctk.CTkSlider(gen_rate_frame, from_=1, to=10, command=self.update_generation_rate)
        self.generation_rate.pack(side='left', padx=10, fill='x', expand=True)
        self.generation_rate.set(7)
        
        self.gen_rate_label = ctk.CTkLabel(gen_rate_frame, text="7 (Rapide)", font=ctk.CTkFont(weight="bold"))
        self.gen_rate_label.pack(side='left', padx=10)

    def create_performance_tab(self):
        """Création de l'onglet Performance avec métriques système"""
        
        # Container principal
        perf_container = ctk.CTkFrame(self.performance_tab)
        perf_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(perf_container, text="⚡ Monitoring des performances", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 30))
        
        # === MÉTRIQUES SYSTÈME ===
        system_frame = ctk.CTkFrame(perf_container)
        system_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(system_frame, text="💻 Système", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Métriques en grille
        metrics_grid = ctk.CTkFrame(system_frame)
        metrics_grid.pack(fill='x', padx=20, pady=(0, 20))
        
        # CPU
        cpu_metric_frame = ctk.CTkFrame(metrics_grid)
        cpu_metric_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ctk.CTkLabel(cpu_metric_frame, text="CPU", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.cpu_usage_label = ctk.CTkLabel(cpu_metric_frame, text="0%", font=ctk.CTkFont(size=16, weight="bold"))
        self.cpu_usage_label.pack(pady=5)
        
        # RAM
        ram_metric_frame = ctk.CTkFrame(metrics_grid)
        ram_metric_frame.pack(side='left', fill='x', expand=True, padx=5)
        ctk.CTkLabel(ram_metric_frame, text="RAM", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.ram_usage_label = ctk.CTkLabel(ram_metric_frame, text="0 GB", font=ctk.CTkFont(size=16, weight="bold"))
        self.ram_usage_label.pack(pady=5)
        
        # GPU (si disponible)
        gpu_metric_frame = ctk.CTkFrame(metrics_grid)
        gpu_metric_frame.pack(side='right', fill='x', expand=True, padx=(10, 0))
        ctk.CTkLabel(gpu_metric_frame, text="GPU", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.gpu_usage_label = ctk.CTkLabel(gpu_metric_frame, text="N/A", font=ctk.CTkFont(size=16, weight="bold"))
        self.gpu_usage_label.pack(pady=5)
        
        # === MÉTRIQUES CFR ===
        cfr_metrics_frame = ctk.CTkFrame(perf_container)
        cfr_metrics_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(cfr_metrics_frame, text="🧠 CFR Engine", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Métriques CFR en grille
        cfr_grid = ctk.CTkFrame(cfr_metrics_frame)
        cfr_grid.pack(fill='x', padx=20, pady=(0, 20))
        
        # Itérations/sec
        iter_metric_frame = ctk.CTkFrame(cfr_grid)
        iter_metric_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ctk.CTkLabel(iter_metric_frame, text="Itérations/sec", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.iterations_sec_label = ctk.CTkLabel(iter_metric_frame, text="0", font=ctk.CTkFont(size=16, weight="bold"))
        self.iterations_sec_label.pack(pady=5)
        
        # Convergence
        conv_metric_frame = ctk.CTkFrame(cfr_grid)
        conv_metric_frame.pack(side='left', fill='x', expand=True, padx=5)
        ctk.CTkLabel(conv_metric_frame, text="Convergence", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.convergence_label = ctk.CTkLabel(conv_metric_frame, text="0%", font=ctk.CTkFont(size=16, weight="bold"))
        self.convergence_label.pack(pady=5)
        
        # Qualité
        quality_metric_frame = ctk.CTkFrame(cfr_grid)
        quality_metric_frame.pack(side='right', fill='x', expand=True, padx=(10, 0))
        ctk.CTkLabel(quality_metric_frame, text="Qualité", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.quality_label = ctk.CTkLabel(quality_metric_frame, text="0%", font=ctk.CTkFont(size=16, weight="bold"))
        self.quality_label.pack(pady=5)
        
        # === MÉTRIQUES OCR ===
        ocr_metrics_frame = ctk.CTkFrame(perf_container)
        ocr_metrics_frame.pack(fill='x')
        
        ctk.CTkLabel(ocr_metrics_frame, text="👁️ OCR Engine", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Métriques OCR
        ocr_grid = ctk.CTkFrame(ocr_metrics_frame)
        ocr_grid.pack(fill='x', padx=20, pady=(0, 20))
        
        # Capture/sec
        capture_metric_frame = ctk.CTkFrame(ocr_grid)
        capture_metric_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ctk.CTkLabel(capture_metric_frame, text="Captures/sec", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.captures_sec_label = ctk.CTkLabel(capture_metric_frame, text="0", font=ctk.CTkFont(size=16, weight="bold"))
        self.captures_sec_label.pack(pady=5)
        
        # Confiance
        ocr_conf_metric_frame = ctk.CTkFrame(ocr_grid)
        ocr_conf_metric_frame.pack(side='left', fill='x', expand=True, padx=5)
        ctk.CTkLabel(ocr_conf_metric_frame, text="Confiance moy.", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.ocr_confidence_label = ctk.CTkLabel(ocr_conf_metric_frame, text="0%", font=ctk.CTkFont(size=16, weight="bold"))
        self.ocr_confidence_label.pack(pady=5)
        
        # Temps traitement
        ocr_time_metric_frame = ctk.CTkFrame(ocr_grid)
        ocr_time_metric_frame.pack(side='right', fill='x', expand=True, padx=(10, 0))
        ctk.CTkLabel(ocr_time_metric_frame, text="Temps moy.", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.ocr_time_label = ctk.CTkLabel(ocr_time_metric_frame, text="0ms", font=ctk.CTkFont(size=16, weight="bold"))
        self.ocr_time_label.pack(pady=5)

    def create_version_tab(self):
        """Création de l'onglet Version et About"""
        
        # Container principal
        version_container = ctk.CTkFrame(self.version_tab)
        version_container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Logo/titre principal
        ctk.CTkLabel(version_container, text="🎯 RTPA Studio", 
                    font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(40, 10))
        
        ctk.CTkLabel(version_container, text="Real-Time Poker Assistant", 
                    font=ctk.CTkFont(size=18), text_color="gray").pack(pady=(0, 20))
        
        # Informations de version
        version_info_frame = ctk.CTkFrame(version_container)
        version_info_frame.pack(pady=(20, 30))
        
        ctk.CTkLabel(version_info_frame, text="Version 1.0.0", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        ctk.CTkLabel(version_info_frame, text="Build 1000 - Version stable", 
                    font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 15))
        
        # Fonctionnalités
        features_frame = ctk.CTkFrame(version_container)
        features_frame.pack(fill='x', pady=(20, 30))
        
        ctk.CTkLabel(features_frame, text="✨ Fonctionnalités", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 10))
        
        features = [
            "🧠 Intelligence Artificielle CFR/Nash",
            "👁️ OCR automatique en temps réel",
            "⚡ Accélération GPU avec CUDA",
            "📊 Analyse avancée de performance",
            "🎯 Recommandations stratégiques",
            "📈 Statistiques détaillées"
        ]
        
        for feature in features:
            ctk.CTkLabel(features_frame, text=feature, font=ctk.CTkFont(size=11)).pack(anchor='w', padx=20, pady=2)
        
        # Bouton mise à jour
        self.check_update_btn = ctk.CTkButton(version_container, 
                                             text="🔄 Vérifier les mises à jour",
                                             command=self.check_for_updates,
                                             width=200)
        self.check_update_btn.pack(pady=(30, 10))
        
        # Status de mise à jour
        self.update_status_label = ctk.CTkLabel(version_container, text="", 
                                               font=ctk.CTkFont(size=12))
        self.update_status_label.pack(pady=5)
        
        # Copyright
        ctk.CTkLabel(version_container, text="© 2025 RTPA Studio - Tous droits réservés", 
                    font=ctk.CTkFont(size=10), text_color="gray").pack(side='bottom', pady=(30, 20))
    
    def update_hero_info(self, pseudo, stack, position):
        """Met à jour les informations du joueur principal"""
        self.hero_name_label.config(text=pseudo)
        self.hero_stack_label.config(text=stack)
        self.hero_position_label.config(text=position)
    
    def update_players_from_ocr(self, players_data, hero_data=None):
        """Met à jour les informations des joueurs depuis l'OCR"""
        # Mettre à jour nos infos si fournies
        if hero_data:
            self.update_hero_info(hero_data.get('name', 'MonPseudo'), 
                                self.format_amount(float(hero_data.get('stack', '0').replace('€', '').replace(',', '.'))), 
                                hero_data.get('position', 'Unknown'))
        
        # Compter uniquement les joueurs réellement détectés par OCR
        real_active_count = 0
        if players_data:
            real_active_count = sum(1 for p in players_data if p.get('status') == 'actif')
        if hero_data and hero_data.get('detected_by_ocr', False) and hero_data.get('status') == 'actif':
            real_active_count += 1
        
        self.active_players_count.config(text=f"{real_active_count}/9")
        
        # Afficher les joueurs uniquement avec les vraies données OCR
        # Ne pas créer de données factices - attendre les vraies données OCR
        real_players = []
        
        # Ajouter les joueurs détectés par OCR (s'il y en a)
        if players_data and len(players_data) > 0:
            real_players.extend(players_data)
        
        # Ajouter le héros seulement s'il y a des vraies données OCR
        if hero_data and hero_data.get('detected_by_ocr', False):
            hero_player = {
                'name': hero_data.get('name'),
                'stack': hero_data.get('stack_numeric'),
                'position': hero_data.get('position_index'),
                'position_name': hero_data.get('position'),
                'status': hero_data.get('status'),
                'vpip': hero_data.get('vpip'),
                'pfr': hero_data.get('pfr'),
                'is_button': hero_data.get('position_index') == 6,
                'is_sb': hero_data.get('position_index') == 7,
                'is_bb': hero_data.get('position_index') == 8,
                'is_hero': True
            }
            real_players.append(hero_player)
        
        self.create_players_display(real_players)
    
    def create_players_display(self, players_data=None):
        """Affichage des 9 positions fixes d'une table 9-max"""
        
        # Effacer l'affichage existant
        for widget in self.players_list_frame.winfo_children():
            widget.destroy()
        
        # Définir les 9 positions fixes d'une table 9-max
        positions = [
            {'name': 'UTG', 'index': 0},
            {'name': 'UTG+1', 'index': 1}, 
            {'name': 'MP1', 'index': 2},
            {'name': 'MP2', 'index': 3},
            {'name': 'MP3', 'index': 4},
            {'name': 'CO', 'index': 5},
            {'name': 'BTN', 'index': 6},
            {'name': 'SB', 'index': 7},
            {'name': 'BB', 'index': 8}
        ]
        
        # Créer un dictionnaire des joueurs par position
        players_by_position = {}
        if players_data:
            for player in players_data:
                pos_index = player.get('position', 0)
                players_by_position[pos_index] = player
        
        # Afficher chaque position (siège vide ou occupé)
        for pos in positions:
            player_frame = ttk.Frame(self.players_list_frame)
            player_frame.pack(fill='x', pady=1, padx=2)
            
            main_line = ttk.Frame(player_frame)
            main_line.pack(fill='x')
            
            # Position avec couleur et icône selon le type
            pos_text = pos['name']
            position_icon = ""
            text_color = '#ffffff'  # Couleur par défaut (blanc)
            
            if pos['index'] == 6:  # BTN (Button)
                position_icon = " 🟢"
                text_color = '#FFD700'  # Or
            elif pos['index'] == 7:  # SB (Small Blind) 
                position_icon = " 🟡"
                text_color = '#FF6B35'  # Orange-rouge
            elif pos['index'] == 8:  # BB (Big Blind)
                position_icon = " 🔵"
                text_color = '#FF1744'  # Rouge
            else:
                text_color = '#87CEEB'  # Bleu clair pour les autres positions
            
            # Appliquer la couleur avec tkinter au lieu de ttk pour supporter les couleurs
            pos_label = tk.Label(main_line, text=f"{pos_text}{position_icon}", 
                               font=('Arial', 8, 'bold'),
                               fg=text_color,
                               bg='#2b2b2b')
            pos_label.pack(side='left')
            
            # Vérifier si la position est occupée
            player = players_by_position.get(pos['index'])
            
            if player:
                # Position occupée - afficher uniquement les vraies infos OCR
                status_color = '#28a745' if player.get('status') == 'actif' else '#6c757d'
                status_icon = "●" if player.get('status') == 'actif' else "○"
                
                # Statut (seulement si détecté par OCR)
                ttk.Label(main_line, text=status_icon, font=('Arial', 8), 
                         foreground=status_color).pack(side='left', padx=(2, 3))
                
                # Nom (seulement si détecté par OCR) - en bleu et gras si c'est le héros
                if player.get('name'):
                    name = player.get('name')[:8]
                    if len(player.get('name', '')) > 8:
                        name += "."
                        
                    is_hero = player.get('is_hero', False)
                    font_weight = 'bold' if is_hero else 'normal'
                    name_color = '#007bff' if is_hero else status_color
                    ttk.Label(main_line, text=name, font=('Arial', 8, font_weight), 
                             foreground=name_color).pack(side='left')
                    
                    # Stats (seulement si disponibles et réelles)
                    vpip = player.get('vpip')
                    pfr = player.get('pfr')
                    if vpip is not None and pfr is not None:
                        stats_text = f"{vpip}/{pfr}"
                        ttk.Label(main_line, text=stats_text, font=('Arial', 7), 
                                 foreground='#6c757d').pack(side='left', padx=(5, 0))
                    
                    # Stack (seulement si détecté par OCR)
                    stack_value = player.get('stack')
                    if stack_value is not None and stack_value > 0:
                        if isinstance(stack_value, (int, float)):
                            if stack_value >= 1000:
                                stack_text = f"{stack_value/1000:.1f}k"
                            else:
                                stack_text = f"{stack_value:.0f}"
                        else:
                            stack_text = str(stack_value)
                        
                        ttk.Label(main_line, text=stack_text, font=('Arial', 7), 
                                 foreground=status_color).pack(side='right', padx=(5, 0))
            else:
                # Position vide - afficher seulement "Siège vide" (pas de données factices)
                ttk.Label(main_line, text="Siège vide", font=('Arial', 8, 'italic'), 
                         foreground='#999999').pack(side='left', padx=(5, 0))
    
    def setup_styles(self):
        """Configuration des styles pour l'interface"""
        style = ttk.Style()
        
        # Style pour les cadres de cartes
        style.configure('Card.TFrame', relief='ridge', borderwidth=2, background='#f0f0f0')
    
    def format_amount(self, amount):
        """Formate un montant en euros avec 2 décimales"""
        try:
            return f"{float(amount):.2f}€"
        except (ValueError, TypeError):
            return "0.00€"
    
    # Méthodes pour les menus (à implémenter selon besoins)
    def setup_menu_bar(self):
        """Configuration de la barre de menu"""
        pass  # Implémentation future si nécessaire
    
    def on_closing(self):
        """Gestion propre de la fermeture"""
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
        self.root.destroy()
    
    def run(self):
        """Lance l'interface graphique"""
        self.running = True
        self.start_gui_update_thread()
        self.root.mainloop()
    
    def start_gui_update_thread(self):
        """Démarre le thread de mise à jour de l'interface"""
        if self.update_thread and self.update_thread.is_alive():
            return
        
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def _update_loop(self):
        """Boucle de mise à jour de l'interface avec stabilisation"""
        last_data = None
        update_pending = False
        
        while self.running:
            try:
                if self.app_manager and not update_pending:
                    # Récupérer les données du gestionnaire (si la méthode existe)
                    if hasattr(self.app_manager, 'get_display_data'):
                        data = self.app_manager.get_display_data()
                    else:
                        # Données vides quand aucune partie n'est détectée
                        data = {
                            'hero_cards': [],
                            'board_cards': [],
                            'pot': '0.00€',
                            'stack': '0.00€',
                            'action': '',
                            'bet_size': '',
                            'win_probability': '',
                            'risk_level': '',
                            'confidence': '',
                            'reasoning': 'En attente d\'analyse...',
                            'players_info': []  # Aucun joueur affiché quand pas de partie active
                        }
                    
                    # Ne mettre à jour que si les données ont changé
                    if data != last_data:
                        update_pending = True
                        last_data = data.copy() if isinstance(data, dict) else data
                        
                        # Mettre à jour dans le thread principal avec callback de fin
                        def update_complete():
                            nonlocal update_pending
                            update_pending = False
                        
                        self.root.after(0, lambda: self._perform_stable_update(data, update_complete))
                
                time.sleep(1.5)  # Mise à jour moins fréquente pour stabilité
                
            except Exception as e:
                print(f"Erreur dans la boucle de mise à jour: {e}")
                update_pending = False
                time.sleep(1)
    
    def _perform_stable_update(self, data, callback):
        """Effectue une mise à jour stable et complète des données"""
        try:
            # Mise à jour complète en une seule fois
            self.update_display(data)
            
            # Mettre à jour les joueurs si disponibles
            if data.get('players_info'):
                self.update_players_from_ocr(data['players_info'])
            
            # Forcer la mise à jour graphique
            self.root.update_idletasks()
            
        except Exception as e:
            print(f"Erreur mise à jour stable: {e}")
        finally:
            # Signaler que la mise à jour est terminée
            if callback:
                callback()
    
    # ========================================
    # FONCTIONS CALLBACK POUR LES PARAMÈTRES
    # ========================================
    
    def update_cpu_value(self, value):
        """Met à jour l'affichage de la valeur CPU et applique la limite"""
        try:
            cpu_value = int(float(value))
            self.cpu_value_label.configure(text=f"{cpu_value}%")
            
            # Sauvegarder le paramètre de manière persistante
            if hasattr(self, 'app_manager') and self.app_manager:
                # Sauvegarder dans settings.yaml
                self.app_manager.update_settings({'cpu_usage_limit': float(cpu_value)})
                
                if hasattr(self.app_manager, 'cfr_trainer') and self.app_manager.cfr_trainer:
                    # Appliquer la limite CPU réelle
                    self.app_manager.cfr_trainer.configure_generation_resources(
                        cpu_percent=cpu_value
                    )
                    print(f"✅ Limite CPU CFR appliquée et sauvegardée: {cpu_value}%")
        except Exception as e:
            print(f"Erreur mise à jour CPU: {e}")
    
    def update_ram_value(self, value):
        """Met à jour l'affichage de la valeur RAM et applique la limite"""
        try:
            ram_value = float(value)
            self.ram_value_label.configure(text=f"{ram_value:.1f} GB")
            
            # Sauvegarder le paramètre de manière persistante
            if hasattr(self, 'app_manager') and self.app_manager:
                # Convertir GB en pourcentage approximatif (pour 16GB total)
                ram_percentage = (ram_value / 16.0) * 100
                # Sauvegarder dans settings.yaml
                self.app_manager.update_settings({'ram_usage_limit': ram_percentage})
                
                if hasattr(self.app_manager, 'cfr_trainer') and self.app_manager.cfr_trainer:
                    # Appliquer la limite RAM réelle (convertir GB en MB)
                    ram_mb = ram_value * 1024
                    self.app_manager.cfr_trainer.configure_generation_resources(
                        memory_mb=ram_mb
                    )
                    print(f"✅ Limite RAM CFR appliquée et sauvegardée: {ram_value:.1f} GB")
        except Exception as e:
            print(f"Erreur mise à jour RAM: {e}")
    
    def update_generation_rate(self, value):
        """Met à jour l'affichage de la vitesse de génération et applique le changement"""
        try:
            rate_value = int(float(value))
            rate_labels = {
                1: "1 (Très lent)", 2: "2 (Lent)", 3: "3 (Lent)", 
                4: "4 (Modéré)", 5: "5 (Moyen)", 6: "6 (Moyen)",
                7: "7 (Rapide)", 8: "8 (Rapide)", 9: "9 (Très rapide)", 10: "10 (Maximum)"
            }
            display_text = rate_labels.get(rate_value, f"{rate_value}")
            self.gen_rate_label.configure(text=display_text)
            
            # Appliquer la vitesse de génération réelle
            if hasattr(self, 'app_manager') and self.app_manager:
                if hasattr(self.app_manager, 'cfr_trainer') and self.app_manager.cfr_trainer:
                    # Convertir la valeur 1-10 en mains par seconde (1=1 main/s, 10=10 mains/s)
                    hands_per_sec = rate_value
                    self.app_manager.cfr_trainer.configure_generation_resources(
                        generation_rate=hands_per_sec
                    )
                    print(f"✅ Vitesse génération appliquée: {rate_value} ({display_text})")
        except Exception as e:
            print(f"Erreur mise à jour vitesse: {e}")
    
    def load_saved_settings(self):
        """Charge les paramètres sauvegardés et met à jour l'interface"""
        try:
            if hasattr(self, 'app_manager') and self.app_manager and hasattr(self.app_manager, 'settings'):
                settings = self.app_manager.settings
                
                # Charger CPU (pourcentage direct)
                if hasattr(self, 'cpu_limit') and self.cpu_limit:
                    cpu_value = getattr(settings, 'cpu_usage_limit', 80.0)
                    self.cpu_limit.set(cpu_value)
                    if hasattr(self, 'cpu_value_label'):
                        self.cpu_value_label.configure(text=f"{int(cpu_value)}%")
                
                # Charger RAM (convertir pourcentage en GB approximatif)
                if hasattr(self, 'ram_limit') and self.ram_limit:
                    ram_percentage = getattr(settings, 'ram_usage_limit', 70.0)
                    # Convertir pourcentage en GB (assumant 16GB total)
                    ram_gb = (ram_percentage / 100.0) * 16.0
                    self.ram_limit.set(ram_gb)
                    if hasattr(self, 'ram_value_label'):
                        self.ram_value_label.configure(text=f"{ram_gb:.1f} GB")
                
                # Charger GPU
                if hasattr(self, 'gpu_enabled') and self.gpu_enabled:
                    gpu_enabled = getattr(settings, 'gpu_enabled', True)
                    if gpu_enabled:
                        self.gpu_enabled.select()
                    else:
                        self.gpu_enabled.deselect()
                
                # Charger mémoire GPU
                if hasattr(self, 'gpu_memory') and self.gpu_memory:
                    gpu_memory = getattr(settings, 'gpu_memory_limit', 80.0)
                    self.gpu_memory.set(gpu_memory)
                    if hasattr(self, 'gpu_mem_label'):
                        self.gpu_mem_label.configure(text=f"{int(gpu_memory)}%")
                
                print("✅ Paramètres chargés depuis settings.yaml")
                
        except Exception as e:
            print(f"Erreur chargement paramètres: {e}")
    
    # Autres méthodes callback (à implémenter selon besoins)
    def update_cfr_iterations(self, value):
        """Met à jour le nombre d'itérations CFR"""
        iterations = int(float(value))
        self.cfr_iter_label.configure(text=str(iterations))
        if hasattr(self, 'app_manager') and self.app_manager:
            self.app_manager.update_settings({'cfr_iterations': iterations})
    
    def toggle_cfr_sampling(self):
        """Active/désactive le sampling CFR"""
        sampling_enabled = self.cfr_sampling.get()
        if hasattr(self, 'app_manager') and self.app_manager:
            self.app_manager.update_settings({'cfr_sampling_enabled': sampling_enabled})
    
    def update_ocr_interval(self, value):
        """Met à jour l'intervalle OCR"""
        interval = int(float(value))
        self.ocr_interval_label.configure(text=f"{interval}ms")
        if hasattr(self, 'app_manager') and self.app_manager:
            self.app_manager.update_settings({'ocr_interval_ms': interval})
    
    def update_ocr_confidence(self, value):
        """Met à jour la confiance OCR"""
        confidence = float(value)
        self.ocr_confidence_label.configure(text=f"{int(confidence*100)}%")
        if hasattr(self, 'app_manager') and self.app_manager:
            self.app_manager.update_settings({'ocr_confidence_threshold': confidence})
    
    def change_language(self, selection):
        """Change la langue"""
        lang = "fr" if selection == "Français" else "en"
        if hasattr(self, 'app_manager') and self.app_manager:
            self.app_manager.update_settings({'language': lang})
    
    def change_table_type(self, selection):
        """Change le type de table"""
        table_type = "cashgame" if selection == "Cash Game" else "tournament"
        if hasattr(self, 'app_manager') and self.app_manager:
            self.app_manager.update_settings({'default_table_type': table_type})
    
    def update_target_hands(self, value):
        """Met à jour l'objectif de mains"""
        target = int(float(value))
        self.target_hands_label.configure(text=str(target))
        if hasattr(self, 'app_manager') and self.app_manager:
            self.app_manager.update_settings({'target_hands_per_100': target})
    
    def toggle_gpu(self):
        """Active/désactive le GPU"""
        gpu_enabled = self.gpu_enabled.get()
        if hasattr(self, 'app_manager') and self.app_manager:
            self.app_manager.update_settings({'gpu_enabled': gpu_enabled})
    
    def update_gpu_memory(self, value):
        """Met à jour la limite mémoire GPU"""
        gpu_mem = int(float(value))
        self.gpu_mem_label.configure(text=f"{gpu_mem}%")
        if hasattr(self, 'app_manager') and self.app_manager:
            self.app_manager.update_settings({'gpu_memory_limit': float(gpu_mem)})
    
    def toggle_auto_resource_mgmt(self):
        """Active/désactive la gestion automatique des ressources"""
        auto_mgmt = self.auto_resource_mgmt.get()
        if hasattr(self, 'app_manager') and self.app_manager:
            self.app_manager.update_settings({'auto_resource_management': auto_mgmt})
    
    def check_for_updates(self):
        """Vérifie les mises à jour"""
        self.update_status_label.configure(text="Vérification en cours...", text_color="orange")
        self.check_update_btn.configure(state="disabled")
        
        # Thread de vérification
        import threading
        thread = threading.Thread(target=self._check_github_updates, daemon=True)
        thread.start()
    
    def _check_github_updates(self):
        """Thread pour vérifier GitHub - temporairement désactivé"""
        try:
            # Fonctionnalité de mise à jour désactivée temporairement
            # Le dépôt GitHub n'est pas encore configuré pour ce projet
            self.root.after(0, lambda: self.update_status_label.configure(
                text="Vérification des mises à jour non disponible", text_color="orange"
            ))
            self.root.after(0, lambda: self.check_update_btn.configure(state="normal"))
            
        except Exception as e:
            print(f"Erreur système: {e}")
            self.root.after(0, lambda: self.update_status_label.configure(
                text="Erreur système", text_color="red"
            ))
            self.root.after(0, lambda: self.check_update_btn.configure(state="normal"))

    def _get_current_version(self):
        """Récupère la version actuelle depuis version.json"""
        try:
            import os
            import json
            version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'version.json')
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    version_info = json.load(f)
                    return version_info.get('version', '1.0.0')
        except:
            pass
        return "1.0.0"
    
    def update_display(self, data):
        """Met à jour l'affichage avec les données reçues"""
        try:
            # Mise à jour des cartes héros
            if data.get('hero_cards') and len(data['hero_cards']) >= 2:
                self.hero_card1.configure(text=self.card_to_symbol(data['hero_cards'][0]))
                self.hero_card2.configure(text=self.card_to_symbol(data['hero_cards'][1]))
            else:
                self.hero_card1.configure(text="🂠")
                self.hero_card2.configure(text="🂠")
            
            # Mise à jour du board
            if data.get('board_cards'):
                for i, card in enumerate(data['board_cards'][:5]):
                    if i < len(self.board_cards):
                        if card:
                            self.board_cards[i].configure(text=self.card_to_symbol(card))
                        else:
                            self.board_cards[i].configure(text="🂠")
                            
            # Mise à jour des informations de jeu
            if data.get('pot'):
                self.pot_value.configure(text=str(data['pot']))
                
            if data.get('action'):
                self.action_label.configure(text=str(data['action']))
                
            if data.get('win_probability'):
                self.win_prob_label.configure(text=str(data['win_probability']))
                
            if data.get('risk_level'):
                self.risk_label.configure(text=str(data['risk_level']))
                
            if data.get('confidence'):
                self.confidence_label.configure(text=str(data['confidence']))
                
            if data.get('reasoning'):
                self.reasoning_label.configure(text=str(data['reasoning']))
                
        except Exception as e:
            print(f"Erreur mise à jour affichage: {e}")
    
    def card_to_symbol(self, card_str):
        """Convertit une carte string (ex: 'As', 'Kh') en symbole Unicode"""
        if not card_str or len(card_str) != 2:
            return "🂠"
        
        rank, suit = card_str[0], card_str[1]
        
        # Mapping des couleurs
        suit_map = {
            's': '♠️',  # Spades
            'h': '♥️',  # Hearts  
            'd': '♦️',  # Diamonds
            'c': '♣️'   # Clubs
        }
        
        # Mapping des rangs
        rank_map = {
            'A': 'A', 'K': 'K', 'Q': 'Q', 'J': 'J',
            'T': '10', '9': '9', '8': '8', '7': '7',
            '6': '6', '5': '5', '4': '4', '3': '3', '2': '2'
        }
        
        suit_symbol = suit_map.get(suit.lower(), '?')
        rank_symbol = rank_map.get(rank.upper(), '?')
        
        return f"{rank_symbol}{suit_symbol}"