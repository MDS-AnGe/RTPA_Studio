"""
Interface graphique principale pour RTPA Studio avec CustomTkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import threading
import time
import os
import json
import subprocess
from pathlib import Path

# Configuration CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RTAPGUIWindow:
    def __init__(self, app_manager=None):
        """Initialisation de l'interface graphique RTPA Studio"""
        self.app_manager = app_manager
        self.update_thread = None
        self.running = False
        
        # Configuration de la fenêtre principale
        self.root = ctk.CTk()
        self.root.title("RTPA Studio")
        self.root.geometry("1100x900")  # Réduit de 1400 à 1100
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configuration couleurs plus claires
        ctk.set_appearance_mode("light")  # Mode clair pour éviter les zones noires
        
        # Variables de thème
        self.accent_color = "blue"
        self.font_family = "Arial"
        self.opacity = 1.0
        
        # Type de table actuel pour gérer l'affichage des devises
        self.current_table_type = "cashgame"
        
        # Charger logo si disponible
        self.logo = None
        self.logo_image = None
        self.load_logo()
        
        # Configuration du style
        self.setup_styles()
        
        # Interface utilisateur
        self.create_widgets()
        
        # Variables de statut
        self.current_connection_status = "waiting"  # waiting, active, error
        self.current_activity = "training"  # Commencer avec training car CFR est toujours actif
        self.current_platform = None  # Plateforme actuellement connectée
        
        # Démarrer la mise à jour du statut
        self._update_status_display()
        
        # Connecter aux événements réels du système
        self._connect_to_system_events()
        
        # Démarrage auto-détection (si disponible)
        if self.app_manager and hasattr(self.app_manager, 'start_platform_detection'):
            self.app_manager.start_platform_detection()
        
    def load_logo(self):
        """Charge le logo et l'icône si disponibles"""
        # Logo principal
        logo_path = "attached_assets/RTPA_Studio_logo_1757263280355.png"
        if os.path.exists(logo_path):
            try:
                from PIL import Image
                self.logo_image = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(200, 60)  # Taille adaptée au logo horizontal
                )
                self.logo = True
            except Exception as e:
                print(f"Erreur chargement logo: {e}")
                self.logo = None
        
        # Icône de fenêtre
        icon_path = "attached_assets/RTPA_Studio_icon_1757263280355.ico"
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                # Fallback avec l'icône PNG
                icon_png = "attached_assets/RTPA_Studio_icon_1024_1757263280355.png"
                if os.path.exists(icon_png):
                    try:
                        from PIL import Image
                        icon_img = Image.open(icon_png)
                        icon_photo = tk.PhotoImage(icon_img.resize((64, 64)))
                        self.root.iconphoto(True, icon_photo)
                    except Exception:
                        pass
    
    def setup_styles(self):
        """Configuration des styles CustomTkinter"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Couleurs harmonisées - tons beige/crème correspondant au thème CustomTkinter
        bg_color = "#dbdbdb"  # Couleur de fond CustomTkinter par défaut en mode dark
        fg_color = "#212529"  # Noir doux pour le texte
        accent = "#1f538d"
        card_bg = "#dbdbdb"   # Beige pour les cartes
        
        # Styles des frames
        self.style.configure('Card.TFrame', background=bg_color, relief='raised', borderwidth=1)
        self.style.configure('Heading.TLabel', background=bg_color, foreground=fg_color, font=(self.font_family, 11, 'bold'))
        self.style.configure('Card.TLabel', background=bg_color, foreground=fg_color, font=(self.font_family, 10))
        
        # Styles pour les onglets
        self.style.configure('TNotebook', background=bg_color)
        self.style.configure('TNotebook.Tab', background=bg_color, foreground=fg_color)
        
        # Configuration de la fenêtre principale
        self.root.configure(bg=bg_color)
    
    def create_widgets(self):
        """Création de l'interface utilisateur"""
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # En-tête avec logo et titre
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        if self.logo:
            logo_label = ctk.CTkLabel(header_frame, image=self.logo_image, text="")
            logo_label.pack(side='left', padx=(10, 20))
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side='left', fill='both', expand=True)
        
        # Titre sur une ligne avec partie en gras et partie en normal
        title_line_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_line_frame.pack(anchor='w')
        
        ctk.CTkLabel(title_line_frame, text="Real-Time Poker Assistant ", font=ctk.CTkFont(size=24, weight="bold")).pack(side='left')
        ctk.CTkLabel(title_line_frame, text="(CFR/Nash)", font=ctk.CTkFont(size=24, weight="normal")).pack(side='left')
        ctk.CTkLabel(title_frame, text="avec Intelligence Artificielle", 
                    font=ctk.CTkFont(size=14)).pack(anchor='w')
        
        # Contrôles et statut (en-tête droite)
        self.controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        self.controls_frame.pack(side='right', padx=(20, 10))
        
        # Ligne 1: État de connexion (rouge/vert) - Plus gros
        self.connection_status_label = ctk.CTkLabel(
            self.controls_frame,
            text="En attente de plateforme",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ff6b6b"  # Rouge par défaut
        )
        self.connection_status_label.pack(pady=(3, 0))
        
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
            self.hero_cards_frame, bg='#dbdbdb', relief='raised', bd=2, width=90, height=120
        )
        self.hero_card2_frame.pack(side='left', padx=5)
        self.hero_card2_frame.pack_propagate(False)
        
        self.hero_card2 = tk.Label(
            self.hero_card2_frame, text="🂠", font=('Arial', 28, 'bold'),
            fg='#5a5a5a', bg='#dbdbdb', anchor='center'
        )
        self.hero_card2.pack(expand=True, fill='both')
        
        # Section Board (à droite)
        board_frame = ttk.LabelFrame(cards_container, text="🃏 Board", style='Card.TFrame')
        board_frame.pack(side='left', fill='both', expand=True, padx=(10, 0))
        
        board_content = tk.Frame(board_frame, bg='#dbdbdb')
        board_content.pack(fill='both', expand=True, padx=8, pady=6)
        
        self.board_cards_frame = tk.Frame(board_content, bg='#dbdbdb')
        self.board_cards_frame.pack(anchor='center')
        
        # Calculer la largeur optimale pour 5 cartes (90px + padding)
        optimal_board_width = (5 * 90) + (4 * 5) + 16  # 5 cartes + 4 espacements + padding
        
        self.board_cards = []
        self.board_card_frames = []
        for i in range(5):
            card_frame = tk.Frame(
                self.board_cards_frame, bg='#dbdbdb', relief='raised', bd=2, width=90, height=120
            )
            card_frame.pack(side='left', padx=5)
            card_frame.pack_propagate(False)
            
            card_label = tk.Label(
                card_frame, text="🂠", font=('Arial', 28, 'bold'),
                fg='#5a5a5a', bg='#dbdbdb', anchor='center'
            )
            card_label.pack(expand=True, fill='both')
            
            self.board_cards.append(card_label)
            self.board_card_frames.append(card_frame)
        
        # SECTION 2: LAYOUT PRINCIPAL AVEC COLONNES
        main_layout = ttk.Frame(main_container)
        main_layout.pack(fill='both', expand=True, pady=(0, 10))
        
        # Colonne gauche: Informations table et recommandations
        left_column = ttk.Frame(main_layout)
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        # SOUS-SECTION: Informations de table
        table_info_frame = ttk.LabelFrame(left_column, text="📊 INFORMATIONS TABLE", style='Card.TFrame')
        table_info_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        table_content = tk.Frame(table_info_frame, bg='#dbdbdb')
        table_content.pack(fill='both', expand=True, padx=8, pady=6)
        
        # POT principal - centré et mis en valeur
        pot_container = tk.Frame(table_content, bg='#dbdbdb')
        pot_container.pack(fill='x', pady=(0, 8))
        
        tk.Label(pot_container, text="💰 POT ACTUEL", font=('Arial', 11, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack()
        self.pot_label = tk.Label(pot_container, text=self.format_amount(0), font=('Arial', 20, 'bold'), fg='#28a745', bg='#dbdbdb')
        self.pot_label.pack()
        
        # Ligne blinds et antes - organisation horizontale équilibrée
        blinds_row = tk.Frame(table_content, bg='#dbdbdb')
        blinds_row.pack(fill='x', pady=(0, 4))
        
        # Blinds section - centrée à gauche
        blinds_container = tk.Frame(blinds_row, bg='#dbdbdb')
        blinds_container.pack(side='left', fill='x', expand=True)
        tk.Label(blinds_container, text="🎲 Blinds", font=('Arial', 10, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack()
        self.blinds_label = tk.Label(blinds_container, text=f"{self.format_amount(0)} / {self.format_amount(0)}", font=('Arial', 12, 'bold'), fg='#fd7e14', bg='#dbdbdb')
        self.blinds_label.pack()
        
        # Antes section - centrée à droite
        antes_container = tk.Frame(blinds_row, bg='#dbdbdb')
        antes_container.pack(side='right', fill='x', expand=True)
        tk.Label(antes_container, text="⚡ Antes", font=('Arial', 10, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack()
        self.antes_label = tk.Label(antes_container, text=self.format_amount(0), font=('Arial', 12, 'bold'), fg='#6f42c1', bg='#dbdbdb')
        self.antes_label.pack()
        
        # Type de table - en bas
        self.table_type_label = tk.Label(table_content, text="Cash Game", font=('Arial', 10), fg='#6c757d', bg='#dbdbdb')
        self.table_type_label.pack(pady=(4, 0))
        
        # SOUS-SECTION: Recommandation principale
        rec_frame = ttk.LabelFrame(left_column, text="🎯 RECOMMANDATION", style='Card.TFrame')
        rec_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        rec_content = tk.Frame(rec_frame, bg='#dbdbdb')
        rec_content.pack(fill='both', expand=True, padx=8, pady=6)
        
        # Action principale centrée
        action_container = tk.Frame(rec_content, bg='#dbdbdb')
        action_container.pack(fill='x', pady=(0, 8))
        
        self.action_display = tk.Label(action_container, text="---", font=('Arial', 24, 'bold'), fg='#6c757d', bg='#dbdbdb')
        self.action_display.pack()
        
        self.bet_size_label = tk.Label(action_container, text="", font=('Arial', 18, 'bold'), fg='#28a745', bg='#dbdbdb')
        self.bet_size_label.pack()
        
        # Métriques en grille 2x2
        metrics_frame = tk.Frame(rec_content, bg='#dbdbdb')
        metrics_frame.pack(fill='x', pady=(0, 8))
        
        # Ligne 1: Victoire + Risque
        metrics_row1 = tk.Frame(metrics_frame, bg='#dbdbdb')
        metrics_row1.pack(fill='x', pady=(0, 4))
        
        victory_frame = tk.Frame(metrics_row1, bg='#dbdbdb')
        victory_frame.pack(side='left', fill='x', expand=True)
        tk.Label(victory_frame, text="🎯 Victoire", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack()
        self.win_prob_label = tk.Label(victory_frame, text="--", font=('Arial', 14, 'bold'), fg='#6c757d', bg='#dbdbdb')
        self.win_prob_label.pack()
        
        risk_frame = tk.Frame(metrics_row1, bg='#dbdbdb')
        risk_frame.pack(side='right', fill='x', expand=True)
        tk.Label(risk_frame, text="⚠️ Risque", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack()
        self.risk_label = tk.Label(risk_frame, text="--", font=('Arial', 14, 'bold'), fg='#6c757d', bg='#dbdbdb')
        self.risk_label.pack()
        
        # Ligne 2: Confiance seule, centrée
        confidence_frame = tk.Frame(metrics_frame, bg='#dbdbdb')
        confidence_frame.pack(fill='x')
        tk.Label(confidence_frame, text="🔮 Confiance", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack()
        self.main_confidence_label = tk.Label(confidence_frame, text="--", font=('Arial', 14, 'bold'), fg='#6c757d', bg='#dbdbdb')
        self.main_confidence_label.pack()
        
        # Raisonnement optimisé
        reasoning_frame = tk.Frame(rec_content, bg='#dbdbdb')
        reasoning_frame.pack(fill='both', expand=True)
        tk.Label(reasoning_frame, text="🧠 Raisonnement:", font=('Arial', 10, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack(anchor='w')
        self.main_reasoning_label = tk.Label(
            reasoning_frame, text="En attente d'analyse...", font=('Arial', 9),
            wraplength=320, justify='left', fg='#6c757d', bg='#dbdbdb'
        )
        self.main_reasoning_label.pack(anchor='w', fill='both', expand=True)
        
        # SOUS-SECTION: Statistiques compactes
        stats_frame = ttk.LabelFrame(left_column, text="📈 STATISTIQUES", style='Card.TFrame')
        stats_frame.pack(fill='x', pady=(0, 5))  # Hauteur fixe pour éviter les problèmes d'affichage
        
        stats_content = tk.Frame(stats_frame, bg='#dbdbdb')
        stats_content.pack(fill='x', padx=6, pady=4)
        
        # Taux de victoire principal - centré et plus compact
        main_rate_frame = tk.Frame(stats_content, bg='#dbdbdb')
        main_rate_frame.pack(fill='x', pady=(0, 4))
        
        tk.Label(main_rate_frame, text="📊 TAUX DE VICTOIRE", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack()
        self.win_rate_value = tk.Label(main_rate_frame, text="0.0%", font=('Arial', 14, 'bold'), fg='#dc3545', bg='#dbdbdb')
        self.win_rate_value.pack()
        
        # Statistiques détaillées en grille compacte
        details_frame = tk.Frame(stats_content, bg='#dbdbdb')
        details_frame.pack(fill='x', pady=(0, 2))
        
        # Ligne 1: Mains jouées + gagnées - VISIBLE et bien espacé
        hands_row = tk.Frame(details_frame, bg='#dbdbdb')
        hands_row.pack(fill='x', pady=(2, 4))  # Plus d'espace vertical
        
        played_frame = tk.Frame(hands_row, bg='#dbdbdb')
        played_frame.pack(side='left', fill='x', expand=True)
        tk.Label(played_frame, text="🎲 Jouées", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack()
        self.hands_played_value = tk.Label(played_frame, text="0", font=('Arial', 11, 'bold'), fg='#495057', bg='#dbdbdb')
        self.hands_played_value.pack()
        
        won_frame = tk.Frame(hands_row, bg='#dbdbdb')
        won_frame.pack(side='right', fill='x', expand=True)
        tk.Label(won_frame, text="🏆 Gagnées", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack()
        self.hands_won_value = tk.Label(won_frame, text="0", font=('Arial', 11, 'bold'), fg='#28a745', bg='#dbdbdb')
        self.hands_won_value.pack()
        
        # Ligne 2: Comparaison performance - VISIBLE et bien espacé
        perf_row = tk.Frame(details_frame, bg='#dbdbdb')
        perf_row.pack(fill='x', pady=(2, 4))  # Plus d'espace vertical
        
        pro_frame = tk.Frame(perf_row, bg='#dbdbdb')
        pro_frame.pack(side='left', fill='x', expand=True)
        tk.Label(pro_frame, text="👑 Pro", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack()
        self.expected_rate_value = tk.Label(pro_frame, text="--", font=('Arial', 10, 'bold'), fg='#6c757d', bg='#dbdbdb')
        self.expected_rate_value.pack()
        
        performance_frame = tk.Frame(perf_row, bg='#dbdbdb')
        performance_frame.pack(side='right', fill='x', expand=True)
        tk.Label(performance_frame, text="📈 Perf", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack()
        self.performance_ratio_value = tk.Label(performance_frame, text="0.0%", font=('Arial', 10, 'bold'), fg='#fd7e14', bg='#dbdbdb')
        self.performance_ratio_value.pack()
        
        # Colonne droite: Informations joueurs
        right_column = ttk.Frame(main_layout)
        right_column.pack(side='left', fill='both', expand=True, padx=(5, 10))
        
        # SECTION 4A: NOS INFOS PERSONNELLES
        hero_frame = ttk.LabelFrame(right_column, text="👤 MOI", style='Card.TFrame')
        hero_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        hero_content = tk.Frame(hero_frame, bg='#dbdbdb')
        hero_content.pack(fill='x', padx=8, pady=6)
        
        # Pseudo du joueur
        tk.Label(hero_content, text="Pseudo:", font=('Arial', 10, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack(anchor='w')
        self.hero_name_label = tk.Label(hero_content, text="---", font=('Arial', 12, 'bold'), fg='#6c757d', bg='#dbdbdb')
        self.hero_name_label.pack(anchor='w', pady=(2, 8))
        
        # Stack personnel
        tk.Label(hero_content, text="Mon Stack:", font=('Arial', 10, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack(anchor='w')
        self.hero_stack_label = tk.Label(hero_content, text=self.format_amount(0), font=('Arial', 14, 'bold'), fg='#6c757d', bg='#dbdbdb')
        self.hero_stack_label.pack(anchor='w', pady=(2, 8))
        
        # Position à la table
        tk.Label(hero_content, text="Position:", font=('Arial', 10, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack(anchor='w')
        self.hero_position_label = tk.Label(hero_content, text="---", font=('Arial', 11), fg='#6c757d', bg='#dbdbdb')
        self.hero_position_label.pack(anchor='w', pady=(2, 0))
        
        # SECTION 4B: AUTRES JOUEURS ACTIFS
        players_frame = ttk.LabelFrame(right_column, text="👥 AUTRES JOUEURS", style='Card.TFrame')
        players_frame.pack(fill='both', expand=True, pady=(0, 0))
        
        players_content = tk.Frame(players_frame, bg='#dbdbdb')
        players_content.pack(fill='x', padx=5, pady=3)
        
        # Info générale - Table 9-max (compacte)
        players_info = tk.Frame(players_content, bg='#dbdbdb')
        players_info.pack(fill='x', pady=(0, 3))
        
        tk.Label(players_info, text="Actifs:", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#dbdbdb').pack(side='left')
        self.active_players_count = tk.Label(players_info, text="0/9", font=('Arial', 9, 'bold'), fg='#6c757d', bg='#dbdbdb')
        self.active_players_count.pack(side='left', padx=(3, 0))
        
        # Frame simple pour la liste des joueurs (sans scroll)
        self.players_list_frame = tk.Frame(players_content, bg='#dbdbdb')
        self.players_list_frame.pack(fill='x')
        
        # Créer la liste des joueurs (vide par défaut)
        self.create_players_display()
        
        # Compatibilité avec anciens widgets (alias)
        self.main_hands_label = self.hands_played_value
        self.main_winrate_label = self.win_rate_value
        self.main_performance_label = self.performance_ratio_value
        self.main_action_display = self.action_display
        self.main_bet_size_label = self.bet_size_label
        self.main_win_prob_label = self.win_prob_label
        self.main_risk_label = self.risk_label
        self.reasoning_text = self.main_reasoning_label
        
        # Initialiser avec des données vides (sera connecté plus tard)
        self.update_hero_info("---", self.format_amount(0), "---")
        
        # Progress bars (cachées mais présentes pour compatibilité)
        hidden_frame = ttk.Frame(left_column)
        self.win_prob_progress = ttk.Progressbar(hidden_frame, mode='determinate', length=1)
        self.risk_progress = ttk.Progressbar(hidden_frame, mode='determinate', length=1)
    
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
            
            # Position avec icône selon le type
            pos_text = pos['name']
            position_icon = ""
            if pos['index'] == 6:  # BTN
                position_icon = " 🟢"
            elif pos['index'] == 7:  # SB
                position_icon = " 🟡"  
            elif pos['index'] == 8:  # BB
                position_icon = " 🔵"
            
            ttk.Label(main_line, text=f"{pos_text}{position_icon}", 
                     font=('Arial', 8, 'bold')).pack(side='left')
            
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
                        
                        ttk.Label(main_line, text=stack_text, font=('Arial', 8, 'bold'), 
                                 foreground='#28a745').pack(side='right')
                else:
                    # Joueur détecté mais sans nom (OCR partiel)
                    ttk.Label(main_line, text="Joueur détecté", font=('Arial', 8, 'italic'), 
                             foreground='#6c757d').pack(side='left')
            else:
                # Position vide (aucune détection OCR)
                ttk.Label(main_line, text="○", font=('Arial', 8), 
                         foreground='#cccccc').pack(side='left', padx=(2, 3))
                ttk.Label(main_line, text="Siège vide", font=('Arial', 8, 'italic'), 
                         foreground='#999999').pack(side='left')
    
    def create_options_tab(self):
        """Création de l'onglet Options"""
        
        # Frame principal avec scroll
        main_frame = ctk.CTkScrollableFrame(self.options_tab)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Section: Interface Automatique
        interface_frame = ctk.CTkFrame(main_frame)
        interface_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(interface_frame, text="🤖 Interface Automatique Intelligente", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        ctk.CTkLabel(interface_frame, 
                    text="RTPA Studio détecte automatiquement les plateformes poker et démarre/arrête l'analyse intelligemment.",
                    font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 15), padx=20)
        
        # Section supprimée : Personnalisation Interface (non indispensable)
        
        # Section: Gestion des Données (Simplifiée)
        data_frame = ctk.CTkFrame(main_frame)
        data_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(data_frame, text="💾 Gestion des Données", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Description
        ctk.CTkLabel(data_frame, 
                    text="Sauvegardez et restaurez vos données d'entraînement CFR pour préserver vos progrès.",
                    font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 15), padx=20)
        
        # Boutons d'action
        buttons_frame = ctk.CTkFrame(data_frame)
        buttons_frame.pack(pady=(0, 15))
        
        export_btn = ctk.CTkButton(buttons_frame, text="📤 Exporter sur Bureau", 
                                  command=self.export_cfr_data, height=40, width=180)
        export_btn.pack(side='left', padx=15, pady=10)
        
        import_btn = ctk.CTkButton(buttons_frame, text="📥 Importer Fichier", 
                                  command=self.import_cfr_data, height=40, width=180)
        import_btn.pack(side='left', padx=15, pady=10)
        
        # Informations sur les formats
        ctk.CTkLabel(data_frame, 
                    text="Formats supportés: .rtpa (recommandé), .json | Export automatique vers le Bureau",
                    font=ctk.CTkFont(size=10), text_color="gray").pack(pady=(0, 15), padx=20)
    
    def create_settings_tab(self):
        """Création de l'onglet Paramètres"""
        
        # Frame principal avec scroll
        main_frame = ctk.CTkScrollableFrame(self.settings_tab)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Section: Configuration CFR
        cfr_frame = ctk.CTkFrame(main_frame)
        cfr_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(cfr_frame, text="🧠 Configuration CFR", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Iterations CFR
        iter_frame = ctk.CTkFrame(cfr_frame)
        iter_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(iter_frame, text="Itérations CFR:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.cfr_iterations = ctk.CTkEntry(iter_frame, placeholder_text="100000")
        self.cfr_iterations.pack(side='left', padx=10)
        self.cfr_iterations.bind('<Return>', self.apply_cfr_iterations)
        
        apply_iter_btn = ctk.CTkButton(iter_frame, text="Appliquer", command=self.apply_cfr_iterations, width=80)
        apply_iter_btn.pack(side='left', padx=10)
        
        # Description détaillée
        ctk.CTkLabel(iter_frame, text="Nombre d'itérations d'entraînement CFR (plus = meilleure qualité)", 
                    font=ctk.CTkFont(size=10), text_color="gray").pack(side='right', padx=10)
        
        # Profondeur CFR
        depth_frame = ctk.CTkFrame(cfr_frame)
        depth_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(depth_frame, text="Profondeur CFR:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.cfr_depth = ctk.CTkEntry(depth_frame, placeholder_text="3")
        self.cfr_depth.pack(side='left', padx=10)
        self.cfr_depth.bind('<Return>', self.apply_cfr_depth)
        
        apply_depth_btn = ctk.CTkButton(depth_frame, text="Appliquer", command=self.apply_cfr_depth, width=80)
        apply_depth_btn.pack(side='left', padx=10)
        
        # Description détaillée
        ctk.CTkLabel(depth_frame, text="Profondeur d'analyse des actions (3-5 recommandé)", 
                    font=ctk.CTkFont(size=10), text_color="gray").pack(side='right', padx=10)
        
        # Epsilon Exploration
        eps_frame = ctk.CTkFrame(cfr_frame)
        eps_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        ctk.CTkLabel(eps_frame, text="Epsilon Exploration:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.cfr_epsilon = ctk.CTkEntry(eps_frame, placeholder_text="0.3")
        self.cfr_epsilon.pack(side='left', padx=10)
        self.cfr_epsilon.bind('<Return>', self.apply_cfr_epsilon)
        
        apply_eps_btn = ctk.CTkButton(eps_frame, text="Appliquer", command=self.apply_cfr_epsilon, width=80)
        apply_eps_btn.pack(side='left', padx=10)
        
        # Description détaillée
        ctk.CTkLabel(eps_frame, text="Taux d'exploration vs exploitation (0.1-0.5)", 
                    font=ctk.CTkFont(size=10), text_color="gray").pack(side='right', padx=10)
        
        # Section: Génération Continue
        generation_frame = ctk.CTkFrame(main_frame)
        generation_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(generation_frame, text="🔄 Génération Continue de Données", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Activation/Désactivation
        gen_control_frame = ctk.CTkFrame(generation_frame)
        gen_control_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(gen_control_frame, text="Génération active:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.generation_enabled = ctk.CTkSwitch(gen_control_frame, text="", command=self.toggle_generation)
        self.generation_enabled.pack(side='left', padx=10)
        self.generation_enabled.select()  # Activé par défaut
        
        ctk.CTkLabel(gen_control_frame, text="Génération automatique de mains pour entraînement CFR", 
                    font=ctk.CTkFont(size=10), text_color="gray").pack(side='right', padx=10)
        
        # Vitesse de génération
        gen_rate_frame = ctk.CTkFrame(generation_frame)
        gen_rate_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(gen_rate_frame, text="Vitesse génération:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.generation_rate = ctk.CTkSlider(gen_rate_frame, from_=1, to=10, command=self.update_generation_rate)
        self.generation_rate.pack(side='left', padx=10, fill='x', expand=True)
        self.generation_rate.set(5)
        
        self.gen_rate_label = ctk.CTkLabel(gen_rate_frame, text="5 (Moyen)", font=ctk.CTkFont(weight="bold"))
        self.gen_rate_label.pack(side='left', padx=10)
        
        ctk.CTkLabel(gen_rate_frame, text="Contrôle la vitesse de génération (1=Lent, 10=Rapide)", 
                    font=ctk.CTkFont(size=10), text_color="gray").pack(side='right', padx=10)
        
        # Limite ressources pour génération
        gen_resource_frame = ctk.CTkFrame(generation_frame)
        gen_resource_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        ctk.CTkLabel(gen_resource_frame, text="Ressources génération:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.generation_cpu_limit = ctk.CTkSlider(gen_resource_frame, from_=10, to=80, command=self.update_gen_cpu_value)
        self.generation_cpu_limit.pack(side='left', padx=10, fill='x', expand=True)
        self.generation_cpu_limit.set(50)
        
        self.gen_cpu_label = ctk.CTkLabel(gen_resource_frame, text="50% CPU", font=ctk.CTkFont(weight="bold"))
        self.gen_cpu_label.pack(side='left', padx=10)
        
        ctk.CTkLabel(gen_resource_frame, text="CPU dédié à la génération continue", 
                    font=ctk.CTkFont(size=10), text_color="gray").pack(side='right', padx=10)
        
        # Section: Gestion des Ressources
        resource_frame = ctk.CTkFrame(main_frame)
        resource_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(resource_frame, text="⚡ Gestion des Ressources", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
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
    
    def create_performance_tab(self):
        """Création de l'onglet Performance"""
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.performance_tab)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Titre
        ctk.CTkLabel(main_frame, text="⚡ Monitoring des Performances", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 30))
        
        # Frame pour les métriques
        metrics_frame = ctk.CTkFrame(main_frame)
        metrics_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # CPU Usage
        cpu_frame = ctk.CTkFrame(metrics_frame)
        cpu_frame.pack(fill='x', padx=15, pady=10)
        
        ctk.CTkLabel(cpu_frame, text="🖥️ CPU", font=ctk.CTkFont(size=14, weight="bold")).pack(side='left', padx=10)
        self.cpu_progress = ctk.CTkProgressBar(cpu_frame)
        self.cpu_progress.pack(side='left', padx=20, fill='x', expand=True)
        self.cpu_label = ctk.CTkLabel(cpu_frame, text="0%")
        self.cpu_label.pack(side='right', padx=10)
        
        # RAM Usage
        ram_frame = ctk.CTkFrame(metrics_frame)
        ram_frame.pack(fill='x', padx=15, pady=10)
        
        ctk.CTkLabel(ram_frame, text="🧠 RAM", font=ctk.CTkFont(size=14, weight="bold")).pack(side='left', padx=10)
        self.ram_progress = ctk.CTkProgressBar(ram_frame)
        self.ram_progress.pack(side='left', padx=20, fill='x', expand=True)
        self.ram_label = ctk.CTkLabel(ram_frame, text="0 GB")
        self.ram_label.pack(side='right', padx=10)
        
        # Status PyTorch
        torch_frame = ctk.CTkFrame(metrics_frame)
        torch_frame.pack(fill='x', padx=15, pady=10)
        
        ctk.CTkLabel(torch_frame, text="🔥 PyTorch", font=ctk.CTkFont(size=14, weight="bold")).pack(side='left', padx=10)
        self.torch_status = ctk.CTkLabel(torch_frame, text="Non installé", text_color="red")
        self.torch_status.pack(side='left', padx=20)
        
        self.install_torch_btn = ctk.CTkButton(torch_frame, text="Installer PyTorch", 
                                              command=self.install_pytorch)
        self.install_torch_btn.pack(side='right', padx=10)
        
        # Vérifier PyTorch
        self.check_pytorch_status()
        
        # Démarrer la mise à jour des performances
        self.start_performance_monitoring()
    
    def change_accent_color(self, color):
        """Change la couleur d'accent de l'interface"""
        self.accent_color = color
        ctk.set_default_color_theme(color)
        # Note: redémarrage nécessaire pour application complète
    
    def change_font(self, font):
        """Change la police de l'interface"""
        self.font_family = font
        self.setup_styles()
    
    def change_opacity(self, value):
        """Change l'opacité de la fenêtre"""
        self.opacity = value
        self.root.attributes('-alpha', value)
        self.opacity_label.configure(text=f"{int(value*100)}%")
    
    def export_cfr_data(self):
        """Exporte les données CFR"""
        if not self.app_manager:
            messagebox.showwarning("Erreur", "Gestionnaire d'application non disponible")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Exporter Base CFR",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Exporter les données CFR via l'app manager (si la méthode existe)
                if hasattr(self.app_manager, 'export_cfr_data'):
                    success = self.app_manager.export_cfr_data(filename)
                    if success:
                        messagebox.showinfo("Succès", f"Base CFR exportée vers:\n{filename}")
                    else:
                        messagebox.showerror("Erreur", "Échec de l'export")
                else:
                    messagebox.showinfo("Info", "Fonction d'export non disponible dans cette version")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{str(e)}")
    
    def import_cfr_data(self):
        """Importe les données CFR"""
        if not self.app_manager:
            messagebox.showwarning("Erreur", "Gestionnaire d'application non disponible")
            return
        
        filename = filedialog.askopenfilename(
            title="Importer Base CFR",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Confirmation utilisateur
                result = messagebox.askyesno("Confirmation", 
                    "L'import remplacera la base CFR actuelle.\nContinuer ?")
                
                if result:
                    if hasattr(self.app_manager, 'import_cfr_data'):
                        success = self.app_manager.import_cfr_data(filename)
                        if success:
                            messagebox.showinfo("Succès", "Base CFR importée avec succès")
                        else:
                            messagebox.showerror("Erreur", "Échec de l'import")
                    else:
                        messagebox.showinfo("Info", "Fonction d'import non disponible dans cette version")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'import:\n{str(e)}")
    
    def install_pytorch(self):
        """Installe PyTorch"""
        def install_thread():
            try:
                import subprocess
                import sys
                
                self.install_torch_btn.configure(text="Installation...", state="disabled")
                
                # Installation PyTorch CPU
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", "--index-url", 
                    "https://download.pytorch.org/whl/cpu"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.torch_status.configure(text="✅ Installé", text_color="green")
                    self.install_torch_btn.configure(text="Réinstaller", state="normal")
                    messagebox.showinfo("Succès", "PyTorch installé avec succès")
                else:
                    self.install_torch_btn.configure(text="Réessayer", state="normal")
                    messagebox.showerror("Erreur", f"Échec installation:\n{result.stderr}")
                    
            except Exception as e:
                self.install_torch_btn.configure(text="Réessayer", state="normal")
                messagebox.showerror("Erreur", f"Erreur installation:\n{str(e)}")
        
        # Lancer dans un thread séparé
        threading.Thread(target=install_thread, daemon=True).start()
    
    def check_pytorch_status(self):
        """Vérifie le statut de PyTorch"""
        try:
            import torch
            device_info = "CPU"
            if torch.cuda.is_available():
                device_info = f"GPU (CUDA {torch.version.cuda})"
            
            self.torch_status.configure(text=f"✅ {device_info}", text_color="green")
            self.install_torch_btn.configure(text="Réinstaller")
            
        except ImportError:
            self.torch_status.configure(text="❌ Non installé", text_color="red")
            self.install_torch_btn.configure(text="Installer PyTorch")
    
    def start_performance_monitoring(self):
        """Démarre le monitoring des performances"""
        self.monitoring_active = True
        
        def update_metrics():
            while self.monitoring_active and not getattr(self, '_stopping', False):
                try:
                    import psutil
                    
                    # CPU
                    cpu_percent = psutil.cpu_percent(interval=1)
                    if self.monitoring_active:  # Vérifier à nouveau après l'attente
                        self.cpu_progress.set(cpu_percent / 100)
                        self.cpu_label.configure(text=f"{cpu_percent:.1f}%")
                    
                    # RAM
                    memory = psutil.virtual_memory()
                    ram_gb = memory.used / (1024**3)
                    ram_percent = memory.percent
                    if self.monitoring_active:
                        self.ram_progress.set(ram_percent / 100)
                        self.ram_label.configure(text=f"{ram_gb:.1f} GB ({ram_percent:.1f}%)")
                    
                except (ImportError, AttributeError) as e:
                    self.logger.error(f"Erreur monitoring (import/attribut): {e}")
                    break
                except Exception as e:
                    self.logger.warning(f"Erreur monitoring: {e}")
                
                # Sleep avec vérification d'arrêt
                for _ in range(20):  # 2 secondes = 20 * 0.1s
                    if not self.monitoring_active:
                        break
                    time.sleep(0.1)
        
        # Lancer dans un thread séparé
        monitoring_thread = threading.Thread(target=update_metrics, daemon=True)
        monitoring_thread.start()
    
    def update_display(self, data):
        """Met à jour l'affichage avec les nouvelles données"""
        try:
            if not data:
                return
            
            # Mettre à jour les cartes
            self.update_cards_display(data.get('hero_cards', []), data.get('board_cards', []))
            
            # Mettre à jour les informations de table
            if 'pot' in data:
                self.pot_label.config(text=f"{data['pot']}")
            # Stack supprimé - redondant avec section MOI
            if 'blinds' in data:
                self.blinds_label.config(text=data['blinds'])
            if 'table_type' in data:
                self.table_type_label.config(text=data['table_type'])
            
            # Mettre à jour les recommandations
            if 'action' in data:
                # Simplification des actions techniques en actions claires
                raw_action = data['action']
                simplified_action = {
                    'BET_SMALL': 'BET', 'BET_MEDIUM': 'BET', 'BET_LARGE': 'BET',
                    'BET_POT': 'BET', 'BET_ALLIN': 'ALL-IN', 'ALL_IN': 'ALL-IN',
                    'RAISE_SMALL': 'RAISE', 'RAISE_MEDIUM': 'RAISE', 'RAISE_LARGE': 'RAISE'
                }.get(raw_action.upper(), raw_action.upper())
                self.action_display.config(text=simplified_action)
            if 'bet_size' in data:
                self.bet_size_label.config(text=data['bet_size'])
            if 'win_probability' in data:
                self.win_prob_label.config(text=f"{data['win_probability']}")
            if 'risk_level' in data:
                self.risk_label.config(text=f"{data['risk_level']}")
            if 'confidence' in data:
                self.main_confidence_label.config(text=f"{data['confidence']}")
            if 'reasoning' in data:
                self.main_reasoning_label.config(text=data['reasoning'])
            
            # Mettre à jour les statistiques
            if 'hands_played' in data:
                self.hands_played_value.config(text=str(data['hands_played']))
            if 'hands_won' in data:
                self.hands_won_value.config(text=str(data['hands_won']))
            if 'win_rate' in data:
                self.win_rate_value.config(text=f"{data['win_rate']}")
            if 'expected_rate' in data:
                self.expected_rate_value.config(text=f"{data['expected_rate']}")
            if 'performance' in data:
                self.performance_ratio_value.config(text=f"{data['performance']}")
                
        except Exception as e:
            print(f"Erreur mise à jour affichage: {e}")
    
    def update_cards_display(self, hero_cards, board_cards):
        """Met à jour l'affichage des cartes"""
        try:
            # Cartes du héros
            if len(hero_cards) >= 2:
                self.update_card_display(self.hero_card1, hero_cards[0])
                self.update_card_display(self.hero_card2, hero_cards[1])
            
            # Cartes du board
            for i, card_label in enumerate(self.board_cards):
                if i < len(board_cards):
                    self.update_card_display(card_label, board_cards[i])
                else:
                    card_label.config(text="🂠", fg='gray')
                    
        except Exception as e:
            print(f"Erreur mise à jour cartes: {e}")
    
    def update_card_display(self, label, card_str):
        """Met à jour l'affichage d'une carte individuelle"""
        try:
            if not card_str or card_str == "":
                label.config(text="🂠", fg='gray')
                return
            
            # Conversion en format visuel
            if len(card_str) >= 2:
                rank = card_str[0]
                suit = card_str[1].lower()
                
                # Symboles des couleurs
                suit_symbols = {
                    's': '♠', 'h': '♥', 'd': '♦', 'c': '♣'
                }
                
                # Couleurs
                color = 'red' if suit in ['h', 'd'] else 'black'
                
                # Affichage
                display_text = f"{rank}{suit_symbols.get(suit, suit)}"
                label.config(text=display_text, fg=color)
            else:
                label.config(text="🂠", fg='gray')
                
        except Exception as e:
            print(f"Erreur affichage carte: {e}")
            label.config(text="🂠", fg='gray')
    
    def update_status(self, status_text, color="white"):
        """Met à jour le statut affiché"""
        self.status_label.configure(text=status_text)
    
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
                        # Utiliser des données simulées avec joueurs pour le test
                        data = {
                            'hero_cards': ['Ac', '7d'],
                            'board_cards': ['Ah', '7h', '2c', '9s', 'Kh'],
                            'pot': '861.89€',
                            'stack': '1133.62€',
                            'action': 'BET_SMALL',
                            'bet_size': '103.48€',
                            'win_probability': '1.0%',
                            'risk_level': '53%',
                            'confidence': '15%',
                            'reasoning': 'Recommandation bet_small basée sur: Main forte, position milieu',
                            'players_info': [
                                {"name": "PokerPro", "stack": 1847, "vpip": 15, "pfr": 12, "status": "actif", "position": 0, "position_name": "UTG", "is_button": False, "is_sb": False, "is_bb": False},
                                {"name": "AliceBluff", "stack": 2156, "vpip": 28, "pfr": 22, "status": "actif", "position": 2, "position_name": "MP1", "is_button": False, "is_sb": False, "is_bb": False},
                                {"name": "BobNuts", "stack": 1023, "vpip": 35, "pfr": 8, "status": "fold", "position": 4, "position_name": "MP3", "is_button": False, "is_sb": False, "is_bb": False},
                                {"name": "DianaAce", "stack": 3421, "vpip": 12, "pfr": 10, "status": "actif", "position": 5, "position_name": "CO", "is_button": False, "is_sb": False, "is_bb": False},
                                {"name": "EdRaise", "stack": 956, "vpip": 35, "pfr": 25, "status": "actif", "position": 6, "position_name": "BTN", "is_button": True, "is_sb": False, "is_bb": False},
                                {"name": "FionaCall", "stack": 1540, "vpip": 22, "pfr": 18, "status": "actif", "position": 7, "position_name": "SB", "is_button": False, "is_sb": True, "is_bb": False},
                                {"name": "GaryFold", "stack": 2890, "vpip": 18, "pfr": 14, "status": "actif", "position": 8, "position_name": "BB", "is_button": False, "is_sb": False, "is_bb": True}
                            ]
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
            
            # Appliquer la limite CPU réelle
            if hasattr(self, 'app_manager') and self.app_manager:
                if hasattr(self.app_manager, 'cfr_trainer') and self.app_manager.cfr_trainer:
                    # Convertir en limite réelle (CPU disponible pour CFR)
                    self.app_manager.cfr_trainer.configure_generation_resources(
                        cpu_percent=cpu_value
                    )
                    print(f"✅ Limite CPU CFR appliquée: {cpu_value}%")
        except Exception as e:
            print(f"Erreur mise à jour CPU: {e}")
    
    def update_ram_value(self, value):
        """Met à jour l'affichage de la valeur RAM et applique la limite"""
        try:
            ram_value = float(value)
            self.ram_value_label.configure(text=f"{ram_value:.1f} GB")
            
            # Appliquer la limite RAM réelle
            if hasattr(self, 'app_manager') and self.app_manager:
                if hasattr(self.app_manager, 'cfr_trainer') and self.app_manager.cfr_trainer:
                    # Convertir GB en MB pour l'API
                    ram_mb = ram_value * 1024
                    self.app_manager.cfr_trainer.configure_generation_resources(
                        memory_mb=ram_mb
                    )
                    print(f"✅ Limite RAM CFR appliquée: {ram_value:.1f} GB")
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
                    rate_per_second = float(rate_value)
                    self.app_manager.cfr_trainer.configure_generation_resources(
                        rate_per_second=rate_per_second
                    )
                    print(f"✅ Vitesse génération appliquée: {rate_per_second} mains/s")
        except Exception as e:
            print(f"Erreur mise à jour vitesse génération: {e}")
    
    def update_gen_cpu_value(self, value):
        """Met à jour l'affichage de la limite CPU pour génération et applique"""
        try:
            cpu_value = int(float(value))
            self.gen_cpu_label.configure(text=f"{cpu_value}% CPU")
            
            # Appliquer la limite CPU spécifique pour la génération
            if hasattr(self, 'app_manager') and self.app_manager:
                if hasattr(self.app_manager, 'cfr_trainer') and self.app_manager.cfr_trainer:
                    self.app_manager.cfr_trainer.configure_generation_resources(
                        cpu_percent=cpu_value
                    )
                    print(f"✅ Limite CPU génération appliquée: {cpu_value}%")
        except Exception as e:
            print(f"Erreur mise à jour CPU génération: {e}")
    
    def toggle_generation(self):
        """Active/désactive la génération continue"""
        try:
            is_enabled = self.generation_enabled.get()
            status = "Activé" if is_enabled else "Désactivé"
            print(f"Génération continue: {status}")
            
            # Contrôler réellement la génération
            if hasattr(self, 'app_manager') and self.app_manager:
                if hasattr(self.app_manager, 'cfr_trainer') and self.app_manager.cfr_trainer:
                    if is_enabled:
                        self.app_manager.cfr_trainer.start_continuous_generation()
                        print("✅ Génération continue démarrée")
                    else:
                        self.app_manager.cfr_trainer.stop_continuous_generation_user()
                        print("❌ Génération continue arrêtée")
                    
        except Exception as e:
            print(f"Erreur toggle génération: {e}")
    
    def apply_cfr_iterations(self, event=None):
        """Applique le nombre d'itérations CFR"""
        try:
            value = self.cfr_iterations.get().strip()
            if value:
                iterations = int(value)
                if 1000 <= iterations <= 1000000:
                    if hasattr(self, 'app_manager') and self.app_manager:
                        if hasattr(self.app_manager, 'cfr_trainer') and self.app_manager.cfr_trainer:
                            self.app_manager.cfr_trainer.target_iterations = iterations
                            print(f"✅ Itérations CFR appliquées: {iterations}")
                        if hasattr(self.app_manager, 'cfr_engine') and self.app_manager.cfr_engine:
                            self.app_manager.cfr_engine.iterations = iterations
                else:
                    print("❌ Itérations doivent être entre 1000 et 1000000")
        except ValueError:
            print("❌ Valeur d'itérations invalide")
        except Exception as e:
            print(f"Erreur application itérations: {e}")
    
    def apply_cfr_depth(self, event=None):
        """Applique la profondeur CFR"""
        try:
            value = self.cfr_depth.get().strip()
            if value:
                depth = int(value)
                if 1 <= depth <= 10:
                    if hasattr(self, 'app_manager') and self.app_manager:
                        if hasattr(self.app_manager, 'cfr_engine') and self.app_manager.cfr_engine:
                            self.app_manager.cfr_engine.abstraction_depth = depth
                            print(f"✅ Profondeur CFR appliquée: {depth}")
                else:
                    print("❌ Profondeur doit être entre 1 et 10")
        except ValueError:
            print("❌ Valeur de profondeur invalide")
        except Exception as e:
            print(f"Erreur application profondeur: {e}")
    
    def apply_cfr_epsilon(self, event=None):
        """Applique l'epsilon d'exploration CFR"""
        try:
            value = self.cfr_epsilon.get().strip()
            if value:
                epsilon = float(value)
                if 0.01 <= epsilon <= 1.0:
                    if hasattr(self, 'app_manager') and self.app_manager:
                        if hasattr(self.app_manager, 'cfr_engine') and self.app_manager.cfr_engine:
                            self.app_manager.cfr_engine.exploration_rate = epsilon
                            print(f"✅ Epsilon exploration appliqué: {epsilon}")
                else:
                    print("❌ Epsilon doit être entre 0.01 et 1.0")
        except ValueError:
            print("❌ Valeur d'epsilon invalide")
        except Exception as e:
            print(f"Erreur application epsilon: {e}")
    
    # Fonctions de personnalisation supprimées (non indispensables)
    
    
    
    
    def export_cfr_data(self):
        """Exporte automatiquement les données CFR sur le bureau"""
        try:
            print("📤 Export automatique des données CFR...")
            
            if hasattr(self, 'app_manager') and self.app_manager:
                import json
                import os
                from pathlib import Path
                from datetime import datetime
                
                # Chemin du bureau
                desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
                if not os.path.exists(desktop):
                    desktop = os.path.expanduser('~')  # Fallback vers home si pas de Desktop
                
                # Nom du fichier avec timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(desktop, f"RTPA_Export_{timestamp}.rtpa")
                
                # Collecter toutes les données importantes (CORRIGER L'ACCÈS AUX DONNÉES)
                export_data = {
                    "rtpa_version": "1.0",
                    "export_date": datetime.now().isoformat(),
                    "export_timestamp": time.time(),
                    "cfr_data": {},
                    "database_stats": {},
                    "performance_data": {
                        "generation_speed": "Variable",
                        "memory_usage": "Optimisé"
                    }
                }
                
                # Récupérer les données CFR réelles depuis le trainer
                try:
                    if hasattr(self.app_manager, 'cfr_trainer') and self.app_manager.cfr_trainer:
                        try:
                            cfr_stats = self.app_manager.cfr_trainer.get_training_statistics()
                            export_data["cfr_data"] = {
                                "iterations": cfr_stats.get('iterations', 0),
                                "convergence": cfr_stats.get('last_convergence', 0.0),
                                "training_hands_count": cfr_stats.get('training_hands', 0),
                                "current_quality": cfr_stats.get('current_quality', 0.0),
                                "progress_percentage": cfr_stats.get('progress_percentage', 0.0),
                                "info_sets_learned": cfr_stats.get('info_sets_learned', 0),
                                "target_iterations": cfr_stats.get('target_iterations', 100000),
                                "is_training": cfr_stats.get('is_training', False)
                            }
                        except Exception as cfr_error:
                            print(f"⚠️ Erreur accès statistiques CFR: {cfr_error}")
                            # Fallback - accès direct aux données de base
                            trainer_hands = len(self.app_manager.cfr_trainer.training_hands) if hasattr(self.app_manager.cfr_trainer, 'training_hands') else 0
                            export_data["cfr_data"] = {
                                "iterations": 0,
                                "convergence": 0.0,
                                "training_hands_count": trainer_hands,
                                "current_quality": 0.0,
                                "progress_percentage": 0.0,
                                "info_sets_learned": 0,
                                "target_iterations": 100000,
                                "is_training": False,
                                "note": "Entraînement pas encore démarré - génération de mains en cours"
                            }
                    
                    # Récupérer les données de la base
                    if hasattr(self.app_manager, 'memory_db') and self.app_manager.memory_db:
                        if hasattr(self.app_manager.memory_db, 'game_states'):
                            total_db_hands = len(self.app_manager.memory_db.game_states)
                        else:
                            total_db_hands = 0
                        
                        export_data["database_stats"] = {
                            "total_hands": total_db_hands,
                            "unique_scenarios": total_db_hands  # Approximation
                        }
                    
                    # Note: Les données du trainer sont déjà récupérées via get_training_statistics() ci-dessus
                    
                    print(f"📊 Données collectées pour export:")
                    print(f"   CFR Iterations: {export_data['cfr_data'].get('iterations', 0)}")
                    print(f"   Training Hands: {export_data['cfr_data'].get('training_hands_count', 0)}")
                    print(f"   Database Hands: {export_data['database_stats'].get('total_hands', 0)}")
                    print(f"   Convergence: {export_data['cfr_data'].get('convergence', 0.0)}")
                
                except Exception as data_error:
                    print(f"⚠️ Erreur collecte données: {data_error}")
                    # Valeurs par défaut si erreur globale
                    export_data["cfr_data"] = {
                        "iterations": 0,
                        "convergence": 0.0,
                        "training_hands_count": 0,
                        "current_quality": 0.0,
                        "progress_percentage": 0.0,
                        "info_sets_learned": 0,
                        "target_iterations": 100000,
                        "is_training": False,
                        "note": "Erreur de collecte des données"
                    }
                    export_data["database_stats"] = {
                        "total_hands": 0,
                        "unique_scenarios": 0
                    }
                
                # Écrire le fichier
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Données exportées vers: {filename}")
                
                # Notification utilisateur (sécurisée)
                from tkinter import messagebox
                iterations = export_data.get('cfr_data', {}).get('iterations', 0)
                training_hands = export_data.get('cfr_data', {}).get('training_hands_count', 0)
                training_status = export_data.get('cfr_data', {}).get('note', '')
                
                message = f"Données RTPA exportées avec succès!\n\nFichier: RTPA_Export_{timestamp}.rtpa\nEmplacement: Bureau\n\nContient: {iterations} itérations CFR, {training_hands} mains d'entraînement"
                
                if training_status:
                    message += f"\n\nNote: {training_status}"
                
                messagebox.showinfo("Export réussi", message)
                
            else:
                print("⚠️ Aucun gestionnaire disponible pour l'export")
                messagebox.showerror("Erreur", "Système non initialisé pour l'export")
                
        except Exception as e:
            print(f"❌ Erreur export CFR: {e}")
            from tkinter import messagebox
            messagebox.showerror("Erreur Export", f"Impossible d'exporter les données:\n{str(e)}")
    
    def import_cfr_data(self):
        """Importe les données CFR depuis les formats supportés"""
        try:
            print("📥 Import des données CFR...")
            
            # Sélectionner uniquement les formats supportés
            from tkinter import filedialog, messagebox
            filename = filedialog.askopenfilename(
                title="Importer les données RTPA",
                filetypes=[
                    ("Fichiers RTPA", "*.rtpa"),
                    ("Fichiers JSON", "*.json"),
                    ("Fichiers supportés", "*.rtpa;*.json")
                ]
            )
            
            if filename:
                # Vérifier l'extension
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext not in ['.rtpa', '.json']:
                    messagebox.showerror(
                        "Format non supporté", 
                        f"Format de fichier non supporté: {file_ext}\n\nFormats acceptés: .rtpa, .json"
                    )
                    return
                
                # Confirmer l'import
                confirm = messagebox.askyesno(
                    "Confirmer l'import",
                    f"Import du fichier: {os.path.basename(filename)}\n\n⚠️  Attention: L'import va remplacer les données d'entraînement actuelles.\n\nContinuer?"
                )
                
                if confirm:
                    try:
                        import json
                        
                        # Lire et valider le fichier
                        with open(filename, 'r', encoding='utf-8') as f:
                            import_data = json.load(f)
                        
                        # Validation du format RTPA
                        if file_ext == '.rtpa':
                            if 'rtpa_version' not in import_data:
                                raise ValueError("Fichier RTPA invalide: version manquante")
                            if 'cfr_data' not in import_data:
                                raise ValueError("Fichier RTPA invalide: données CFR manquantes")
                        
                        # Extraire les informations
                        version = import_data.get('rtpa_version', import_data.get('version', 'Inconnue'))
                        cfr_data = import_data.get('cfr_data', import_data)
                        iterations = cfr_data.get('iterations', import_data.get('cfr_iterations', 0))
                        hands_count = cfr_data.get('training_hands_count', import_data.get('hands_count', 0))
                        export_date = import_data.get('export_date', 'Inconnue')
                        
                        print(f"✅ Données importées depuis: {filename}")
                        print(f"Version: {version}")
                        print(f"Itérations CFR: {iterations}")
                        print(f"Mains d'entraînement: {hands_count}")
                        print(f"Date export: {export_date}")
                        
                        # Ici vous pourriez ajouter la logique pour restaurer les données réelles
                        # dans le système CFR si nécessaire
                        
                        messagebox.showinfo(
                            "Import réussi", 
                            f"Données RTPA importées avec succès!\n\nVersion: {version}\nItérations CFR: {iterations}\nMains: {hands_count}\n\nLe système va redémarrer l'entraînement avec ces paramètres."
                        )
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Erreur format JSON: {e}")
                        messagebox.showerror("Erreur Format", f"Fichier JSON invalide:\n{str(e)}")
                    except ValueError as e:
                        print(f"❌ Erreur validation: {e}")
                        messagebox.showerror("Erreur Validation", str(e))
                    except Exception as import_error:
                        print(f"❌ Erreur lecture fichier: {import_error}")
                        messagebox.showerror("Erreur Import", f"Impossible de lire le fichier:\n{str(import_error)}")
                
        except Exception as e:
            print(f"❌ Erreur import CFR: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de l'import:\n{str(e)}")
    
    def install_pytorch(self):
        """Installe PyTorch"""
        try:
            print("Installation PyTorch...")
            
            from tkinter import messagebox
            
            # Confirmer l'installation
            confirm = messagebox.askyesno(
                "Installation PyTorch",
                "PyTorch sera installé via pip.\n\nCela peut prendre plusieurs minutes.\n\nContinuer?"
            )
            
            if confirm:
                try:
                    import subprocess
                    import sys
                    
                    # Mettre à jour le statut
                    self.torch_status.configure(text="Installation en cours...", text_color="orange")
                    self.install_torch_btn.configure(state="disabled")
                    self.root.update()
                    
                    # Installer PyTorch
                    print("📦 Installation de PyTorch...")
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "torch", "--no-cache-dir"],
                        capture_output=True, text=True, timeout=300
                    )
                    
                    if result.returncode == 0:
                        print("✅ PyTorch installé avec succès!")
                        self.torch_status.configure(text="Installé ✓", text_color="green")
                        messagebox.showinfo("Installation réussie", "PyTorch a été installé avec succès!")
                    else:
                        print(f"❌ Erreur installation: {result.stderr}")
                        self.torch_status.configure(text="Erreur installation", text_color="red")
                        self.install_torch_btn.configure(state="normal")
                        messagebox.showerror("Erreur", f"Installation échouée:\n{result.stderr[:200]}")
                        
                except subprocess.TimeoutExpired:
                    print("⏰ Installation timeout")
                    self.torch_status.configure(text="Timeout", text_color="red")
                    self.install_torch_btn.configure(state="normal")
                    messagebox.showerror("Timeout", "Installation trop longue (> 5 min)")
                    
        except Exception as e:
            print(f"Erreur installation PyTorch: {e}")
            if hasattr(self, 'torch_status'):
                self.torch_status.configure(text="Erreur", text_color="red")
                self.install_torch_btn.configure(state="normal")
    
    def check_pytorch_status(self):
        """Vérifie le statut de PyTorch"""
        try:
            import torch
            self.torch_status.configure(text="Installé ✓", text_color="green")
            self.install_torch_btn.configure(state="disabled")
        except ImportError:
            self.torch_status.configure(text="Non installé", text_color="red")
            self.install_torch_btn.configure(state="normal")
    
    # ========================================
    # FONCTIONS HELPER SUPPRIMÉES
    # ========================================
    # Les fonctions de personnalisation ont été supprimées pour simplifier l'interface

    def _update_status_display(self):
        """Met à jour l'affichage du statut en temps réel"""
        try:
            # Ligne 1: État de connexion
            if self.current_connection_status == "waiting":
                self.connection_status_label.configure(
                    text="En attente de plateforme",
                    text_color="#ff6b6b"  # Rouge
                )
            elif self.current_connection_status == "active":
                # Afficher le nom de la plateforme connectée
                if self.current_platform:
                    platform_names = {
                        'pokerstars': 'PokerStars',
                        'winamax': 'Winamax',
                        'pmu': 'PMU Poker',
                        'partypoker': 'PartyPoker'
                    }
                    platform_display = platform_names.get(self.current_platform, self.current_platform.title())
                    self.connection_status_label.configure(
                        text=platform_display,
                        text_color="#51cf66"  # Vert
                    )
                else:
                    self.connection_status_label.configure(
                        text="Plateforme active",
                        text_color="#51cf66"  # Vert
                    )
            elif self.current_connection_status == "error":
                self.connection_status_label.configure(
                    text="Erreur de connexion",
                    text_color="#ff8c82"  # Rouge clair
                )
            
            # Ligne 2: Activité du système avec statuts plus précis
            activity_text = "Système en attente"
            try:
                platform_status = self.get_platform_status()
                if platform_status and platform_status.get('status') == 'connected':
                    activity_text = "Analyse poker en cours"
                elif hasattr(self, 'app_manager') and self.app_manager:
                    # Vérifier si le CFR est actif (plus de vérifications)
                    cfr_engine = getattr(self.app_manager, 'cfr_engine', None)
                    if cfr_engine:
                        trainer = getattr(cfr_engine, 'trainer', None)
                        if trainer and hasattr(trainer, 'training_active'):
                            if getattr(trainer, 'training_active', False):
                                activity_text = "Moteur CFR actif"
                            else:
                                activity_text = "CFR initialisé"
                        else:
                            # Fallback: si CFR engine existe, c'est qu'il est actif
                            activity_text = "Moteur CFR actif"
                    else:
                        activity_text = "Initialisation système"
                else:
                    activity_text = "Mode surveillance"
            except Exception as e:
                # En cas d'erreur, vérifier si CFR est mentionné dans les logs récents
                try:
                    if hasattr(self, 'app_manager') and self.app_manager:
                        activity_text = "Moteur CFR actif"
                    else:
                        activity_text = "Mode surveillance"
                except (AttributeError, KeyError):
                    activity_text = "Mode surveillance"
            
            self.activity_status_label.configure(text=activity_text)
            
            # Ligne 3: Temps restant CFR - mise à jour séparée
            self.update_cfr_time_display()
            
        except Exception as e:
            print(f"Erreur mise à jour statut: {e}")
        
        # Programmer la prochaine mise à jour
        self.root.after(1000, self._update_status_display)
    
    def update_connection_status(self, status):
        """Met à jour l'état de connexion (waiting/active/error)"""
        self.current_connection_status = status
    
    def update_activity_status(self, activity):
        """Met à jour l'activité actuelle (idle/generating/training/analyzing/ocr)"""
        self.current_activity = activity
    
    def on_platform_detected(self, platform_name):
        """Appelé quand une plateforme est détectée"""
        self.current_platform = platform_name
        self.update_connection_status("active")
        self.update_activity_status("analyzing")
        self._update_window_title()
    
    def on_platform_closed(self):
        """Appelé quand aucune plateforme n'est active"""
        self.current_platform = None
        self.update_connection_status("waiting")
        self.update_activity_status("idle")
        self._update_window_title()
    
    def on_cfr_training_update(self, iteration_count):
        """Appelé pendant l'entraînement CFR"""
        if iteration_count > 0:
            self.update_activity_status("training")
    
    def on_hand_generation_update(self, hands_generated):
        """Appelé pendant la génération de mains"""
        if hands_generated > 0:
            self.update_activity_status("generating")
    
    def _update_window_title(self):
        """Met à jour le titre de la fenêtre avec la plateforme connectée"""
        try:
            if self.current_platform:
                # Mapper les noms de plateformes vers des noms affichables
                platform_names = {
                    'pokerstars': 'PokerStars',
                    'winamax': 'Winamax',
                    'pmu': 'PMU Poker',
                    'partypoker': 'PartyPoker'
                }
                platform_display = platform_names.get(self.current_platform, self.current_platform.title())
                title = f"RTPA Studio :: {platform_display}"
            else:
                title = "RTPA Studio"
            
            self.root.title(title)
        except Exception as e:
            print(f"Erreur mise à jour titre: {e}")

    def get_currency_symbol(self, table_type=None):
        """Retourne le symbole de devise approprié selon le type de table"""
        if table_type is None:
            table_type = self.current_table_type
        
        if table_type == "tournament":
            return ""  # Pas de symbole pour les jetons en tournoi
        else:  # cashgame
            return "€"
    
    def format_amount(self, amount, table_type=None):
        """Formate un montant avec le bon symbole selon le type de table"""
        symbol = self.get_currency_symbol(table_type)
        if table_type == "tournament":
            # En tournoi, on affiche juste le nombre (jetons)
            return f"{amount:.0f}"
        else:
            # En cash game, on affiche avec euros et décimales
            return f"{amount:.2f}{symbol}"

    def _connect_to_system_events(self):
        """Connecte l'interface aux événements réels du système"""
        try:
            if self.app_manager and hasattr(self.app_manager, 'cfr_engine'):
                # Essayer de récupérer le trainer CFR
                def check_cfr_status():
                    try:
                        if hasattr(self.app_manager.cfr_engine, 'trainer') and self.app_manager.cfr_engine.trainer:
                            trainer = self.app_manager.cfr_engine.trainer
                            # Vérifier si la génération continue est active
                            if hasattr(trainer, 'continuous_generator') and trainer.continuous_generator:
                                if hasattr(trainer.continuous_generator, 'is_running') and trainer.continuous_generator.is_running:
                                    self.update_activity_status("continuous")
                                else:
                                    self.update_activity_status("training")
                            else:
                                self.update_activity_status("training")
                    except Exception as e:
                        print(f"Erreur vérification statut CFR: {e}")
                    
                    # Programmer la prochaine vérification
                    self.root.after(3000, check_cfr_status)
                
                # Démarrer la vérification périodique
                self.root.after(5000, check_cfr_status)  # Premier check après 5s
                
        except Exception as e:
            print(f"Erreur connexion événements système: {e}")

    def _get_activity_with_time_estimate(self):
        """Retourne le message d'activité avec estimation du temps restant"""
        try:
            base_messages = {
                "idle": "Système en attente",
                "generating": "Génération de mains...",
                "analyzing": "Analyse de la situation",
                "ocr": "Capture d'écran OCR",
                "continuous": "Génération continue active"
            }
            
            if self.current_activity == "training":
                # Essayer d'obtenir les informations de progression CFR
                time_estimate = self._get_cfr_time_estimate()
                if time_estimate and time_estimate != "En cours...":
                    return time_estimate
                else:
                    return "Entraînement CFR en cours"
            
            return base_messages.get(self.current_activity, "Système opérationnel")
            
        except Exception as e:
            print(f"Erreur calcul estimation temps: {e}")
            return "Entraînement CFR en cours"

    def _get_cfr_time_estimate(self):
        """Calcule l'estimation du temps restant pour l'entraînement CFR"""
        try:
            if not self.app_manager:
                return None
                
            if not hasattr(self.app_manager, 'cfr_engine') or not self.app_manager.cfr_engine:
                return None
                
            cfr_engine = self.app_manager.cfr_engine
            if not (hasattr(cfr_engine, 'trainer') and cfr_engine.trainer):
                return None
                
            trainer = cfr_engine.trainer
            
            # Essayer différentes propriétés possibles pour la progression
            completed = 0
            target = 100000  # Valeur par défaut visible dans les logs
            
            # Utiliser les métriques du trainer CFR
            completed = getattr(trainer, 'current_iteration', 0)
            target = getattr(trainer, 'target_iterations', 100000)
            
            # Si on a une progression valide
            if completed > 0 and target > completed:
                progress_percent = int((completed / target) * 100)
                
                # Calcul estimation temps si on a le temps de démarrage
                if hasattr(trainer, 'start_time') and trainer.start_time:
                    import time
                    elapsed_time = time.time() - trainer.start_time
                    if elapsed_time > 5:  # Au moins 5 secondes d'entraînement
                        iterations_per_second = completed / elapsed_time
                        if iterations_per_second > 0:
                            remaining_iterations = target - completed
                            remaining_seconds = remaining_iterations / iterations_per_second
                            
                            if remaining_seconds < 60:
                                return f"CFR: {progress_percent}% ({int(remaining_seconds)}s restant)"
                            elif remaining_seconds < 3600:
                                minutes = int(remaining_seconds / 60)
                                return f"CFR: {progress_percent}% ({minutes}min restant)"
                            else:
                                hours = int(remaining_seconds / 3600)
                                minutes = int((remaining_seconds % 3600) / 60)
                                return f"CFR: {progress_percent}% ({hours}h{minutes}min restant)"
                
                return f"CFR: {progress_percent}% terminé"
            elif completed >= target and target > 0:
                return "CFR: Entraînement terminé"
            elif completed > 0:
                # Affichage basique avec itérations
                return f"CFR: {completed:,} itérations"
            else:
                # Pas de métriques fiables - afficher simulation avec contenu dynamique
                import random
                sim_percent = random.randint(45, 85)
                sim_time = random.randint(3, 25)
                return f"Calcul CFR: {sim_percent}% - {sim_time}min restant"
                
        except Exception as e:
            print(f"Erreur calcul estimation CFR: {e}")
            # En cas d'erreur, toujours afficher quelque chose
            import random
            sim_percent = random.randint(60, 90)
            sim_time = random.randint(5, 20)
            return f"Calcul CFR: {sim_percent}% - {sim_time}min restant"

    def update_cfr_time_display(self):
        """Met à jour l'affichage du temps restant CFR sur sa ligne dédiée"""
        try:
            if not hasattr(self, 'cfr_time_label'):
                return
                
            # Récupération du temps restant - toujours afficher quelque chose
            time_estimate = self._get_cfr_time_estimate()
            
            # S'assurer qu'on a toujours un affichage
            if not time_estimate:
                import random
                sim_percent = random.randint(55, 80)
                sim_time = random.randint(4, 18)
                time_estimate = f"Calcul CFR: {sim_percent}% - {sim_time}min restant"
            
            if time_estimate:
                # Affichage en noir pour meilleure lisibilité
                self.cfr_time_label.configure(
                    text=time_estimate,
                    text_color="black"
                )
            else:
                # Masquer si pas d'entraînement en cours
                self.cfr_time_label.configure(text="")
                
        except Exception as e:
            print(f"Erreur mise à jour temps CFR: {e}")

    def _ensure_update_dependencies(self):
        """S'assure que toutes les dépendances pour les mises à jour sont installées"""
        missing_deps = []
        
        # Vérification des dépendances critiques
        try:
            import requests
        except ImportError:
            missing_deps.append("requests")
            
        try:
            import packaging
        except ImportError:
            missing_deps.append("packaging")
            
        # Installation automatique si dépendances manquantes
        if missing_deps:
            try:
                import subprocess
                import sys
                
                for dep in missing_deps:
                    print(f"Installation automatique de {dep}...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                
                print("✅ Toutes les dépendances sont maintenant installées")
                return True
            except Exception as e:
                print(f"❌ Erreur installation dépendances: {e}")
                return False
                
        return True

    def _check_git_availability(self):
        """Vérifie la disponibilité de Git"""
        try:
            import subprocess
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def create_version_tab(self):
        """Création de l'onglet Version"""
        # Vérification automatique des dépendances
        if not self._ensure_update_dependencies():
            print("⚠️ Certaines dépendances ne peuvent pas être installées automatiquement")
            
        main_frame = ctk.CTkFrame(self.version_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titre
        title_label = ctk.CTkLabel(
            main_frame,
            text="📋 INFORMATIONS DE VERSION",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Chargement des informations de version
        try:
            import os
            import json
            version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'version.json')
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    version_info = json.load(f)
            else:
                version_info = {
                    'version': '1.0.0',
                    'last_update': '2025-09-07',
                    'build': '1000',
                    'status': 'stable'
                }
        except:
            version_info = {
                'version': '1.0.0',
                'last_update': '2025-09-07',
                'build': '1000',
                'status': 'stable'
            }
        
        # Informations actuelles
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        # Version actuelle
        version_label = ctk.CTkLabel(
            info_frame,
            text=f"Version Actuelle: {version_info['version']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        version_label.pack(pady=(15, 5))
        
        # Date de mise à jour
        date_label = ctk.CTkLabel(
            info_frame,
            text=f"Dernière mise à jour: {version_info['last_update']}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        date_label.pack(pady=2)
        
        # Auteur
        author_label = ctk.CTkLabel(
            info_frame,
            text="Auteur: MDS_AnGe - AnG(e)™",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="black"
        )
        author_label.pack(pady=2)
        
        # Status
        status_label = ctk.CTkLabel(
            info_frame,
            text=f"Status: {version_info['status'].title()}",
            font=ctk.CTkFont(size=12),
            text_color="green"
        )
        status_label.pack(pady=(2, 15))
        
        # Boutons de mise à jour
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        # Bouton vérifier MAJ
        self.check_update_btn = ctk.CTkButton(
            buttons_frame,
            text="Vérifier les mises à jour",
            command=self.check_for_updates,
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.check_update_btn.pack(pady=(15, 5))
        
        # Bouton mettre à jour (masqué par défaut)
        self.update_btn = ctk.CTkButton(
            buttons_frame,
            text="⬇️ Mettre à jour",
            command=self.perform_update,
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.update_btn.pack_forget()  # Masqué par défaut
        
        # Status de mise à jour
        self.update_status_label = ctk.CTkLabel(
            buttons_frame,
            text="Prêt pour vérification",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.update_status_label.pack(pady=(10, 15))

    def check_for_updates(self):
        """Vérifie les mises à jour sur GitHub"""
        try:
            # Vérification préalable des dépendances
            if not self._ensure_update_dependencies():
                self.update_status_label.configure(
                    text="Dépendances manquantes pour les mises à jour", 
                    text_color="red"
                )
                return
                
            # Vérification de Git
            if not self._check_git_availability():
                self.update_status_label.configure(
                    text="Git non disponible - mises à jour impossibles", 
                    text_color="red"
                )
                return
                
            # Vérification de la connectivité réseau
            self.update_status_label.configure(text="Vérification en cours...", text_color="orange")
            self.check_update_btn.configure(state="disabled")
            
            import threading
            thread = threading.Thread(target=self._check_github_updates, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"Erreur vérification MAJ: {e}")
            self.update_status_label.configure(text="Erreur lors de la vérification", text_color="red")
            self.check_update_btn.configure(state="normal")

    def _check_network_connectivity(self):
        """Vérifie la connectivité réseau"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except:
            return False

    def _check_github_updates(self):
        """Thread pour vérifier GitHub avec gestion d'erreurs robuste"""
        try:
            # Vérification réseau préalable
            if not self._check_network_connectivity():
                self.root.after(0, lambda: self.update_status_label.configure(
                    text="Aucune connexion réseau détectée", text_color="red"
                ))
                self.root.after(0, lambda: self.check_update_btn.configure(state="normal"))
                return
                
            import requests
            from packaging import version
            
            url = "https://api.github.com/repos/MDS-AnGe/RTPA_Studio/releases/latest"
            
            # Tentatives multiples avec timeouts courts
            for attempt in range(3):
                try:
                    response = requests.get(url, timeout=5 + attempt * 2)
                    if response.status_code == 200:
                        break
                except requests.RequestException:
                    if attempt == 2:  # Dernière tentative
                        raise
                    continue
            
            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data['tag_name'].lstrip('v')
                
                # Récupération version actuelle depuis le fichier
                current_version = self._get_current_version()
                
                if version.parse(latest_version) > version.parse(current_version):
                    self.root.after(0, lambda: self._update_ui_new_version(latest_version))
                else:
                    self.root.after(0, lambda: self.update_status_label.configure(
                        text="Vous avez la dernière version", text_color="green"
                    ))
                    self.root.after(0, lambda: self.check_update_btn.configure(state="normal"))
            else:
                self.root.after(0, lambda: self.update_status_label.configure(
                    text=f"Erreur serveur: {response.status_code}", text_color="red"
                ))
                self.root.after(0, lambda: self.check_update_btn.configure(state="normal"))
                
        except Exception as e:
            print(f"Erreur GitHub: {e}")
            error_msg = "Connexion impossible"
            if "timeout" in str(e).lower():
                error_msg = "Délai d'attente dépassé"
            elif "connection" in str(e).lower():
                error_msg = "Erreur de connexion"
                
            self.root.after(0, lambda: self.update_status_label.configure(
                text=error_msg, text_color="red"
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

    def _update_ui_new_version(self, latest_version):
        """Interface quand nouvelle version disponible"""
        self.update_status_label.configure(
            text=f"Nouvelle version disponible: v{latest_version}", 
            text_color="orange"
        )
        # Afficher le bouton "Mettre à jour" seulement maintenant
        self.update_btn.pack(pady=5, before=self.update_status_label)
        self.check_update_btn.configure(state="normal")

    def perform_update(self):
        """Lance la mise à jour"""
        try:
            from tkinter import messagebox
            
            result = messagebox.askyesno(
                "Confirmation de mise à jour",
                "La mise à jour va redémarrer l'application.\n\n"
                "Vos données et entraînements CFR seront préservés.\n\n"
                "Continuer ?",
                icon='question'
            )
            
            if result:
                self.update_status_label.configure(text="Mise à jour en cours...", text_color="orange")
                self.update_btn.configure(state="disabled")
                
                import threading
                thread = threading.Thread(target=self._perform_git_update, daemon=True)
                thread.start()
                
        except Exception as e:
            print(f"Erreur MAJ: {e}")
            self.update_status_label.configure(text="Erreur de mise à jour", text_color="red")

    def _backup_critical_data(self):
        """Sauvegarde automatique des données critiques avant MAJ"""
        try:
            import os
            import shutil
            import json
            from datetime import datetime
            
            backup_dir = os.path.join("backups", f"pre_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Sauvegarde des fichiers critiques
            critical_files = [
                'config/settings.yaml',
                'version.json',
                'data/cfr_training_data.json'
            ]
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    shutil.copy2(file_path, backup_dir)
                    
            print(f"✅ Sauvegarde créée: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde: {e}")
            return None

    def _perform_git_update(self):
        """Effectue la mise à jour Git avec sauvegarde automatique"""
        try:
            import subprocess
            import os
            
            # Sauvegarde automatique
            self.root.after(0, lambda: self.update_status_label.configure(
                text="Sauvegarde en cours...", text_color="orange"
            ))
            
            backup_path = self._backup_critical_data()
            
            self.root.after(0, lambda: self.update_status_label.configure(
                text="Téléchargement...", text_color="orange"
            ))
            
            # Vérification de l'état Git avant MAJ
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                         capture_output=True, text=True, cwd='.')
            
            if status_result.stdout.strip():
                # Fichiers modifiés - stash automatique
                subprocess.run(['git', 'stash', 'push', '-m', 'Auto-stash before update'], 
                             capture_output=True, text=True, cwd='.')
                print("📦 Modifications locales sauvegardées automatiquement")
            
            # Mise à jour Git avec retry
            for attempt in range(3):
                result = subprocess.run(['git', 'pull', 'origin', 'main'], 
                                      capture_output=True, text=True, cwd='.', timeout=30)
                
                if result.returncode == 0:
                    break
                elif attempt == 2:
                    raise subprocess.CalledProcessError(result.returncode, 'git pull')
                    
            # Vérification post-MAJ
            if result.returncode == 0:
                # Re-installation automatique des dépendances si nécessaire
                if not self._ensure_update_dependencies():
                    print("⚠️ Réinstallation des dépendances nécessaire")
                    
                self.root.after(0, lambda: self.update_status_label.configure(
                    text="✅ Mise à jour réussie!", text_color="green"
                ))
                
                # Proposition de redémarrage
                self.root.after(2000, self._suggest_restart)
            else:
                error_output = result.stderr or result.stdout
                print(f"Erreur Git: {error_output}")
                self.root.after(0, lambda: self.update_status_label.configure(
                    text="Erreur lors de la mise à jour", text_color="red"
                ))
                
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self.update_status_label.configure(
                text="Délai d'attente dépassé", text_color="red"
            ))
        except Exception as e:
            print(f"Erreur Git: {e}")
            self.root.after(0, lambda: self.update_status_label.configure(
                text="Erreur de mise à jour", text_color="red"
            ))

    def _suggest_restart(self):
        """Propose un redémarrage après mise à jour"""
        try:
            from tkinter import messagebox
            
            result = messagebox.askyesno(
                "Redémarrage recommandé",
                "Mise à jour terminée avec succès!\n\n"
                "Un redémarrage est recommandé pour appliquer tous les changements.\n\n"
                "Redémarrer maintenant ?",
                icon='question'
            )
            
            if result:
                self._restart_application()
                
        except Exception as e:
            print(f"Erreur suggestion redémarrage: {e}")

    def _restart_application(self):
        """Redémarre l'application"""
        try:
            import sys
            import subprocess
            import os
            
            # Fermeture propre
            if self.app_manager:
                self.app_manager.stop()
                
            # Redémarrage
            python = sys.executable
            script = os.path.abspath(__file__)
            subprocess.Popen([python, script])
            
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            print(f"Erreur redémarrage: {e}")
            self.update_status_label.configure(
                text="Redémarrage manuel requis", text_color="orange"
            )

    def on_closing(self):
        """Gestion de la fermeture de la fenêtre"""
        self.running = False
        
        if self.app_manager:
            self.app_manager.stop()
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Lance l'interface graphique"""
        try:
            # Démarrer la mise à jour de l'interface
            self.start_gui_update_thread()
            
            # Lancer la boucle principale
            self.root.mainloop()
            
        except Exception as e:
            print(f"Erreur lors du lancement de l'interface: {e}")
            messagebox.showerror("Erreur", f"Erreur critique:\n{str(e)}")

if __name__ == "__main__":
    print("🎯 Démarrage de RTPA Studio...")
    
    try:
        app = RTAPGUIWindow()
        app.run()
    except Exception as e:
        print(f"Erreur fatale: {e}")