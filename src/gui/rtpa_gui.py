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
        self.root.title("🎯 RTPA Studio - Analyse Poker Temps Réel")
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
        self.load_logo()
        
        # Configuration du style
        self.setup_styles()
        
        # Interface utilisateur
        self.create_widgets()
        
        # Démarrage auto-détection (si disponible)
        if self.app_manager and hasattr(self.app_manager, 'start_platform_detection'):
            self.app_manager.start_platform_detection()
        
    def load_logo(self):
        """Charge le logo RTPA Studio si disponible"""
        logo_path = "attached_assets/rtpa_logo.png"
        if os.path.exists(logo_path):
            try:
                from PIL import Image
                self.logo_image = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(64, 64)
                )
                self.logo = True
            except Exception:
                self.logo = None
    
    def setup_styles(self):
        """Configuration des styles CustomTkinter"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Couleurs harmonisées - tons gris doux
        bg_color = "#e9ecef"  # Gris très clair harmonieux
        fg_color = "#212529"  # Noir doux pour le texte
        accent = "#1f538d"
        card_bg = "#f8f9fa"   # Gris très clair pour les cartes
        
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
        
        ctk.CTkLabel(title_frame, text="🎯 RTPA Studio", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor='w')
        ctk.CTkLabel(title_frame, text="Analyse Poker Temps Réel avec Intelligence Artificielle", 
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
            bg='#f8f9fa', relief='raised', bd=2, width=90, height=120
        )
        self.hero_card1_frame.pack(side='left', padx=5)
        self.hero_card1_frame.pack_propagate(False)
        
        self.hero_card1 = tk.Label(
            self.hero_card1_frame, text="🂠", font=('Arial', 28, 'bold'),
            fg='gray', bg='#f8f9fa', anchor='center'
        )
        self.hero_card1.pack(expand=True, fill='both')
        
        self.hero_card2_frame = tk.Frame(
            self.hero_cards_frame, bg='#f8f9fa', relief='raised', bd=2, width=90, height=120
        )
        self.hero_card2_frame.pack(side='left', padx=5)
        self.hero_card2_frame.pack_propagate(False)
        
        self.hero_card2 = tk.Label(
            self.hero_card2_frame, text="🂠", font=('Arial', 28, 'bold'),
            fg='gray', bg='#f8f9fa', anchor='center'
        )
        self.hero_card2.pack(expand=True, fill='both')
        
        # Section Board (à droite)
        board_frame = ttk.LabelFrame(cards_container, text="🃏 Board", style='Card.TFrame')
        board_frame.pack(side='left', fill='both', expand=True, padx=(10, 0))
        
        self.board_cards_frame = ttk.Frame(board_frame)
        self.board_cards_frame.pack(anchor='w', padx=8, pady=10)
        
        # Calculer la largeur optimale pour 5 cartes (70px + padding)
        optimal_board_width = (5 * 70) + (4 * 6) + 16  # 5 cartes + 4 espacements + padding
        
        self.board_cards = []
        self.board_card_frames = []
        for i in range(5):
            card_frame = tk.Frame(
                self.board_cards_frame, bg='#f8f9fa', relief='raised', bd=2, width=70, height=95
            )
            card_frame.pack(side='left', padx=3)
            card_frame.pack_propagate(False)
            
            card_label = tk.Label(
                card_frame, text="🂠", font=('Arial', 22, 'bold'),
                fg='gray', bg='#f8f9fa', anchor='center'
            )
            card_label.pack(expand=True, fill='both')
            
            self.board_cards.append(card_label)
            self.board_card_frames.append(card_frame)
        
        # SECTION 2: LAYOUT PRINCIPAL AVEC COLONNES
        main_layout = ttk.Frame(main_container)
        main_layout.pack(fill='both', expand=True, pady=(0, 10))
        
        # Colonne gauche: Informations table et recommandations
        left_column = ttk.Frame(main_layout)
        left_column.pack(side='left', fill='y', padx=(0, 15))
        
        # SOUS-SECTION: Informations de table
        table_info_frame = ttk.LabelFrame(left_column, text="📊 INFORMATIONS TABLE", style='Card.TFrame')
        table_info_frame.pack(fill='x', pady=(0, 10))
        
        table_content = ttk.Frame(table_info_frame)
        table_content.pack(padx=10, pady=8)
        
        # Ligne 1: Pot + Blinds (alignés à gauche)
        row1 = ttk.Frame(table_content)
        row1.pack(anchor='w', pady=(0, 8))
        
        ttk.Label(row1, text="💰 POT:", style='Heading.TLabel', font=('Arial', 13, 'bold')).pack(side='left', padx=(0, 8))
        self.pot_label = ttk.Label(row1, text="0.00€", style='Card.TLabel', font=('Arial', 18, 'bold'), foreground='#28a745')
        self.pot_label.pack(side='left', padx=(0, 20))
        
        ttk.Label(row1, text="🎲 Blinds:", style='Heading.TLabel', font=('Arial', 11)).pack(side='left', padx=(0, 8))
        self.blinds_label = ttk.Label(row1, text="0.00€ / 0.00€", style='Card.TLabel', font=('Arial', 13, 'bold'), foreground='#fd7e14')
        self.blinds_label.pack(side='left')
        
        # Ligne 2: Antes + Type (alignés à gauche) 
        row2 = ttk.Frame(table_content)
        row2.pack(anchor='w', pady=(5, 0))
        
        ttk.Label(row2, text="⚡ Antes:", style='Heading.TLabel', font=('Arial', 10)).pack(side='left', padx=(0, 8))
        self.antes_label = ttk.Label(row2, text="0.00€", style='Card.TLabel', font=('Arial', 11), foreground='#6f42c1')
        self.antes_label.pack(side='left', padx=(0, 20))
        
        self.table_type_label = ttk.Label(row2, text="Cash Game", font=('Arial', 11), foreground='#6c757d')
        self.table_type_label.pack(side='left')
        
        # SOUS-SECTION: Recommandation principale
        rec_frame = ttk.LabelFrame(left_column, text="🎯 RECOMMANDATION", style='Card.TFrame')
        rec_frame.pack(fill='x', pady=(0, 10))
        
        rec_content = ttk.Frame(rec_frame)
        rec_content.pack(padx=10, pady=8)
        
        # Action + détails en ligne
        action_line = ttk.Frame(rec_content)
        action_line.pack(fill='x', pady=(0, 5))
        
        # Action principale - beaucoup plus visible
        self.action_display = ttk.Label(action_line, text="CHECK", font=('Arial', 22, 'bold'), foreground='#28a745')
        self.action_display.pack(side='left')
        
        self.bet_size_label = ttk.Label(action_line, text="", style='Card.TLabel', font=('Arial', 16, 'bold'), foreground='#28a745')
        self.bet_size_label.pack(side='left', padx=(15, 25))
        
        # Probabilité + Risque + Confiance en ligne
        ttk.Label(action_line, text="Victoire:", style='Heading.TLabel').pack(side='left', padx=(0, 2))
        self.win_prob_label = ttk.Label(action_line, text="50%", font=('Arial', 12, 'bold'), foreground='green')
        self.win_prob_label.pack(side='left', padx=(0, 15))
        
        ttk.Label(action_line, text="Risque:", style='Heading.TLabel').pack(side='left', padx=(0, 2))
        self.risk_label = ttk.Label(action_line, text="30%", font=('Arial', 12, 'bold'), foreground='orange')
        self.risk_label.pack(side='left', padx=(0, 15))
        
        ttk.Label(action_line, text="Confiance:", style='Heading.TLabel').pack(side='left', padx=(0, 2))
        self.main_confidence_label = ttk.Label(action_line, text="85%", font=('Arial', 12, 'bold'), foreground='blue')
        self.main_confidence_label.pack(side='left', padx=(0, 20))
        
        # Raisonnement
        ttk.Label(rec_content, text="🧠 Raisonnement:", style='Heading.TLabel').pack(anchor='w', pady=(5, 2))
        self.main_reasoning_label = ttk.Label(
            rec_content, text="En attente d'analyse...", font=('Arial', 10),
            wraplength=350, justify='left'
        )
        self.main_reasoning_label.pack(anchor='w')
        
        # SOUS-SECTION: Statistiques compactes
        stats_frame = ttk.LabelFrame(left_column, text="📈 STATISTIQUES", style='Card.TFrame')
        stats_frame.pack(fill='x')
        
        stats_content = ttk.Frame(stats_frame)
        stats_content.pack(padx=10, pady=6)
        
        # Ligne 1: Mains + Taux (alignés à gauche)
        stats_line1 = ttk.Frame(stats_content)
        stats_line1.pack(anchor='w', pady=(0, 8))
        
        ttk.Label(stats_line1, text="Mains:", style='Heading.TLabel', font=('Arial', 11, 'bold')).pack(side='left')
        self.hands_played_value = ttk.Label(stats_line1, text="0", style='Card.TLabel', font=('Arial', 13, 'bold'), foreground='#495057')
        self.hands_played_value.pack(side='left', padx=(8, 15))
        
        ttk.Label(stats_line1, text="Gagnées:", style='Heading.TLabel', font=('Arial', 11, 'bold')).pack(side='left')
        self.hands_won_value = ttk.Label(stats_line1, text="0", style='Card.TLabel', font=('Arial', 13, 'bold'), foreground='#28a745')
        self.hands_won_value.pack(side='left', padx=(8, 20))
        
        ttk.Label(stats_line1, text="TAUX:", style='Heading.TLabel', font=('Arial', 12, 'bold')).pack(side='left')
        self.win_rate_value = ttk.Label(stats_line1, text="0.0%", style='Card.TLabel', font=('Arial', 16, 'bold'), foreground='#dc3545')
        self.win_rate_value.pack(side='left', padx=(8, 0))
        
        # Ligne 2: Pro + Performance (alignés à gauche)
        stats_line2 = ttk.Frame(stats_content)
        stats_line2.pack(anchor='w', pady=(5, 0))
        
        ttk.Label(stats_line2, text="Pro:", style='Heading.TLabel', font=('Arial', 10)).pack(side='left')
        self.expected_rate_value = ttk.Label(stats_line2, text="68.0%", style='Card.TLabel', font=('Arial', 11), foreground='#6f42c1')
        self.expected_rate_value.pack(side='left', padx=(5, 20))
        
        ttk.Label(stats_line2, text="Perf:", style='Heading.TLabel', font=('Arial', 10)).pack(side='left')
        self.performance_ratio_value = ttk.Label(stats_line2, text="0.0%", style='Card.TLabel', font=('Arial', 11), foreground='#fd7e14')
        self.performance_ratio_value.pack(side='left', padx=(5, 0))
        
        # Colonne droite: Informations joueurs
        right_column = ttk.Frame(main_layout)
        right_column.pack(side='left', fill='both', expand=True, padx=(5, 10))
        
        # SECTION 4A: NOS INFOS PERSONNELLES
        hero_frame = ttk.LabelFrame(right_column, text="👤 MOI", style='Card.TFrame')
        hero_frame.pack(fill='x', pady=(0, 10))  # Suppression des contraintes de largeur
        
        hero_content = ttk.Frame(hero_frame)
        hero_content.pack(fill='x', padx=8, pady=6)
        
        # Pseudo du joueur
        ttk.Label(hero_content, text="Pseudo:", style='Heading.TLabel').pack(anchor='w')
        self.hero_name_label = ttk.Label(hero_content, text="MonPseudo", style='Card.TLabel', font=('Arial', 12, 'bold'), foreground='blue')
        self.hero_name_label.pack(anchor='w', pady=(2, 8))
        
        # Stack personnel
        ttk.Label(hero_content, text="Mon Stack:", style='Heading.TLabel').pack(anchor='w')
        self.hero_stack_label = ttk.Label(hero_content, text="2500€", style='Card.TLabel', font=('Arial', 14, 'bold'), foreground='green')
        self.hero_stack_label.pack(anchor='w', pady=(2, 8))
        
        # Position à la table
        ttk.Label(hero_content, text="Position:", style='Heading.TLabel').pack(anchor='w')
        self.hero_position_label = ttk.Label(hero_content, text="Button", style='Card.TLabel', font=('Arial', 11))
        self.hero_position_label.pack(anchor='w', pady=(2, 0))
        
        # SECTION 4B: AUTRES JOUEURS ACTIFS
        players_frame = ttk.LabelFrame(right_column, text="👥 AUTRES JOUEURS", style='Card.TFrame')
        players_frame.pack(fill='both', expand=True, pady=(10, 0))  # Suppression des contraintes de largeur
        
        players_content = ttk.Frame(players_frame)
        players_content.pack(fill='both', expand=True, padx=8, pady=6)
        
        # Info générale - Table 9-max
        players_info = ttk.Frame(players_content)
        players_info.pack(fill='x', pady=(0, 8))
        
        ttk.Label(players_info, text="Actifs:", style='Heading.TLabel').pack(side='left')
        self.active_players_count = ttk.Label(players_info, text="8/9", style='Card.TLabel', font=('Arial', 11, 'bold'))
        self.active_players_count.pack(side='left', padx=(5, 0))
        
        # Scroll pour la liste des joueurs
        players_scroll_frame = ttk.Frame(players_content)
        players_scroll_frame.pack(fill='both', expand=True)
        
        self.players_list_frame = ttk.Frame(players_scroll_frame)
        self.players_list_frame.pack(fill='both', expand=True)
        
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
        
        # Affichage vertical compact pour les autres joueurs avec positions
        for i, player in enumerate(sorted_players):
            player_frame = ttk.Frame(self.players_list_frame)
            player_frame.pack(fill='x', pady=2, padx=5)
            
            # Couleur de statut
            status_color = '#28a745' if player['status'] == 'actif' else '#6c757d'
            status_icon = "✅" if player['status'] == 'actif' else "⏸️"
            
            # Déterminer icône de position
            position_icon = ""
            position_color = '#495057'
            if player.get('is_button'):
                position_icon = " 🔴"  # Button
                position_color = '#dc3545'
            elif player.get('is_sb'):
                position_icon = " 🟡"  # Small Blind
                position_color = '#ffc107'
            elif player.get('is_bb'):
                position_icon = " 🔵"  # Big Blind
                position_color = '#007bff'
            
            # Ligne principale: Position + Nom + Stack
            main_line = ttk.Frame(player_frame)
            main_line.pack(fill='x')
            
            # Position et statut
            position_text = f"{player.get('position_name', 'POS')}{position_icon}"
            ttk.Label(main_line, text=position_text, font=('Arial', 9, 'bold'), foreground=position_color).pack(side='left')
            
            ttk.Label(main_line, text=status_icon, font=('Arial', 10)).pack(side='left', padx=(5, 8))
            
            # Nom du joueur
            name_label = ttk.Label(main_line, text=player['name'], 
                                 font=('Arial', 11, 'bold'), foreground=status_color)
            name_label.pack(side='left', padx=(5, 0))
            
            # Stack
            stack_text = f"{player.get('stack', 0):.0f}€" if isinstance(player.get('stack'), (int, float)) else str(player.get('stack', '0€'))
            stack_label = ttk.Label(main_line, text=stack_text, 
                                  font=('Arial', 10, 'bold'), foreground='#28a745')
            stack_label.pack(side='right')
            
            # Ligne secondaire: VPIP/PFR (stats poker)
            stats_line = ttk.Frame(player_frame)
            stats_line.pack(fill='x', pady=(2, 0))
            
            vpip = player.get('vpip', 0)
            pfr = player.get('pfr', 0)
            vpip_text = f"{vpip}%" if isinstance(vpip, (int, float)) else str(vpip)
            pfr_text = f"{pfr}%" if isinstance(pfr, (int, float)) else str(pfr)
            
            ttk.Label(stats_line, text=f"VPIP: {vpip_text}", font=('Arial', 8), foreground='#6c757d').pack(side='left')
            ttk.Label(stats_line, text=f"PFR: {pfr_text}", font=('Arial', 8), foreground='#6c757d').pack(side='left', padx=(10, 0))
    
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
        
        # Section: Personnalisation
        custom_frame = ctk.CTkFrame(main_frame)
        custom_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(custom_frame, text="🎨 Personnalisation Interface", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Couleur d'accent
        color_frame = ctk.CTkFrame(custom_frame)
        color_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(color_frame, text="Couleur d'accent:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        
        self.accent_var = tk.StringVar(value=self.accent_color)
        accent_menu = ctk.CTkOptionMenu(color_frame, values=["blue", "green", "dark-blue", "orange", "red"],
                                       variable=self.accent_var, command=self.change_accent_color)
        accent_menu.pack(side='left', padx=10)
        
        # Police
        font_frame = ctk.CTkFrame(custom_frame)
        font_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(font_frame, text="Police interface:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        
        self.font_var = tk.StringVar(value=self.font_family)
        font_menu = ctk.CTkOptionMenu(font_frame, values=["Arial", "Helvetica", "Times", "Courier"],
                                     variable=self.font_var, command=self.change_font)
        font_menu.pack(side='left', padx=10)
        
        # Opacité
        opacity_frame = ctk.CTkFrame(custom_frame)
        opacity_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        ctk.CTkLabel(opacity_frame, text="Opacité fenêtre:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        
        self.opacity_var = tk.DoubleVar(value=self.opacity)
        opacity_slider = ctk.CTkSlider(opacity_frame, from_=0.7, to=1.0, variable=self.opacity_var, 
                                      command=self.change_opacity)
        opacity_slider.pack(side='left', padx=10, fill='x', expand=True)
        
        self.opacity_label = ctk.CTkLabel(opacity_frame, text=f"{int(self.opacity*100)}%")
        self.opacity_label.pack(side='left', padx=10)
        
        # Section: Export/Import
        data_frame = ctk.CTkFrame(main_frame)
        data_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(data_frame, text="💾 Gestion des Données", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        buttons_frame = ctk.CTkFrame(data_frame)
        buttons_frame.pack(pady=(0, 15))
        
        ctk.CTkButton(buttons_frame, text="📤 Exporter Base CFR", 
                     command=self.export_cfr_data).pack(side='left', padx=10, pady=10)
        
        ctk.CTkButton(buttons_frame, text="📥 Importer Base CFR", 
                     command=self.import_cfr_data).pack(side='left', padx=10, pady=10)
    
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
        
        ctk.CTkLabel(iter_frame, text="Itérations CFR:").pack(side='left', padx=(10, 20))
        self.cfr_iterations = ctk.CTkEntry(iter_frame, placeholder_text="100000")
        self.cfr_iterations.pack(side='left', padx=10)
        
        # Profondeur CFR
        depth_frame = ctk.CTkFrame(cfr_frame)
        depth_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(depth_frame, text="Profondeur CFR:").pack(side='left', padx=(10, 20))
        self.cfr_depth = ctk.CTkEntry(depth_frame, placeholder_text="3")
        self.cfr_depth.pack(side='left', padx=10)
        
        # Epsilon Exploration
        eps_frame = ctk.CTkFrame(cfr_frame)
        eps_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        ctk.CTkLabel(eps_frame, text="Epsilon Exploration:").pack(side='left', padx=(10, 20))
        self.cfr_epsilon = ctk.CTkEntry(eps_frame, placeholder_text="0.3")
        self.cfr_epsilon.pack(side='left', padx=10)
        
        # Section: Gestion des Ressources
        resource_frame = ctk.CTkFrame(main_frame)
        resource_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(resource_frame, text="⚡ Gestion des Ressources", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Limite CPU
        cpu_frame = ctk.CTkFrame(resource_frame)
        cpu_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(cpu_frame, text="Limite CPU (%):").pack(side='left', padx=(10, 20))
        self.cpu_limit = ctk.CTkSlider(cpu_frame, from_=10, to=100)
        self.cpu_limit.pack(side='left', padx=10, fill='x', expand=True)
        self.cpu_limit.set(80)
        
        # Limite RAM
        ram_frame = ctk.CTkFrame(resource_frame)
        ram_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        ctk.CTkLabel(ram_frame, text="Limite RAM (GB):").pack(side='left', padx=(10, 20))
        self.ram_limit = ctk.CTkSlider(ram_frame, from_=1, to=16)
        self.ram_limit.pack(side='left', padx=10, fill='x', expand=True)
        self.ram_limit.set(8)
    
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
        """Boucle de mise à jour de l'interface"""
        while self.running:
            try:
                if self.app_manager:
                    # Récupérer les données du gestionnaire (si la méthode existe)
                    if hasattr(self.app_manager, 'get_display_data'):
                        data = self.app_manager.get_display_data()
                        # Mettre à jour dans le thread principal
                        self.root.after(0, lambda: self.update_display(data))
                        
                        # Mettre à jour les joueurs si les données sont disponibles
                        if data.get('players_info'):
                            self.root.after(0, lambda: self.update_players_from_ocr(data['players_info']))
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
                        self.root.after(0, lambda: self.update_display(data))
                
                time.sleep(1)  # Mise à jour chaque seconde
                
            except Exception as e:
                print(f"Erreur dans la boucle de mise à jour: {e}")
                time.sleep(1)
    
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