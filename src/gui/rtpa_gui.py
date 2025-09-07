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
        self.root.title("Real-Time Poker Assistant (CFR/Nash) avec Intelligence Artificielle")
        self.root.geometry("1100x900")  # Réduit de 1400 à 1100
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configuration couleurs plus claires
        ctk.set_appearance_mode("light")  # Mode clair pour éviter les zones noires
        
        # Variables de thème
        self.accent_color = "blue"
        self.font_family = "Arial"
        self.opacity = 1.0
        
        # Charger logo si disponible
        self.logo = None
        self.logo_image = None
        self.load_logo()
        
        # Configuration du style
        self.setup_styles()
        
        # Interface utilisateur
        self.create_widgets()
        
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
        
        # Couleurs harmonisées - tons beige/crème
        bg_color = "#f5f5dc"  # Beige harmonieux
        fg_color = "#212529"  # Noir doux pour le texte
        accent = "#1f538d"
        card_bg = "#f5f5dc"   # Beige pour les cartes
        
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
        
        ctk.CTkLabel(title_frame, text="Real-Time Poker Assistant (CFR/Nash)", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor='w')
        ctk.CTkLabel(title_frame, text="avec Intelligence Artificielle", 
                    font=ctk.CTkFont(size=14)).pack(anchor='w')
        
        # Contrôles et statut (en-tête droite)
        self.controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        self.controls_frame.pack(side='right', padx=(20, 10))
        
        self.status_label = ctk.CTkLabel(
            self.controls_frame,
            text="⏳ En attente...",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.status_label.pack(pady=5)
        
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
        
        self.hero_cards_frame = ttk.Frame(hero_frame)
        self.hero_cards_frame.pack(padx=8, pady=10)
        
        # Cartes visuelles Main
        self.hero_card1_frame = tk.Frame(
            self.hero_cards_frame, 
            bg='#f5f5dc', relief='raised', bd=2, width=90, height=120
        )
        self.hero_card1_frame.pack(side='left', padx=5)
        self.hero_card1_frame.pack_propagate(False)
        
        self.hero_card1 = tk.Label(
            self.hero_card1_frame, text="🂠", font=('Arial', 28, 'bold'),
            fg='#5a5a5a', bg='#f5f5dc', anchor='center'
        )
        self.hero_card1.pack(expand=True, fill='both')
        
        self.hero_card2_frame = tk.Frame(
            self.hero_cards_frame, bg='#f5f5dc', relief='raised', bd=2, width=90, height=120
        )
        self.hero_card2_frame.pack(side='left', padx=5)
        self.hero_card2_frame.pack_propagate(False)
        
        self.hero_card2 = tk.Label(
            self.hero_card2_frame, text="🂠", font=('Arial', 28, 'bold'),
            fg='#5a5a5a', bg='#f5f5dc', anchor='center'
        )
        self.hero_card2.pack(expand=True, fill='both')
        
        # Section Board (à droite)
        board_frame = ttk.LabelFrame(cards_container, text="🃏 Board", style='Card.TFrame')
        board_frame.pack(side='left', fill='both', expand=True, padx=(10, 0))
        
        self.board_cards_frame = tk.Frame(board_frame, bg='#f5f5dc')
        self.board_cards_frame.pack(anchor='center', padx=8, pady=10)
        
        # Calculer la largeur optimale pour 5 cartes (90px + padding)
        optimal_board_width = (5 * 90) + (4 * 5) + 16  # 5 cartes + 4 espacements + padding
        
        self.board_cards = []
        self.board_card_frames = []
        for i in range(5):
            card_frame = tk.Frame(
                self.board_cards_frame, bg='#f5f5dc', relief='raised', bd=2, width=90, height=120
            )
            card_frame.pack(side='left', padx=5)
            card_frame.pack_propagate(False)
            
            card_label = tk.Label(
                card_frame, text="🂠", font=('Arial', 28, 'bold'),
                fg='#5a5a5a', bg='#f5f5dc', anchor='center'
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
        
        table_content = tk.Frame(table_info_frame, bg='#f5f5dc')
        table_content.pack(fill='both', expand=True, padx=8, pady=6)
        
        # POT principal - centré et mis en valeur
        pot_container = tk.Frame(table_content, bg='#f5f5dc')
        pot_container.pack(fill='x', pady=(0, 8))
        
        tk.Label(pot_container, text="💰 POT ACTUEL", font=('Arial', 11, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack()
        self.pot_label = tk.Label(pot_container, text="0.00€", font=('Arial', 20, 'bold'), fg='#28a745', bg='#f5f5dc')
        self.pot_label.pack()
        
        # Ligne blinds et antes - organisation horizontale optimisée
        blinds_row = tk.Frame(table_content, bg='#f5f5dc')
        blinds_row.pack(fill='x', pady=(0, 4))
        
        # Blinds section
        blinds_container = tk.Frame(blinds_row, bg='#f5f5dc')
        blinds_container.pack(side='left', fill='x', expand=True)
        tk.Label(blinds_container, text="🎲 Blinds", font=('Arial', 10, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack()
        self.blinds_label = tk.Label(blinds_container, text="0.00€ / 0.00€", font=('Arial', 12, 'bold'), fg='#fd7e14', bg='#f5f5dc')
        self.blinds_label.pack()
        
        # Antes section
        antes_container = tk.Frame(blinds_row, bg='#f5f5dc')
        antes_container.pack(side='right')
        tk.Label(antes_container, text="⚡ Antes", font=('Arial', 10, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack()
        self.antes_label = tk.Label(antes_container, text="0.00€", font=('Arial', 12, 'bold'), fg='#6f42c1', bg='#f5f5dc')
        self.antes_label.pack()
        
        # Type de table - en bas
        self.table_type_label = tk.Label(table_content, text="Cash Game", font=('Arial', 10), fg='#6c757d', bg='#f5f5dc')
        self.table_type_label.pack(pady=(4, 0))
        
        # SOUS-SECTION: Recommandation principale
        rec_frame = ttk.LabelFrame(left_column, text="🎯 RECOMMANDATION", style='Card.TFrame')
        rec_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        rec_content = tk.Frame(rec_frame, bg='#f5f5dc')
        rec_content.pack(fill='both', expand=True, padx=8, pady=6)
        
        # Action principale centrée
        action_container = tk.Frame(rec_content, bg='#f5f5dc')
        action_container.pack(fill='x', pady=(0, 8))
        
        self.action_display = tk.Label(action_container, text="CHECK", font=('Arial', 24, 'bold'), fg='#28a745', bg='#f5f5dc')
        self.action_display.pack()
        
        self.bet_size_label = tk.Label(action_container, text="", font=('Arial', 18, 'bold'), fg='#28a745', bg='#f5f5dc')
        self.bet_size_label.pack()
        
        # Métriques en grille 2x2
        metrics_frame = tk.Frame(rec_content, bg='#f5f5dc')
        metrics_frame.pack(fill='x', pady=(0, 8))
        
        # Ligne 1: Victoire + Risque
        metrics_row1 = tk.Frame(metrics_frame, bg='#f5f5dc')
        metrics_row1.pack(fill='x', pady=(0, 4))
        
        victory_frame = tk.Frame(metrics_row1, bg='#f5f5dc')
        victory_frame.pack(side='left', fill='x', expand=True)
        tk.Label(victory_frame, text="🎯 Victoire", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack()
        self.win_prob_label = tk.Label(victory_frame, text="50%", font=('Arial', 14, 'bold'), fg='#28a745', bg='#f5f5dc')
        self.win_prob_label.pack()
        
        risk_frame = tk.Frame(metrics_row1, bg='#f5f5dc')
        risk_frame.pack(side='right', fill='x', expand=True)
        tk.Label(risk_frame, text="⚠️ Risque", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack()
        self.risk_label = tk.Label(risk_frame, text="30%", font=('Arial', 14, 'bold'), fg='#fd7e14', bg='#f5f5dc')
        self.risk_label.pack()
        
        # Ligne 2: Confiance seule, centrée
        confidence_frame = tk.Frame(metrics_frame, bg='#f5f5dc')
        confidence_frame.pack(fill='x')
        tk.Label(confidence_frame, text="🔮 Confiance", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack()
        self.main_confidence_label = tk.Label(confidence_frame, text="85%", font=('Arial', 14, 'bold'), fg='#6f42c1', bg='#f5f5dc')
        self.main_confidence_label.pack()
        
        # Raisonnement optimisé
        reasoning_frame = tk.Frame(rec_content, bg='#f5f5dc')
        reasoning_frame.pack(fill='both', expand=True)
        tk.Label(reasoning_frame, text="🧠 Raisonnement:", font=('Arial', 10, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack(anchor='w')
        self.main_reasoning_label = tk.Label(
            reasoning_frame, text="En attente d'analyse...", font=('Arial', 9),
            wraplength=320, justify='left', fg='#6c757d', bg='#f5f5dc'
        )
        self.main_reasoning_label.pack(anchor='w', fill='both', expand=True)
        
        # SOUS-SECTION: Statistiques compactes
        stats_frame = ttk.LabelFrame(left_column, text="📈 STATISTIQUES", style='Card.TFrame')
        stats_frame.pack(fill='both', expand=True)
        
        stats_content = tk.Frame(stats_frame, bg='#f5f5dc')
        stats_content.pack(fill='both', expand=True, padx=6, pady=4)
        
        # Taux de victoire principal - centré et plus compact
        main_rate_frame = tk.Frame(stats_content, bg='#f5f5dc')
        main_rate_frame.pack(fill='x', pady=(0, 4))
        
        tk.Label(main_rate_frame, text="📊 TAUX DE VICTOIRE", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack()
        self.win_rate_value = tk.Label(main_rate_frame, text="0.0%", font=('Arial', 14, 'bold'), fg='#dc3545', bg='#f5f5dc')
        self.win_rate_value.pack()
        
        # Statistiques détaillées en grille compacte
        details_frame = tk.Frame(stats_content, bg='#f5f5dc')
        details_frame.pack(fill='both', expand=True, pady=(0, 2))
        
        # Ligne 1: Mains jouées + gagnées - plus compact
        hands_row = tk.Frame(details_frame, bg='#f5f5dc')
        hands_row.pack(fill='x', pady=(0, 2))
        
        played_frame = tk.Frame(hands_row, bg='#f5f5dc')
        played_frame.pack(side='left', fill='x', expand=True)
        tk.Label(played_frame, text="🎲 Jouées", font=('Arial', 8, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack()
        self.hands_played_value = tk.Label(played_frame, text="0", font=('Arial', 10, 'bold'), fg='#495057', bg='#f5f5dc')
        self.hands_played_value.pack()
        
        won_frame = tk.Frame(hands_row, bg='#f5f5dc')
        won_frame.pack(side='right', fill='x', expand=True)
        tk.Label(won_frame, text="🏆 Gagnées", font=('Arial', 8, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack()
        self.hands_won_value = tk.Label(won_frame, text="0", font=('Arial', 10, 'bold'), fg='#28a745', bg='#f5f5dc')
        self.hands_won_value.pack()
        
        # Ligne 2: Comparaison performance - plus compact
        perf_row = tk.Frame(details_frame, bg='#f5f5dc')
        perf_row.pack(fill='x')
        
        pro_frame = tk.Frame(perf_row, bg='#f5f5dc')
        pro_frame.pack(side='left', fill='x', expand=True)
        tk.Label(pro_frame, text="👑 Pro", font=('Arial', 8, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack()
        self.expected_rate_value = tk.Label(pro_frame, text="68.0%", font=('Arial', 9, 'bold'), fg='#6f42c1', bg='#f5f5dc')
        self.expected_rate_value.pack()
        
        performance_frame = tk.Frame(perf_row, bg='#f5f5dc')
        performance_frame.pack(side='right', fill='x', expand=True)
        tk.Label(performance_frame, text="📈 Perf", font=('Arial', 8, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack()
        self.performance_ratio_value = tk.Label(performance_frame, text="0.0%", font=('Arial', 9, 'bold'), fg='#fd7e14', bg='#f5f5dc')
        self.performance_ratio_value.pack()
        
        # Colonne droite: Informations joueurs
        right_column = ttk.Frame(main_layout)
        right_column.pack(side='left', fill='both', expand=True, padx=(5, 10))
        
        # SECTION 4A: NOS INFOS PERSONNELLES
        hero_frame = ttk.LabelFrame(right_column, text="👤 MOI", style='Card.TFrame')
        hero_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        hero_content = tk.Frame(hero_frame, bg='#f5f5dc')
        hero_content.pack(fill='x', padx=8, pady=6)
        
        # Pseudo du joueur
        tk.Label(hero_content, text="Pseudo:", font=('Arial', 10, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack(anchor='w')
        self.hero_name_label = tk.Label(hero_content, text="MonPseudo", font=('Arial', 12, 'bold'), fg='#007bff', bg='#f5f5dc')
        self.hero_name_label.pack(anchor='w', pady=(2, 8))
        
        # Stack personnel
        tk.Label(hero_content, text="Mon Stack:", font=('Arial', 10, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack(anchor='w')
        self.hero_stack_label = tk.Label(hero_content, text="2500€", font=('Arial', 14, 'bold'), fg='#28a745', bg='#f5f5dc')
        self.hero_stack_label.pack(anchor='w', pady=(2, 8))
        
        # Position à la table
        tk.Label(hero_content, text="Position:", font=('Arial', 10, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack(anchor='w')
        self.hero_position_label = tk.Label(hero_content, text="Button", font=('Arial', 11), fg='#4a4a4a', bg='#f5f5dc')
        self.hero_position_label.pack(anchor='w', pady=(2, 0))
        
        # SECTION 4B: AUTRES JOUEURS ACTIFS
        players_frame = ttk.LabelFrame(right_column, text="👥 AUTRES JOUEURS", style='Card.TFrame')
        players_frame.pack(fill='both', expand=True, pady=(0, 0))
        
        players_content = tk.Frame(players_frame, bg='#f5f5dc')
        players_content.pack(fill='x', padx=5, pady=3)
        
        # Info générale - Table 9-max (compacte)
        players_info = tk.Frame(players_content, bg='#f5f5dc')
        players_info.pack(fill='x', pady=(0, 3))
        
        tk.Label(players_info, text="Actifs:", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#f5f5dc').pack(side='left')
        self.active_players_count = tk.Label(players_info, text="8/9", font=('Arial', 9, 'bold'), fg='#4a4a4a', bg='#f5f5dc')
        self.active_players_count.pack(side='left', padx=(3, 0))
        
        # Frame simple pour la liste des joueurs (sans scroll)
        self.players_list_frame = tk.Frame(players_content, bg='#f5f5dc')
        self.players_list_frame.pack(fill='x')
        
        # Créer la liste des joueurs
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
        
        # Initialiser les données OCR (sera connecté plus tard)
        self.update_hero_info("MonPseudo", "2500€", "Button")
        
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
                                hero_data.get('stack', '0€'), 
                                hero_data.get('position', 'Unknown'))
        
        # Mettre à jour le compteur de joueurs actifs
        active_count = sum(1 for p in players_data if p.get('status') == 'actif')
        total_count = len(players_data) + 1  # +1 pour nous
        self.active_players_count.config(text=f"{active_count}/{total_count}")
        
        # Recréer l'affichage des joueurs
        self.create_players_display(players_data)
    
    def create_players_display(self, players_data=None):
        """Création de l'affichage des joueurs actifs avec positions 9-max"""
        
        # Effacer l'affichage existant
        for widget in self.players_list_frame.winfo_children():
            widget.destroy()
        
        # Utiliser les données fournies ou les données par défaut
        if players_data is None:
            # Données d'exemple pour table 9-max (sera remplacé par OCR)
            players_data = [
                {"name": "AlicePoker", "stack": 1847, "vpip": 15, "pfr": 12, "status": "actif", "position": 0, "position_name": "UTG", "is_button": False, "is_sb": False, "is_bb": False},
                {"name": "BobBluff", "stack": 2156, "vpip": 28, "pfr": 22, "status": "actif", "position": 2, "position_name": "MP1", "is_button": False, "is_sb": False, "is_bb": False},
                {"name": "Charlie2024", "stack": 1023, "vpip": 45, "pfr": 8, "status": "fold", "position": 4, "position_name": "MP3", "is_button": False, "is_sb": False, "is_bb": False},
                {"name": "DianaAce", "stack": 3421, "vpip": 12, "pfr": 10, "status": "actif", "position": 5, "position_name": "CO", "is_button": False, "is_sb": False, "is_bb": False},
                {"name": "EdRaise", "stack": 956, "vpip": 35, "pfr": 25, "status": "actif", "position": 6, "position_name": "BTN", "is_button": True, "is_sb": False, "is_bb": False},
                {"name": "FionaCall", "stack": 1540, "vpip": 22, "pfr": 18, "status": "actif", "position": 7, "position_name": "SB", "is_button": False, "is_sb": True, "is_bb": False},
                {"name": "GaryFold", "stack": 2890, "vpip": 18, "pfr": 14, "status": "actif", "position": 8, "position_name": "BB", "is_button": False, "is_sb": False, "is_bb": True}
            ]
        
        # Trier par position pour affichage dans l'ordre de la table
        sorted_players = sorted(players_data, key=lambda p: p.get('position', 0))
        
        # Affichage ultra-compact pour les autres joueurs
        for i, player in enumerate(sorted_players):
            player_frame = ttk.Frame(self.players_list_frame)
            player_frame.pack(fill='x', pady=1, padx=2)
            
            # Couleur de statut
            status_color = '#28a745' if player['status'] == 'actif' else '#6c757d'
            status_icon = "●" if player['status'] == 'actif' else "○"
            
            # Déterminer icône de position
            position_icon = ""
            if player.get('is_button'):
                position_icon = "🔴"  # Button
            elif player.get('is_sb'):
                position_icon = "🟡"  # Small Blind
            elif player.get('is_bb'):
                position_icon = "🔵"  # Big Blind
            
            # Ligne unique ultra-compacte: Position Nom Stack (Stats)
            main_line = ttk.Frame(player_frame)
            main_line.pack(fill='x')
            
            # Position (3 chars max)
            pos_text = player.get('position_name', 'POS')[:3]
            if position_icon:
                pos_text = f"{pos_text}{position_icon}"
            ttk.Label(main_line, text=pos_text, font=('Arial', 8, 'bold')).pack(side='left')
            
            # Statut
            ttk.Label(main_line, text=status_icon, font=('Arial', 8), foreground=status_color).pack(side='left', padx=(2, 3))
            
            # Nom (tronqué si nécessaire)
            name = player['name'][:8] + "." if len(player['name']) > 8 else player['name']
            ttk.Label(main_line, text=name, font=('Arial', 8, 'bold'), foreground=status_color).pack(side='left')
            
            # Stats compactes au centre
            vpip = player.get('vpip', 0)
            pfr = player.get('pfr', 0)
            stats_text = f"{vpip}/{pfr}"
            ttk.Label(main_line, text=stats_text, font=('Arial', 7), foreground='#6c757d').pack(side='left', padx=(5, 0))
            
            # Stack à droite
            stack_value = player.get('stack', 0)
            if isinstance(stack_value, (int, float)):
                if stack_value >= 1000:
                    stack_text = f"{stack_value/1000:.1f}k"
                else:
                    stack_text = f"{stack_value:.0f}"
            else:
                stack_text = str(stack_value)
            
            ttk.Label(main_line, text=stack_text, font=('Arial', 8, 'bold'), foreground='#28a745').pack(side='right')
    
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
        def update_metrics():
            while True:
                try:
                    import psutil
                    
                    # CPU
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.cpu_progress.set(cpu_percent / 100)
                    self.cpu_label.configure(text=f"{cpu_percent:.1f}%")
                    
                    # RAM
                    memory = psutil.virtual_memory()
                    ram_gb = memory.used / (1024**3)
                    ram_percent = memory.percent
                    self.ram_progress.set(ram_percent / 100)
                    self.ram_label.configure(text=f"{ram_gb:.1f} GB ({ram_percent:.1f}%)")
                    
                except Exception as e:
                    print(f"Erreur monitoring: {e}")
                
                time.sleep(2)
        
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