"""
Interface graphique de RTPA Studio
Utilise CustomTkinter pour une interface moderne
"""

import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import threading
import time
import sys
import os
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
        
        # Configuration Windows spécifique pour le gestionnaire des tâches
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes
                
                # Obtenir le handle de la fenêtre
                def get_hwnd():
                    def callback(hwnd, pid):
                        if ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wintypes.DWORD())) == os.getpid():
                            return hwnd
                        return True
                    
                    return ctypes.windll.user32.EnumWindows(callback, 0)
                
                # Définir l'icône et le titre de l'application
                self.root.after(100, self._set_windows_properties)
                
            except ImportError:
                pass
            except Exception:
                pass
        
        # Variables de contrôle pour les sliders
        self.cpu_limit = None
        self.ram_limit = None
        self.cpu_value_label = None
        self.ram_value_label = None
        
        # Variables pour les profils de performance
        self.performance_profile_dropdown = None
        self.profile_description_label = None
        self.profile_status_label = None
        self.apply_profile_button = None
        
        # Interface utilisateur
        self.create_interface()
        
        # Initialisation des profils de performance
        self._load_current_profile()
        
        # Configuration de l'événement de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Démarrer la mise à jour des tâches
        self.root.after(1000, self._update_task_display_loop)
        
        # Charger les paramètres d'affichage
        self.root.after(2000, self.load_display_settings)
    
    def _set_windows_properties(self):
        """Configure les propriétés Windows pour une meilleure identification"""
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes
                
                # Essayer de définir le nom de classe de la fenêtre
                hwnd = self.root.winfo_id()
                if hwnd:
                    # Définir le titre de la fenêtre pour le gestionnaire des tâches
                    ctypes.windll.user32.SetWindowTextW(hwnd, "RTPA Studio")
                    
            except Exception as e:
                pass  # Ignorer les erreurs de configuration Windows
    
    def create_interface(self):
        """Crée tous les éléments de l'interface"""
        
        # Container principal pour l'affichage structuré
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header avec logo - Style professionnel
        self.controls_frame = ctk.CTkFrame(self.main_frame, height=100)
        self.controls_frame.pack(fill='x', pady=(0, 10))
        self.controls_frame.pack_propagate(False)
        
        # Container horizontal pour logo + informations
        header_container = ctk.CTkFrame(self.controls_frame)
        header_container.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Essayer de charger le logo RTPA Studio
        try:
            from PIL import Image
            import os
            
            # Chercher le logo dans les différents emplacements
            logo_paths = [
                "assets/RTPA_Studio_logo_1757286600683.png",
                "attached_assets/RTPA_Studio_logo_1757286600683.png",
                "assets/RTPA_Studio_icon_1024_1757286600683.png",
                "attached_assets/RTPA_Studio_icon_1024_1757286600683.png"
            ]
            
            logo_loaded = False
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    logo_image = Image.open(logo_path)
                    # Adapter la taille selon le type de fichier
                    if "logo" in logo_path:
                        logo_image = logo_image.resize((180, 50), Image.Resampling.LANCZOS)
                        self.header_logo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(180, 50))
                    else:
                        logo_image = logo_image.resize((50, 50), Image.Resampling.LANCZOS)
                        self.header_logo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(50, 50))
                    
                    # Frame gauche pour le logo
                    logo_frame = ctk.CTkFrame(header_container, fg_color="transparent")
                    logo_frame.pack(side='left', padx=(5, 20), pady=5)
                    
                    logo_label = ctk.CTkLabel(logo_frame, image=self.header_logo, text="")
                    logo_label.pack()
                    logo_loaded = True
                    break
                    
            if not logo_loaded:
                raise FileNotFoundError("Aucun logo trouvé")
                
        except Exception as e:
            # Fallback avec icône stylisée si pas de logo
            logo_frame = ctk.CTkFrame(header_container, fg_color="transparent")
            logo_frame.pack(side='left', padx=(5, 20), pady=5)
            
            fallback_label = ctk.CTkLabel(
                logo_frame,
                text="🎯\nRTPA",
                font=ctk.CTkFont(size=14, weight="bold"),
                justify="center"
            )
            fallback_label.pack()
        
        # Frame droite pour les informations système
        info_frame = ctk.CTkFrame(header_container, fg_color="transparent")
        info_frame.pack(side='left', fill='both', expand=True)
        
        # Titre principal
        self.status_label = ctk.CTkLabel(
            info_frame,
            text="Real-Time Poker Assistant (CFR/Nash)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.status_label.pack(anchor='w', pady=(0, 2))
        
        # Status surveillance avec icône (orange par défaut)
        self.activity_status_label = ctk.CTkLabel(
            info_frame,
            text="🟠 Surveillance active",
            font=ctk.CTkFont(size=12),
            text_color="#ff8c00"
        )
        self.activity_status_label.pack(anchor='w', pady=(0, 2))
        
        # Temps restant CFR
        self.cfr_time_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#666666"
        )
        self.cfr_time_label.pack(anchor='w')
        
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
        
        # Initialiser l'optimiseur système
        try:
            from src.utils.system_optimizer import SystemOptimizer
            self.system_optimizer = SystemOptimizer()
            # Charger la configuration sauvegardée
            self.system_optimizer.load_configuration()
            print("✅ Optimiseur système initialisé")
        except Exception as e:
            print(f"⚠️ Erreur initialisation optimiseur: {e}")
            self.system_optimizer = None
        
        # Charger les paramètres sauvegardés après création des éléments
        self.load_saved_settings()
        
        # Charger la configuration OCR si elle existe (avec vérification)
        if hasattr(self, 'ocr_zone_entries'):
            self.load_ocr_configuration()
        
        # Démarrer les mises à jour
        self.root.after(1000, self.update_cfr_progress)  # Démarrer après 1 seconde
        self.root.after(2000, self.update_system_metrics)  # Métriques système
        
        # Initialiser l'affichage de la tâche
        if hasattr(self, 'main_task_label'):
            self.main_task_label.configure(text="Démarrage du système...", text_color="#ff8c00")
    
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
        self.rec_frame = ttk.LabelFrame(left_column, text="🎯 RECOMMANDATION", style='Card.TFrame')
        self.rec_frame.pack(fill='x', pady=(0, 10))
        
        # Action recommandée en gros
        self.action_label = tk.Label(self.rec_frame, text="---", font=('Arial', 24, 'bold'),
                                    fg='#ff6600', bg='#f0f0f0')
        self.action_label.pack(pady=(10, 5))
        
        # Détails recommandation en ligne
        self.rec_details = tk.Frame(self.rec_frame, bg='#f0f0f0')
        self.rec_details.pack(fill='x', padx=15, pady=(0, 15))
        
        # Probabilité de victoire et taille de mise
        self.left_rec = tk.Frame(self.rec_details, bg='#f0f0f0')
        self.left_rec.pack(side='left')
        
        self.win_prob_title = tk.Label(self.left_rec, text="Victoire:", font=('Arial', 10), bg='#f0f0f0')
        self.win_prob_title.pack(anchor='w')
        self.win_prob_label = tk.Label(self.left_rec, text="--", font=('Arial', 10, 'bold'), 
                                      fg='#00b300', bg='#f0f0f0')
        self.win_prob_label.pack(anchor='w')
        
        # Niveau de risque au centre
        center_rec = tk.Frame(self.rec_details, bg='#f0f0f0')
        center_rec.pack(side='left', padx=30)
        
        tk.Label(center_rec, text="Risque:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w')
        self.risk_label = tk.Label(center_rec, text="--", font=('Arial', 10, 'bold'), 
                                  fg='#ff3300', bg='#f0f0f0')
        self.risk_label.pack(anchor='w')
        
        # Confiance à droite
        right_rec = tk.Frame(self.rec_details, bg='#f0f0f0')
        right_rec.pack(side='right')
        
        tk.Label(right_rec, text="Confiance:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w')
        self.confidence_label = tk.Label(right_rec, text="--", font=('Arial', 10, 'bold'), 
                                        fg='#0066ff', bg='#f0f0f0')
        self.confidence_label.pack(anchor='w')
        
        # Raisonnement (séparé et plus visible)
        self.reasoning_frame = tk.Frame(self.rec_frame, bg='#f8f8f8', relief='sunken', bd=1)
        self.reasoning_frame.pack(fill='x', padx=15, pady=(5, 15))
        
        tk.Label(self.reasoning_frame, text="💭 Raisonnement:", font=('Arial', 9, 'bold'),
                bg='#f8f8f8').pack(anchor='w', padx=8, pady=(5, 2))
        
        self.reasoning_label = tk.Label(self.reasoning_frame, text="En attente d'analyse...", 
                                      font=('Arial', 9), bg='#f8f8f8', fg='#444', 
                                      wraplength=400, justify='left')
        self.reasoning_label.pack(anchor='w', padx=8, pady=(0, 8))
        
        # Colonne droite: Informations joueurs et statistiques
        self.right_column = ttk.Frame(columns_container)
        self.right_column.pack(side='right', fill='y', padx=(0, 0))
        
        # SECTION 4A: MES INFORMATIONS
        hero_info_frame = ttk.LabelFrame(self.right_column, text="👤 MOI", style='Card.TFrame')
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
        players_frame = ttk.LabelFrame(self.right_column, text="👥 AUTRES JOUEURS", style='Card.TFrame')
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
        stats_frame = ttk.LabelFrame(self.right_column, text="📊 STATISTIQUES", style='Card.TFrame')
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
        
        # Checkboxes d'affichage avec callbacks
        checkboxes_frame = ctk.CTkFrame(ui_frame)
        checkboxes_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        self.show_probabilities = ctk.CTkCheckBox(checkboxes_frame, text="Afficher probabilités",
                                                 command=self.toggle_probabilities_display)
        self.show_probabilities.pack(side='left', padx=20, pady=10)
        self.show_probabilities.select()
        
        self.show_recommendations = ctk.CTkCheckBox(checkboxes_frame, text="Afficher recommandations",
                                                   command=self.toggle_recommendations_display)
        self.show_recommendations.pack(side='left', padx=20, pady=10)
        self.show_recommendations.select()
        
        self.show_statistics = ctk.CTkCheckBox(checkboxes_frame, text="Afficher statistiques",
                                              command=self.toggle_statistics_display)
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
        
        # === SECTION CALIBRAGE OCR ===
        ocr_calibration_frame = ctk.CTkFrame(settings_container)
        ocr_calibration_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(ocr_calibration_frame, text="🔍 Calibrage OCR", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 15))
        
        # Sélection plateforme
        platform_frame = ctk.CTkFrame(ocr_calibration_frame)
        platform_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        ctk.CTkLabel(platform_frame, text="Plateforme:", font=ctk.CTkFont(size=12, weight="bold")).pack(side='left', padx=(10, 10))
        
        self.platform_selector = ctk.CTkComboBox(
            platform_frame,
            values=["PokerStars", "Winamax", "PMU", "PartyPoker"],
            command=self.change_ocr_platform,
            width=150
        )
        self.platform_selector.pack(side='left', padx=(0, 10))
        self.platform_selector.set("PokerStars")  # Défaut
        
        # Instructions
        instruction_text = ctk.CTkLabel(
            ocr_calibration_frame,
            text="Ajustez les coordonnées pour optimiser la détection OCR selon votre résolution d'écran",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        instruction_text.pack(pady=(0, 15))
        
        # Zones OCR configurables
        zones_frame = ctk.CTkFrame(ocr_calibration_frame)
        zones_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Créer les champs pour chaque zone
        self.ocr_zone_entries = {}
        zones_config = [
            ("Cartes Héros", "hero_cards"),
            ("Board", "board_cards"),
            ("Pot", "pot_size"),
            ("Stack Héros", "hero_stack"),
            ("Blinds", "blinds"),
            ("Boutons Action", "action_buttons")
        ]
        
        for i, (zone_name, zone_key) in enumerate(zones_config):
            zone_row = ctk.CTkFrame(zones_frame)
            zone_row.pack(fill='x', pady=5, padx=10)
            
            # Label de la zone
            ctk.CTkLabel(zone_row, text=f"{zone_name}:", width=120, font=ctk.CTkFont(size=11, weight="bold")).pack(side='left', padx=(5, 10))
            
            # Champs pour les coordonnées
            coords_frame = ctk.CTkFrame(zone_row)
            coords_frame.pack(side='left', padx=(0, 10))
            
            self.ocr_zone_entries[zone_key] = {}
            
            # Top
            ctk.CTkLabel(coords_frame, text="Y:", width=20).pack(side='left', padx=(5, 2))
            self.ocr_zone_entries[zone_key]['top'] = ctk.CTkEntry(coords_frame, width=60, placeholder_text="580")
            self.ocr_zone_entries[zone_key]['top'].pack(side='left', padx=(0, 5))
            
            # Left
            ctk.CTkLabel(coords_frame, text="X:", width=20).pack(side='left', padx=(5, 2))
            self.ocr_zone_entries[zone_key]['left'] = ctk.CTkEntry(coords_frame, width=60, placeholder_text="440")
            self.ocr_zone_entries[zone_key]['left'].pack(side='left', padx=(0, 5))
            
            # Width
            ctk.CTkLabel(coords_frame, text="L:", width=20).pack(side='left', padx=(5, 2))
            self.ocr_zone_entries[zone_key]['width'] = ctk.CTkEntry(coords_frame, width=60, placeholder_text="140")
            self.ocr_zone_entries[zone_key]['width'].pack(side='left', padx=(0, 5))
            
            # Height
            ctk.CTkLabel(coords_frame, text="H:", width=20).pack(side='left', padx=(5, 2))
            self.ocr_zone_entries[zone_key]['height'] = ctk.CTkEntry(coords_frame, width=60, placeholder_text="50")
            self.ocr_zone_entries[zone_key]['height'].pack(side='left', padx=(0, 5))
        
        # Boutons de contrôle
        ocr_buttons_frame = ctk.CTkFrame(ocr_calibration_frame)
        ocr_buttons_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.load_preset_btn = ctk.CTkButton(
            ocr_buttons_frame,
            text="📋 Charger Preset",
            command=self.load_ocr_preset,
            width=150
        )
        self.load_preset_btn.pack(side='left', padx=(10, 5))
        
        self.apply_calibration_btn = ctk.CTkButton(
            ocr_buttons_frame,
            text="✅ Appliquer",
            command=self.apply_ocr_calibration,
            width=150
        )
        self.apply_calibration_btn.pack(side='left', padx=(5, 5))
        
        self.auto_calibrate_btn = ctk.CTkButton(
            ocr_buttons_frame,
            text="🤖 Auto-Calibrage",
            command=self.auto_calibrate_ocr,
            width=150
        )
        self.auto_calibrate_btn.pack(side='left', padx=(5, 5))
        
        self.test_ocr_btn = ctk.CTkButton(
            ocr_buttons_frame,
            text="🔍 Tester OCR",
            command=self.test_ocr_zones,
            width=150
        )
        self.test_ocr_btn.pack(side='left', padx=(5, 10))
        
        # === SECTION CFR BASE DE DONNÉES ===
        cfr_db_frame = ctk.CTkFrame(settings_container)
        cfr_db_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(cfr_db_frame, text="💾 Base CFR/Nash", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 15))
        
        # Boutons Export/Import
        cfr_buttons_frame = ctk.CTkFrame(cfr_db_frame)
        cfr_buttons_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.export_cfr_btn = ctk.CTkButton(cfr_buttons_frame, text="📤 Exporter CFR", 
                                           command=self.export_cfr_database, width=180)
        self.export_cfr_btn.pack(side='left', padx=(10, 5), pady=15)
        
        self.import_cfr_btn = ctk.CTkButton(cfr_buttons_frame, text="📥 Importer CFR", 
                                           command=self.import_cfr_database, width=180)
        self.import_cfr_btn.pack(side='left', padx=5, pady=15)
        
        # Status export/import
        self.cfr_status_label = ctk.CTkLabel(cfr_buttons_frame, text="Prêt pour export/import", 
                                            font=ctk.CTkFont(size=10), text_color="gray")
        self.cfr_status_label.pack(side='right', padx=10, pady=15)
        
        # Description des fonctionnalités
        desc_frame = ctk.CTkFrame(cfr_db_frame)
        desc_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        desc_text = "Sauvegardez et chargez vos calculs CFR/Nash pour préserver votre entraînement"
        ctk.CTkLabel(desc_frame, text=desc_text, font=ctk.CTkFont(size=10), 
                    text_color="gray", wraplength=400).pack(pady=10)
        
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
        """Création de l'onglet Performance avec profils et métriques système"""
        
        # Container principal
        perf_container = ctk.CTkFrame(self.performance_tab)
        perf_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(perf_container, text="⚡ Performance & Profils", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 15))
        
        # === SECTION PROFILS DE PERFORMANCE ===
        profiles_frame = ctk.CTkFrame(perf_container)
        profiles_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(profiles_frame, text="🚀 Profils de Performance", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Description du profil actuel
        self.profile_description_label = ctk.CTkLabel(profiles_frame, 
                                                     text="", 
                                                     font=ctk.CTkFont(size=12),
                                                     text_color="gray",
                                                     wraplength=600)
        self.profile_description_label.pack(pady=(0, 10))
        
        # Sélecteur de profils
        profiles_selector_frame = ctk.CTkFrame(profiles_frame)
        profiles_selector_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        ctk.CTkLabel(profiles_selector_frame, text="Profil actuel:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(side='left', padx=(10, 10))
        
        # Menu déroulant des profils
        self.performance_profile_dropdown = ctk.CTkOptionMenu(
            profiles_selector_frame,
            values=["💚 Éco", "⚖️ Équilibré", "🚀 Performance"],
            command=self.on_profile_changed,
            width=150,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.performance_profile_dropdown.pack(side='left', padx=(0, 20))
        
        # Bouton d'application 
        self.apply_profile_button = ctk.CTkButton(
            profiles_selector_frame,
            text="✅ Appliquer",
            command=self.apply_selected_profile,
            width=100,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2b7a0b",
            hover_color="#22631f"
        )
        self.apply_profile_button.pack(side='left', padx=(0, 10))
        
        # Status d'application
        self.profile_status_label = ctk.CTkLabel(profiles_selector_frame, 
                                               text="",
                                               font=ctk.CTkFont(size=11),
                                               text_color="#00b300")
        self.profile_status_label.pack(side='left', padx=(10, 10))
        
        # Initialiser le profil par défaut
        self._init_performance_profiles()
        
        # === MÉTRIQUES SYSTÈME EN TEMPS RÉEL ===
        system_metrics_frame = ctk.CTkFrame(perf_container)
        system_metrics_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(system_metrics_frame, text="📊 Utilisation des Ressources", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Container pour les métriques
        metrics_container = ctk.CTkFrame(system_metrics_frame)
        metrics_container.pack(fill='x', padx=20, pady=(0, 15))
        
        # CPU Usage
        cpu_frame = ctk.CTkFrame(metrics_container)
        cpu_frame.pack(fill='x', pady=(10, 5))
        
        ctk.CTkLabel(cpu_frame, text="CPU:", font=ctk.CTkFont(size=14, weight="bold")).pack(side='left', padx=(10, 10))
        
        self.cpu_usage_bar = ctk.CTkProgressBar(cpu_frame, width=200, height=20)
        self.cpu_usage_bar.pack(side='left', padx=(0, 10))
        self.cpu_usage_bar.set(0)
        
        self.cpu_usage_label = ctk.CTkLabel(cpu_frame, text="0%", font=ctk.CTkFont(size=12, weight="bold"))
        self.cpu_usage_label.pack(side='left', padx=(0, 10))
        
        # RAM Usage  
        ram_frame = ctk.CTkFrame(metrics_container)
        ram_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(ram_frame, text="RAM:", font=ctk.CTkFont(size=14, weight="bold")).pack(side='left', padx=(10, 10))
        
        self.ram_usage_bar = ctk.CTkProgressBar(ram_frame, width=200, height=20)
        self.ram_usage_bar.pack(side='left', padx=(0, 10))
        self.ram_usage_bar.set(0)
        
        self.ram_usage_label = ctk.CTkLabel(ram_frame, text="0%", font=ctk.CTkFont(size=12, weight="bold"))
        self.ram_usage_label.pack(side='left', padx=(0, 10))
        
        # GPU Usage (si disponible)
        gpu_frame = ctk.CTkFrame(metrics_container)
        gpu_frame.pack(fill='x', pady=(5, 10))
        
        ctk.CTkLabel(gpu_frame, text="GPU:", font=ctk.CTkFont(size=14, weight="bold")).pack(side='left', padx=(10, 10))
        
        self.gpu_usage_bar = ctk.CTkProgressBar(gpu_frame, width=200, height=20)
        self.gpu_usage_bar.pack(side='left', padx=(0, 10))
        self.gpu_usage_bar.set(0)
        
        self.gpu_usage_label = ctk.CTkLabel(gpu_frame, text="N/A", font=ctk.CTkFont(size=12, weight="bold"))
        self.gpu_usage_label.pack(side='left', padx=(0, 10))
        
        # Démarrer la mise à jour des métriques
        self.root.after(1000, self.update_system_metrics)
        
        # === AFFICHAGE TÂCHE EN COURS UNIFIÉ ===
        task_frame = ctk.CTkFrame(perf_container)
        task_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(task_frame, text="📋 Tâche en cours", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Affichage principal de la tâche avec progression
        self.main_task_label = ctk.CTkLabel(task_frame, text="Initialisation du système...", 
                                           font=ctk.CTkFont(size=14, weight="bold"), 
                                           text_color="#00b300")
        self.main_task_label.pack(pady=(5, 10))
        
        # Barre de progression visuelle
        self.task_progress_bar = ctk.CTkProgressBar(task_frame, width=400, height=20)
        self.task_progress_bar.pack(pady=(0, 10))
        self.task_progress_bar.set(0)
        
        # Détail de progression (pourcentage et temps)
        self.task_detail_label = ctk.CTkLabel(task_frame, text="", 
                                             font=ctk.CTkFont(size=11), 
                                             text_color="gray")
        self.task_detail_label.pack(pady=(0, 15))
        
        # Vérification PyTorch et bouton d'installation si nécessaire
        pytorch_frame = ctk.CTkFrame(perf_container)
        pytorch_frame.pack(fill='x', pady=(0, 20))
        
        try:
            import torch
            TORCH_AVAILABLE = True
            
            ctk.CTkLabel(pytorch_frame, text="🚀 PyTorch Status", 
                        font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
            
            ctk.CTkLabel(pytorch_frame, text="✅ PyTorch installé et fonctionnel", 
                        font=ctk.CTkFont(size=14, weight="bold"), 
                        text_color="#00b300").pack(pady=(5, 5))
            
            # Informations détaillées de PyTorch
            info_frame = ctk.CTkFrame(pytorch_frame)
            info_frame.pack(fill='x', padx=20, pady=(5, 15))
            
            ctk.CTkLabel(info_frame, 
                        text=f"Version: {torch.__version__}", 
                        font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 2))
            
            # Détection GPU CUDA
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else "GPU CUDA"
                ctk.CTkLabel(info_frame, 
                            text=f"🎮 GPU détecté: {gpu_name}", 
                            font=ctk.CTkFont(size=11), 
                            text_color="#00b300").pack(pady=2)
            else:
                ctk.CTkLabel(info_frame, 
                            text="💻 Fonctionnement CPU (GPU CUDA non détecté)", 
                            font=ctk.CTkFont(size=11), 
                            text_color="#666666").pack(pady=2)
            
            ctk.CTkLabel(info_frame, 
                        text="Accélération GPU activée pour les calculs CFR intensifs", 
                        font=ctk.CTkFont(size=10), 
                        text_color="gray").pack(pady=(2, 10))
        except ImportError:
            TORCH_AVAILABLE = False
            ctk.CTkLabel(pytorch_frame, text="⚠️ PyTorch non détecté", 
                        font=ctk.CTkFont(size=14, weight="bold"), 
                        text_color="#ff6600").pack(pady=(15, 5))
            
            ctk.CTkLabel(pytorch_frame, 
                        text="Le monitoring GPU avancé nécessite PyTorch installé.\nSans PyTorch, seules les métriques CPU et RAM basiques sont disponibles.", 
                        font=ctk.CTkFont(size=12), 
                        text_color="gray").pack(pady=(0, 10))
            
            # Bouton d'installation PyTorch
            self.install_pytorch_btn = ctk.CTkButton(pytorch_frame, 
                                                   text="🔥 Installer PyTorch",
                                                   command=self.install_pytorch,
                                                   width=200,
                                                   font=ctk.CTkFont(weight="bold"))
            self.install_pytorch_btn.pack(pady=(5, 15))
            
            # Progress bar pour l'installation (masquée par défaut)
            self.pytorch_progress = ctk.CTkProgressBar(pytorch_frame, width=300)
            self.pytorch_progress.pack(pady=(0, 10))
            self.pytorch_progress.pack_forget()  # Masquer initialement
            
            self.pytorch_status_label = ctk.CTkLabel(pytorch_frame, text="", 
                                                    font=ctk.CTkFont(size=11))
            self.pytorch_status_label.pack()
        
        # === PROFILS DE PERFORMANCE ===
        profiles_frame = ctk.CTkFrame(perf_container)
        profiles_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(profiles_frame, text="⚡ Profils de Performance", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Sélecteur de profil
        profile_selector_frame = ctk.CTkFrame(profiles_frame)
        profile_selector_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(profile_selector_frame, text="Profil actuel:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.performance_profile = ctk.CTkComboBox(profile_selector_frame, 
                                                 values=["Économe", "Équilibré", "Performance Max", "Personnalisé"],
                                                 command=self.change_performance_profile)
        self.performance_profile.pack(side='left', padx=10)
        self.performance_profile.set("Équilibré")
        
        # Auto-détection recommandée
        auto_detect_frame = ctk.CTkFrame(profiles_frame)
        auto_detect_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        self.auto_detect_btn = ctk.CTkButton(auto_detect_frame, text="🔍 Détecter optimal", 
                                           command=self.auto_detect_performance, width=150)
        self.auto_detect_btn.pack(side='left', padx=10, pady=10)
        
        self.system_info_label = ctk.CTkLabel(auto_detect_frame, text="", 
                                            font=ctk.CTkFont(size=11), text_color="gray")
        self.system_info_label.pack(side='left', padx=20, pady=10)
        
        # === MÉTRIQUES SYSTÈME ===
        system_frame = ctk.CTkFrame(perf_container)
        system_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(system_frame, text="💻 Utilisation Système", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
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
        self.ram_usage_label = ctk.CTkLabel(ram_metric_frame, text="0%", font=ctk.CTkFont(size=16, weight="bold"))
        self.ram_usage_label.pack(pady=5)
        
        # GPU
        gpu_metric_frame = ctk.CTkFrame(metrics_grid)
        gpu_metric_frame.pack(side='left', fill='x', expand=True, padx=(5, 0))
        ctk.CTkLabel(gpu_metric_frame, text="GPU", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.gpu_usage_label = ctk.CTkLabel(gpu_metric_frame, text="N/A", font=ctk.CTkFont(size=16, weight="bold"))
        self.gpu_usage_label.pack(pady=5)
        
        # === LIMITES PERSONNALISÉES ===
        custom_limits_frame = ctk.CTkFrame(perf_container)
        custom_limits_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(custom_limits_frame, text="🎛️ Limites Personnalisées", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # CPU Limit
        cpu_limit_frame = ctk.CTkFrame(custom_limits_frame)
        cpu_limit_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(cpu_limit_frame, text="Limite CPU:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.cpu_limit_slider = ctk.CTkSlider(cpu_limit_frame, from_=10, to=100, command=self.update_cpu_limit)
        self.cpu_limit_slider.pack(side='left', padx=10, fill='x', expand=True)
        self.cpu_limit_slider.set(80)
        
        self.cpu_limit_label = ctk.CTkLabel(cpu_limit_frame, text="80%", font=ctk.CTkFont(weight="bold"))
        self.cpu_limit_label.pack(side='left', padx=10)
        
        # RAM Limit
        ram_limit_frame = ctk.CTkFrame(custom_limits_frame)
        ram_limit_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(ram_limit_frame, text="Limite RAM:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(10, 20))
        self.ram_limit_slider = ctk.CTkSlider(ram_limit_frame, from_=10, to=95, command=self.update_ram_limit)
        self.ram_limit_slider.pack(side='left', padx=10, fill='x', expand=True)
        self.ram_limit_slider.set(70)
        
        self.ram_limit_label = ctk.CTkLabel(ram_limit_frame, text="70%", font=ctk.CTkFont(weight="bold"))
        self.ram_limit_label.pack(side='left', padx=10)
        
        # GPU Settings
        gpu_settings_frame = ctk.CTkFrame(custom_limits_frame)
        gpu_settings_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.gpu_enabled_checkbox = ctk.CTkCheckBox(gpu_settings_frame, text="Activer GPU (si disponible)",
                                                   command=self.toggle_gpu_enabled)
        self.gpu_enabled_checkbox.pack(side='left', padx=10, pady=10)
        
        self.gpu_memory_slider = ctk.CTkSlider(gpu_settings_frame, from_=10, to=95, command=self.update_gpu_memory)
        self.gpu_memory_slider.pack(side='left', padx=10, fill='x', expand=True)
        self.gpu_memory_slider.set(60)
        
        self.gpu_memory_label = ctk.CTkLabel(gpu_settings_frame, text="60% VRAM", font=ctk.CTkFont(weight="bold"))
        self.gpu_memory_label.pack(side='left', padx=10)
        
        # Boutons d'action
        actions_frame = ctk.CTkFrame(custom_limits_frame)
        actions_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        self.apply_limits_btn = ctk.CTkButton(actions_frame, text="✅ Appliquer limites", 
                                            command=self.apply_custom_limits, width=150)
        self.apply_limits_btn.pack(side='left', padx=10, pady=10)
        
        self.reset_limits_btn = ctk.CTkButton(actions_frame, text="🔄 Réinitialiser", 
                                            command=self.reset_to_recommended, width=130)
        self.reset_limits_btn.pack(side='left', padx=10, pady=10)
        
        self.save_profile_btn = ctk.CTkButton(actions_frame, text="💾 Sauvegarder profil", 
                                            command=self.save_custom_profile, width=160)
        self.save_profile_btn.pack(side='left', padx=10, pady=10)
        ctk.CTkLabel(ram_metric_frame, text="RAM", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.ram_usage_label = ctk.CTkLabel(ram_metric_frame, text="0 GB", font=ctk.CTkFont(size=16, weight="bold"))
        self.ram_usage_label.pack(pady=5)
        
        # GPU (si disponible avec PyTorch)
        gpu_metric_frame = ctk.CTkFrame(metrics_grid)
        gpu_metric_frame.pack(side='right', fill='x', expand=True, padx=(10, 0))
        ctk.CTkLabel(gpu_metric_frame, text="GPU*", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.gpu_usage_label = ctk.CTkLabel(gpu_metric_frame, text="N/A", font=ctk.CTkFont(size=16, weight="bold"))
        self.gpu_usage_label.pack(pady=5)
        
        # Note pour GPU
        ctk.CTkLabel(gpu_metric_frame, text="*PyTorch requis", 
                    font=ctk.CTkFont(size=8), text_color="gray").pack()
        
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
        
        # Logo principal avec support des nouveaux assets
        try:
            from PIL import Image
            import os
            
            # Chemins des logos par ordre de préférence
            logo_paths = [
                "assets/RTPA_Studio_logo_1757286600683.png",
                "attached_assets/RTPA_Studio_logo_1757286600683.png",
                "attached_assets/RTPA_Studio_logo_1757285479377.png"
            ]
            
            logo_loaded = False
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    logo_image = Image.open(logo_path)
                    logo_image = logo_image.resize((300, 90), Image.Resampling.LANCZOS)
                    self.version_logo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(300, 90))
                    logo_label = ctk.CTkLabel(version_container, image=self.version_logo, text="")
                    logo_label.pack(pady=(40, 20))
                    logo_loaded = True
                    break
                    
            if not logo_loaded:
                # Essayer avec l'icône si pas de logo complet
                icon_paths = [
                    "assets/RTPA_Studio_icon_1024_1757286600683.png",
                    "attached_assets/RTPA_Studio_icon_1024_1757286600683.png"
                ]
                
                for icon_path in icon_paths:
                    if os.path.exists(icon_path):
                        icon_image = Image.open(icon_path)
                        icon_image = icon_image.resize((80, 80), Image.Resampling.LANCZOS)
                        self.version_icon = ctk.CTkImage(light_image=icon_image, dark_image=icon_image, size=(80, 80))
                        
                        # Container pour icône + titre
                        icon_title_frame = ctk.CTkFrame(version_container, fg_color="transparent")
                        icon_title_frame.pack(pady=(30, 10))
                        
                        icon_label = ctk.CTkLabel(icon_title_frame, image=self.version_icon, text="")
                        icon_label.pack(pady=(10, 5))
                        
                        ctk.CTkLabel(icon_title_frame, text="RTPA Studio", 
                                    font=ctk.CTkFont(size=28, weight="bold")).pack()
                        logo_loaded = True
                        break
                
                if not logo_loaded:
                    raise FileNotFoundError("Aucun logo trouvé")
                        
        except Exception as e:
            # Fallback texte si aucune image trouvée
            ctk.CTkLabel(version_container, text="RTPA Studio", 
                        font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(40, 10))
        
        ctk.CTkLabel(version_container, text="Real-Time Poker Assistant", 
                    font=ctk.CTkFont(size=18), text_color="gray").pack(pady=(0, 30))
        
        # Informations de version
        version_info_frame = ctk.CTkFrame(version_container)
        version_info_frame.pack(pady=(20, 30))
        
        ctk.CTkLabel(version_info_frame, text="Version 1.1.0", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(version_info_frame, text="Version stable", 
                    font=ctk.CTkFont(size=14, weight="bold"), text_color="#00b300").pack(pady=(0, 20))
        
        # Statut de mise à jour
        self.update_status_label = ctk.CTkLabel(version_container, text="✅ Logiciel à jour", 
                                               font=ctk.CTkFont(size=14, weight="bold"), 
                                               text_color="#00b300")
        self.update_status_label.pack(pady=(20, 15))
        
        # Container pour les boutons de mise à jour
        update_buttons_frame = ctk.CTkFrame(version_container, fg_color="transparent")
        update_buttons_frame.pack(pady=(10, 20))
        
        # Bouton vérification mise à jour
        self.check_update_btn = ctk.CTkButton(update_buttons_frame, 
                                             text="🔄 Vérifier les mises à jour",
                                             command=self.check_for_updates,
                                             width=200)
        self.check_update_btn.pack(pady=(0, 10))
        
        # Bouton installation (caché par défaut)
        self.install_update_btn = ctk.CTkButton(update_buttons_frame,
                                               text="📥 Installer la mise à jour",
                                               command=self.install_update,
                                               width=200,
                                               fg_color="#ff6b35")
        # Le bouton d'installation sera affiché seulement si une mise à jour est disponible
        
        # Copyright
        ctk.CTkLabel(version_container, text="© 2025 RTPA Studio - Tous droits réservés", 
                    font=ctk.CTkFont(size=10), text_color="gray").pack(side='bottom', pady=(30, 20))
    
    def check_for_updates(self):
        """Vérifie les mises à jour disponibles"""
        try:
            self.update_status_label.configure(text="🔄 Vérification en cours...", text_color="orange")
            self.check_update_btn.configure(state="disabled")
            
            # Thread pour éviter de bloquer l'interface
            import threading
            thread = threading.Thread(target=self._check_updates_worker, daemon=True)
            thread.start()
            
        except Exception as e:
            self.update_status_label.configure(text="❌ Erreur lors de la vérification", text_color="red")
            self.check_update_btn.configure(state="normal")
    
    def _check_updates_worker(self):
        """Worker thread pour vérification des mises à jour"""
        try:
            import time
            # Simulation de vérification
            time.sleep(2)
            
            # Pour l'instant, toujours à jour (pas de serveur de mise à jour configuré)
            self.root.after(0, lambda: self.update_status_label.configure(
                text="✅ Logiciel à jour", text_color="#00b300"
            ))
            self.root.after(0, lambda: self.check_update_btn.configure(state="normal"))
            
        except Exception as e:
            self.root.after(0, lambda: self.update_status_label.configure(
                text="❌ Erreur de vérification", text_color="red"
            ))
            self.root.after(0, lambda: self.check_update_btn.configure(state="normal"))
    
    def install_update(self):
        """Lance l'installation d'une mise à jour"""
        try:
            import tkinter.messagebox as msgbox
            result = msgbox.askyesno(
                "Mise à jour", 
                "Une nouvelle version est disponible.\n\nVoulez-vous l'installer maintenant?"
            )
            
            if result:
                self.install_update_btn.configure(state="disabled", text="Installation...")
                # Code d'installation ici
                pass
                
        except Exception as e:
            print(f"Erreur installation mise à jour: {e}")
    
    def on_platform_detected(self, platform_name):
        """Callback quand une plateforme poker est détectée"""
        try:
            if hasattr(self, 'activity_status_label'):
                # Mapping des noms de plateformes pour affichage
                platform_names = {
                    'winamax': 'Winamax',
                    'pokerstars': 'PokerStars', 
                    'pmu': 'PMU Poker',
                    'partypoker': 'PartyPoker',
                    'unibet': 'Unibet Poker'
                }
                display_name = platform_names.get(platform_name.lower(), platform_name)
                
                self.activity_status_label.configure(
                    text=f"🟢 Connecté à {display_name}",
                    text_color="#00b300"
                )
        except Exception as e:
            print(f"Erreur callback platform detected: {e}")
    
    def update_connection_status(self, connected, platform=None):
        """Met à jour le statut de connexion"""
        try:
            if hasattr(self, 'activity_status_label'):
                if connected and platform:
                    # Mapping des noms de plateformes pour affichage
                    platform_names = {
                        'winamax': 'Winamax',
                        'pokerstars': 'PokerStars', 
                        'pmu': 'PMU Poker',
                        'partypoker': 'PartyPoker',
                        'unibet': 'Unibet Poker'
                    }
                    display_name = platform_names.get(platform.lower(), platform)
                    
                    self.activity_status_label.configure(
                        text=f"🟢 Connecté à {display_name}",
                        text_color="#00b300"
                    )
                elif connected:
                    # Surveillance active mais aucune plateforme détectée - reste orange
                    self.activity_status_label.configure(
                        text="🟠 Surveillance active",
                        text_color="#ff8c00"
                    )
                else:
                    # Surveillance arrêtée ou en attente - orange/gris
                    self.activity_status_label.configure(
                        text="🟠 Surveillance active",
                        text_color="#ff8c00"
                    )
        except Exception as e:
            print(f"Erreur update connection status: {e}")
    
    def install_pytorch(self):
        """Lance l'installation de PyTorch"""
        try:
            self.install_pytorch_btn.configure(state="disabled", text="Installation...")
            self.pytorch_progress.pack(pady=(10, 5))
            self.pytorch_progress.set(0)
            self.pytorch_status_label.configure(text="Téléchargement de PyTorch...", text_color="orange")
            
            import threading
            install_thread = threading.Thread(target=self._install_pytorch_worker, daemon=True)
            install_thread.start()
            
        except Exception as e:
            self.pytorch_status_label.configure(text=f"Erreur: {e}", text_color="red")
            self.install_pytorch_btn.configure(state="normal", text="🔥 Installer PyTorch")
    
    def _install_pytorch_worker(self):
        """Worker thread pour l'installation PyTorch"""
        try:
            import subprocess
            import sys
            
            # Mise à jour de la progress bar
            self.root.after(100, lambda: self.pytorch_progress.set(0.2))
            self.root.after(100, lambda: self.pytorch_status_label.configure(text="Installation en cours...", text_color="orange"))
            
            # Installation PyTorch
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "torch", "torchvision", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cpu"
            ], capture_output=True, text=True, timeout=300)
            
            self.root.after(100, lambda: self.pytorch_progress.set(0.8))
            
            if result.returncode == 0:
                self.root.after(100, lambda: self.pytorch_progress.set(1.0))
                self.root.after(200, lambda: self.pytorch_status_label.configure(text="✅ PyTorch installé avec succès!", text_color="green"))
                self.root.after(300, lambda: self.install_pytorch_btn.configure(text="✅ Installé", state="disabled"))
            else:
                raise Exception(f"Erreur installation: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.root.after(100, lambda: self.pytorch_status_label.configure(text="Timeout - Installation trop longue", text_color="red"))
        except Exception as e:
            self.root.after(100, lambda: self.pytorch_status_label.configure(text=f"❌ Erreur: {str(e)[:50]}...", text_color="red"))
            self.root.after(100, lambda: self.install_pytorch_btn.configure(state="normal", text="🔥 Installer PyTorch"))
    
    def update_task_display(self, task_name, time_info=None):
        """Met à jour l'affichage de la tâche en cours"""
        try:
            if hasattr(self, 'current_task_label'):
                self.current_task_label.configure(text=task_name)
            
            if time_info and hasattr(self, 'task_time_label'):
                if isinstance(time_info, str):
                    # Texte formaté directement
                    self.task_time_label.configure(text=time_info)
                elif isinstance(time_info, (int, float)):
                    # Fallback pour compatibilité (nombre de secondes)
                    if time_info > 60:
                        time_text = f"Temps restant: {time_info/60:.1f} min"
                    else:
                        time_text = f"Temps restant: {time_info:.0f}s"
                    self.task_time_label.configure(text=time_text)
                else:
                    self.task_time_label.configure(text=str(time_info))
            elif hasattr(self, 'task_time_label'):
                self.task_time_label.configure(text="")
        except Exception as e:
            print(f"Erreur mise à jour tâche: {e}")
    
    def update_cfr_progress(self):
        """Met à jour la progression de la tâche principale en temps réel"""
        try:
            # Vérifier s'il y a une tâche CFR en cours
            if hasattr(self, 'app_manager') and self.app_manager and hasattr(self.app_manager, 'cfr_engine'):
                cfr_engine = self.app_manager.cfr_engine
                
                # Priorité 1: Génération de mains synthétiques en cours
                if hasattr(cfr_engine, 'cfr_trainer') and cfr_engine.cfr_trainer:
                    trainer = cfr_engine.cfr_trainer
                    
                    # Vérifier génération de mains synthétiques
                    if hasattr(trainer, 'generation_active') and getattr(trainer, 'generation_active', False):
                        generated = getattr(trainer, 'hands_generated', 0)
                        target_gen = getattr(trainer, 'target_hands', 200000)
                        
                        if target_gen > 0:
                            progress = min(100.0, (generated / target_gen) * 100)
                            task_text = f"🔄 Génération de mains synthétiques ({generated:,}/{target_gen:,})"
                            
                            if hasattr(self, 'main_task_label'):
                                self.main_task_label.configure(text=task_text, text_color="#ff8c00")
                            
                            if hasattr(self, 'task_progress_bar'):
                                self.task_progress_bar.set(progress / 100.0)
                            
                            if hasattr(self, 'task_detail_label'):
                                self.task_detail_label.configure(text=f"Progression: {progress:.1f}% - {generated:,} mains générées")
                            
                            self.root.after(500, self.update_cfr_progress)  # Mise à jour rapide
                            return
                    
                    # Priorité 2: Entraînement CFR intensif - Utiliser get_training_progress()
                    try:
                        progress_info = cfr_engine.get_training_progress()
                        if progress_info.get('training_active', False):
                            iterations = progress_info.get('iterations', 0)
                            target = progress_info.get('target_iterations', 100000)
                        
                        if target > 0:
                            progress = min(100.0, (iterations / target) * 100)
                            task_text = f"⚡ Calculs Nash/CFR en cours ({iterations:,}/{target:,} itérations)"
                            
                            # Calculer le temps restant
                            time_str = "Calcul..."
                            if hasattr(trainer, 'training_start_time') and iterations > 50:
                                import time
                                elapsed = time.time() - trainer.training_start_time
                                if elapsed > 0 and iterations > 0:
                                    rate = iterations / elapsed  # itérations par seconde
                                    remaining_iterations = max(0, target - iterations)
                                    remaining_seconds = remaining_iterations / rate if rate > 0 else 0
                                    
                                    # Formatage du temps
                                    if remaining_seconds > 3600:
                                        hours = int(remaining_seconds // 3600)
                                        minutes = int((remaining_seconds % 3600) // 60)
                                        time_str = f"{hours}h{minutes:02d}m"
                                    elif remaining_seconds > 60:
                                        minutes = int(remaining_seconds // 60)
                                        seconds = int(remaining_seconds % 60)
                                        time_str = f"{minutes}m{seconds:02d}s"
                                    else:
                                        time_str = f"{int(remaining_seconds)}s"
                            
                            # Affichage unifié de la tâche CFR
                            task_text = f"Calcul CFR: {progress:.1f}% ({iterations:,}/{target:,}) - Reste: {time_str}"
                            
                            # Mettre à jour l'interface
                            if hasattr(self, 'main_task_label'):
                                self.main_task_label.configure(text=task_text, text_color="#00b300")
                            
                            if hasattr(self, 'task_progress_bar'):
                                self.task_progress_bar.set(progress / 100.0)
                            
                            if hasattr(self, 'task_detail_label'):
                                detail_text = f"Progression: {progress:.1f}% - Convergence Nash en cours"
                                if hasattr(trainer, 'training_start_time'):
                                    import time
                                    elapsed = time.time() - trainer.training_start_time
                                    detail_text += f" | Temps écoulé: {int(elapsed//60)}m{int(elapsed%60):02d}s"
                                self.task_detail_label.configure(text=detail_text)
                            
                            # Programmer la prochaine mise à jour
                            self.root.after(1000, self.update_cfr_progress)  # Mise à jour chaque seconde
                            return
                    except Exception as e:
                        print(f"Erreur récupération training progress: {e}")
                    
                    # Vérifier s'il y a une génération de mains en cours
                    elif hasattr(trainer, 'is_generating') and getattr(trainer, 'is_generating', False):
                        # Génération en cours
                        generated = getattr(trainer, 'hands_generated', 0)
                        target_gen = getattr(trainer, 'target_hands', 200000)
                        
                        if target_gen > 0:
                            progress = min(100.0, (generated / target_gen) * 100)
                            
                            task_text = f"Génération mains: {progress:.1f}% ({generated:,}/{target_gen:,})"
                            
                            if hasattr(self, 'main_task_label'):
                                self.main_task_label.configure(text=task_text, text_color="#ff8c00")
                            
                            if hasattr(self, 'task_progress_bar'):
                                self.task_progress_bar.set(progress / 100.0)
                            
                            if hasattr(self, 'task_detail_label'):
                                self.task_detail_label.configure(text=f"Mains générées: {generated:,} sur {target_gen:,}")
                            
                            self.root.after(1000, self.update_cfr_progress)
                            return
            
            # Aucune tâche en cours - affichage par défaut
            # Priorité 3: Génération continue en cours
            if hasattr(cfr_engine, 'cfr_trainer') and cfr_engine.cfr_trainer and hasattr(cfr_engine.cfr_trainer, 'continuous_generator'):
                cont_gen = cfr_engine.cfr_trainer.continuous_generator
                if hasattr(cont_gen, 'running') and getattr(cont_gen, 'running', False):
                    hands_per_min = getattr(cont_gen, 'current_rate', 450)
                    
                    if hasattr(self, 'main_task_label'):
                        self.main_task_label.configure(text=f"🔄 Génération continue active ({hands_per_min} mains/min)", text_color="#00b300")
                    
                    if hasattr(self, 'task_progress_bar'):
                        # Animation pour génération continue
                        current_time = time.time() if 'time' in globals() else 0
                        animation_progress = (current_time % 2) / 2  # Animation de 2 secondes
                        self.task_progress_bar.set(animation_progress)
                    
                    if hasattr(self, 'task_detail_label'):
                        self.task_detail_label.configure(text="Amélioration continue des stratégies Nash")
                    
                    self.root.after(1000, self.update_cfr_progress)
                    return
            
            # Aucune tâche active
            if hasattr(self, 'main_task_label'):
                self.main_task_label.configure(text="🎯 Système prêt", text_color="#666666")
            
            if hasattr(self, 'task_progress_bar'):
                self.task_progress_bar.set(0)
            
            if hasattr(self, 'task_detail_label'):
                self.task_detail_label.configure(text="En attente de détection de plateforme poker")
            
            # Programmer la prochaine vérification
            self.root.after(2000, self.update_cfr_progress)
            
        except Exception as e:
            print(f"Erreur update progress: {e}")
            # Reprogram même en cas d'erreur
            self.root.after(5000, self.update_cfr_progress)
    
    def change_ocr_platform(self, selected_platform):
        """Change la plateforme OCR et charge les préréglages correspondants"""
        try:
            platform_mapping = {
                "PokerStars": "pokerstars",
                "Winamax": "winamax", 
                "PMU": "pmu",
                "PartyPoker": "partypoker"
            }
            
            internal_name = platform_mapping.get(selected_platform, "pokerstars")
            
            # Charger automatiquement le preset
            self.load_ocr_preset_for_platform(internal_name)
            print(f"✅ Plateforme OCR changée: {selected_platform}")
            
        except Exception as e:
            print(f"Erreur changement plateforme OCR: {e}")
    
    def load_ocr_preset_for_platform(self, platform_name):
        """Charge les préréglages OCR pour une plateforme donnée"""
        try:
            # Importer les préréglages depuis screen_capture
            from src.ocr.screen_capture import ScreenCapture
            ocr = ScreenCapture()
            
            if platform_name in ocr.roi_presets:
                preset = ocr.roi_presets[platform_name]
                
                # Remplir tous les champs avec les valeurs du preset
                for zone_key, coords in preset.items():
                    if zone_key in self.ocr_zone_entries:
                        self.ocr_zone_entries[zone_key]['top'].delete(0, 'end')
                        self.ocr_zone_entries[zone_key]['top'].insert(0, str(coords['top']))
                        
                        self.ocr_zone_entries[zone_key]['left'].delete(0, 'end')
                        self.ocr_zone_entries[zone_key]['left'].insert(0, str(coords['left']))
                        
                        self.ocr_zone_entries[zone_key]['width'].delete(0, 'end')
                        self.ocr_zone_entries[zone_key]['width'].insert(0, str(coords['width']))
                        
                        self.ocr_zone_entries[zone_key]['height'].delete(0, 'end')
                        self.ocr_zone_entries[zone_key]['height'].insert(0, str(coords['height']))
                
                print(f"✅ Preset {platform_name} chargé dans l'interface")
            else:
                print(f"⚠️ Aucun preset trouvé pour {platform_name}")
                
        except Exception as e:
            print(f"Erreur chargement preset: {e}")
    
    def load_ocr_preset(self):
        """Charge le preset pour la plateforme sélectionnée"""
        try:
            selected_platform = self.platform_selector.get()
            platform_mapping = {
                "PokerStars": "pokerstars",
                "Winamax": "winamax", 
                "PMU": "pmu",
                "PartyPoker": "partypoker"
            }
            
            internal_name = platform_mapping.get(selected_platform, "pokerstars")
            self.load_ocr_preset_for_platform(internal_name)
            
        except Exception as e:
            print(f"Erreur load preset: {e}")
    
    def apply_ocr_calibration(self):
        """Applique la calibration OCR avec les nouvelles coordonnées"""
        try:
            # Récupérer toutes les valeurs des champs
            new_zones = {}
            
            for zone_key, entries in self.ocr_zone_entries.items():
                try:
                    new_zones[zone_key] = {
                        'top': int(entries['top'].get() or 0),
                        'left': int(entries['left'].get() or 0),
                        'width': int(entries['width'].get() or 0),
                        'height': int(entries['height'].get() or 0)
                    }
                except ValueError:
                    print(f"⚠️ Valeur invalide pour {zone_key}, utilisation des défauts")
                    continue
            
            # Appliquer au système OCR si disponible
            if hasattr(self, 'app_manager') and self.app_manager:
                if hasattr(self.app_manager, 'screen_capture') and self.app_manager.screen_capture:
                    # Mettre à jour les zones OCR
                    self.app_manager.screen_capture.roi_zones.update(new_zones)
                    print(f"✅ Calibration OCR appliquée: {len(new_zones)} zones mises à jour")
                else:
                    print("⚠️ Module de capture d'écran non disponible")
            
            # Sauvegarder la configuration
            self.save_ocr_configuration(new_zones)
            
        except Exception as e:
            print(f"Erreur application calibration: {e}")
    
    def save_ocr_configuration(self, zones_config):
        """Sauvegarde la configuration OCR"""
        try:
            import json
            import os
            
            config_path = "config/ocr_calibration.json"
            os.makedirs("config", exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(zones_config, f, indent=2)
                
            print(f"✅ Configuration OCR sauvegardée: {config_path}")
            
        except Exception as e:
            print(f"Erreur sauvegarde configuration OCR: {e}")
    
    def test_ocr_zones(self):
        """Teste les zones OCR configurées"""
        try:
            if hasattr(self, 'app_manager') and self.app_manager:
                if hasattr(self.app_manager, 'screen_capture') and self.app_manager.screen_capture:
                    # Test simple des zones
                    capture = self.app_manager.screen_capture
                    
                    # Capturer une image test
                    test_img = capture.capture_screen_region()
                    
                    if test_img is not None:
                        print("✅ Test OCR réussi - Capture d'écran fonctionnelle")
                        
                        # Tester quelques zones
                        test_zones = ['hero_cards', 'board_cards', 'pot_size']
                        for zone in test_zones:
                            if zone in capture.roi_zones:
                                coords = capture.roi_zones[zone]
                                print(f"  • {zone}: {coords['width']}x{coords['height']} à ({coords['left']}, {coords['top']})")
                        
                        print("🔍 Test terminé - Vérifiez la console pour les détails")
                    else:
                        print("❌ Échec capture d'écran - Vérifiez la configuration")
                else:
                    print("⚠️ Module OCR non disponible pour test")
            else:
                print("⚠️ Gestionnaire d'application non disponible")
                
        except Exception as e:
            print(f"Erreur test OCR: {e}")
    
    def auto_calibrate_ocr(self):
        """Recalibrage automatique basé sur la détection de plateforme"""
        try:
            print("🤖 Démarrage du recalibrage automatique...")
            
            # Vérifier si une plateforme est détectée
            if hasattr(self, 'app_manager') and self.app_manager:
                if hasattr(self.app_manager, 'platform_detector') and self.app_manager.platform_detector:
                    detector = self.app_manager.platform_detector
                    
                    # Forcer une détection
                    detection_result = detector.force_detection()
                    
                    if detection_result and detection_result.get('count', 0) > 0:
                        # Plateforme détectée - utiliser le preset correspondant
                        detected_platforms = detection_result.get('platforms', [])
                        if detected_platforms:
                            platform_name = detected_platforms[0]  # Première plateforme détectée
                            
                            # Mapper vers nos noms internes
                            platform_mapping = {
                                'pokerstars': 'PokerStars',
                                'winamax': 'Winamax',
                                'pmu': 'PMU',
                                'partypoker': 'PartyPoker'
                            }
                            
                            display_name = platform_mapping.get(platform_name, 'PokerStars')
                            
                            # Mettre à jour le sélecteur
                            self.platform_selector.set(display_name)
                            
                            # Charger automatiquement le preset
                            self.load_ocr_preset_for_platform(platform_name)
                            
                            # Appliquer automatiquement
                            self.apply_ocr_calibration()
                            
                            print(f"✅ Recalibrage automatique terminé pour {display_name}")
                            return
                
                # Aucune plateforme détectée - utiliser la plateforme sélectionnée
                selected_platform = self.platform_selector.get()
                platform_mapping = {
                    "PokerStars": "pokerstars",
                    "Winamax": "winamax", 
                    "PMU": "pmu",
                    "PartyPoker": "partypoker"
                }
                
                internal_name = platform_mapping.get(selected_platform, "pokerstars")
                
                # Charger le preset de base
                self.load_ocr_preset_for_platform(internal_name)
                
                # Appliquer automatiquement
                self.apply_ocr_calibration()
                
                print(f"✅ Recalibrage automatique appliqué pour {selected_platform}")
            
            else:
                print("⚠️ Gestionnaire d'application non disponible pour auto-calibrage")
                
        except Exception as e:
            print(f"Erreur auto-calibrage: {e}")
    
    def load_ocr_configuration(self):
        """Charge la configuration OCR sauvegardée"""
        try:
            import json
            import os
            
            config_path = "config/ocr_calibration.json"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    zones_config = json.load(f)
                
                # Appliquer la configuration aux champs de l'interface
                for zone_key, coords in zones_config.items():
                    if hasattr(self, 'ocr_zone_entries') and zone_key in self.ocr_zone_entries:
                        self.ocr_zone_entries[zone_key]['top'].delete(0, 'end')
                        self.ocr_zone_entries[zone_key]['top'].insert(0, str(coords['top']))
                        
                        self.ocr_zone_entries[zone_key]['left'].delete(0, 'end')
                        self.ocr_zone_entries[zone_key]['left'].insert(0, str(coords['left']))
                        
                        self.ocr_zone_entries[zone_key]['width'].delete(0, 'end')
                        self.ocr_zone_entries[zone_key]['width'].insert(0, str(coords['width']))
                        
                        self.ocr_zone_entries[zone_key]['height'].delete(0, 'end')
                        self.ocr_zone_entries[zone_key]['height'].insert(0, str(coords['height']))
                
                print(f"✅ Configuration OCR chargée: {config_path}")
                
        except Exception as e:
            print(f"Info: Aucune configuration OCR sauvegardée ({e})")
    
    def change_performance_profile(self, profile_name):
        """Change le profil de performance"""
        try:
            if not self.system_optimizer:
                return
            
            profile_mapping = {
                "Économe": "econome",
                "Équilibré": "equilibre", 
                "Performance Max": "performance_max",
                "Personnalisé": "custom"
            }
            
            internal_name = profile_mapping.get(profile_name, "equilibre")
            success = self.system_optimizer.set_profile(internal_name)
            
            if success:
                # Mettre à jour l'interface avec les nouvelles limites
                limits = self.system_optimizer.get_current_limits()
                self.cpu_limit_slider.set(limits.cpu_percent)
                self.ram_limit_slider.set(limits.ram_percent)
                self.gpu_memory_slider.set(limits.gpu_memory_percent)
                
                if limits.gpu_enabled:
                    self.gpu_enabled_checkbox.select()
                else:
                    self.gpu_enabled_checkbox.deselect()
                
                # Mettre à jour les labels
                self.update_cpu_limit(limits.cpu_percent)
                self.update_ram_limit(limits.ram_percent)
                self.update_gpu_memory(limits.gpu_memory_percent)
                
                self.logger.info(f"Profil de performance changé: {profile_name}")
            else:
                self.logger.error(f"Erreur changement profil: {profile_name}")
                
        except Exception as e:
            self.logger.error(f"Erreur change_performance_profile: {e}")
    
    def auto_detect_performance(self):
        """Détecte automatiquement le profil optimal"""
        try:
            if not self.system_optimizer:
                self.system_info_label.configure(text="⚠️ Optimiseur non disponible")
                return
            
            recommended = self.system_optimizer.get_recommended_profile()
            caps = self.system_optimizer.capabilities
            
            # Mapper le profil interne vers l'affichage
            profile_display = {
                "econome": "Économe",
                "equilibre": "Équilibré",
                "performance_max": "Performance Max"
            }
            
            recommended_display = profile_display.get(recommended, "Équilibré")
            self.performance_profile.set(recommended_display)
            self.change_performance_profile(recommended_display)
            
            # Afficher les informations système
            info_text = f"Détecté: {caps.cpu_cores}C/{caps.cpu_threads}T, {caps.ram_total_gb:.1f}GB RAM"
            if caps.gpu_available:
                info_text += f", GPU: {caps.gpu_name[:20]}..."
            
            self.system_info_label.configure(text=info_text)
            self.logger.info(f"Profil auto-détecté: {recommended_display}")
            
        except Exception as e:
            self.logger.error(f"Erreur auto_detect_performance: {e}")
            self.system_info_label.configure(text="❌ Erreur détection")
    
    def update_cpu_limit(self, value):
        """Met à jour la limite CPU"""
        try:
            self.cpu_limit_label.configure(text=f"{int(value)}%")
        except Exception as e:
            self.logger.error(f"Erreur update_cpu_limit: {e}")
    
    def update_ram_limit(self, value):
        """Met à jour la limite RAM"""
        try:
            self.ram_limit_label.configure(text=f"{int(value)}%")
        except Exception as e:
            self.logger.error(f"Erreur update_ram_limit: {e}")
    
    def update_gpu_memory(self, value):
        """Met à jour la limite mémoire GPU"""
        try:
            self.gpu_memory_label.configure(text=f"{int(value)}% VRAM")
        except Exception as e:
            self.logger.error(f"Erreur update_gpu_memory: {e}")
    
    def toggle_gpu_enabled(self):
        """Active/désactive le GPU"""
        try:
            enabled = self.gpu_enabled_checkbox.get()
            self.logger.info(f"GPU {'activé' if enabled else 'désactivé'}")
        except Exception as e:
            self.logger.error(f"Erreur toggle_gpu_enabled: {e}")
    
    def apply_custom_limits(self):
        """Applique les limites personnalisées"""
        try:
            if not self.system_optimizer:
                return
            
            cpu_percent = self.cpu_limit_slider.get()
            ram_percent = self.ram_limit_slider.get()
            gpu_enabled = self.gpu_enabled_checkbox.get()
            gpu_memory_percent = self.gpu_memory_slider.get()
            
            success = self.system_optimizer.set_custom_limits(
                cpu_percent, ram_percent, gpu_enabled, gpu_memory_percent
            )
            
            if success:
                self.performance_profile.set("Personnalisé")
                self.system_optimizer.set_profile("custom")
                
                # Appliquer au moteur CFR si disponible
                if hasattr(self, 'app_manager') and self.app_manager:
                    optimal_settings = self.system_optimizer.get_optimal_cfr_settings()
                    self.app_manager.update_settings(optimal_settings)
                
                self.logger.info("Limites personnalisées appliquées")
                self.system_info_label.configure(text="✅ Limites appliquées")
            else:
                self.system_info_label.configure(text="❌ Erreur application")
                
        except Exception as e:
            self.logger.error(f"Erreur apply_custom_limits: {e}")
    
    def reset_to_recommended(self):
        """Remet les paramètres recommandés"""
        try:
            if self.system_optimizer:
                self.auto_detect_performance()
                self.system_info_label.configure(text="🔄 Paramètres réinitialisés")
        except Exception as e:
            self.logger.error(f"Erreur reset_to_recommended: {e}")
    
    def save_custom_profile(self):
        """Sauvegarde le profil personnalisé"""
        try:
            if self.system_optimizer:
                success = self.system_optimizer.save_configuration()
                if success:
                    self.system_info_label.configure(text="💾 Profil sauvegardé")
                    self.logger.info("Profil personnalisé sauvegardé")
                else:
                    self.system_info_label.configure(text="❌ Erreur sauvegarde")
        except Exception as e:
            self.logger.error(f"Erreur save_custom_profile: {e}")
    
    def update_system_metrics(self):
        """Met à jour les métriques système en temps réel"""
        try:
            if self.system_optimizer:
                usage = self.system_optimizer.monitor_resource_usage()
                
                # Mettre à jour les labels d'utilisation
                self.cpu_usage_label.configure(text=f"{usage['cpu_percent']:.1f}%")
                self.ram_usage_label.configure(text=f"{usage['ram_percent']:.1f}%")
                
                if usage['gpu_usage'] > 0:
                    self.gpu_usage_label.configure(text=f"{usage['gpu_usage']:.1f}%")
                else:
                    self.gpu_usage_label.configure(text="N/A")
                
                # Couleurs selon l'utilisation
                cpu_color = "#ff4444" if usage['cpu_percent'] > 90 else "#00b300" if usage['cpu_percent'] < 70 else "#ff8c00"
                ram_color = "#ff4444" if usage['ram_percent'] > 85 else "#00b300" if usage['ram_percent'] < 60 else "#ff8c00"
                
                self.cpu_usage_label.configure(text_color=cpu_color)
                self.ram_usage_label.configure(text_color=ram_color)
                
                # Auto-ajustement si nécessaire
                adjusted = self.system_optimizer.auto_adjust_if_needed()
                if adjusted and hasattr(self, 'system_info_label'):
                    self.system_info_label.configure(text="⚠️ Auto-ajustement appliqué")
            
            # Programmer la prochaine mise à jour
            self.root.after(3000, self.update_system_metrics)  # Toutes les 3 secondes
            
        except Exception as e:
            self.logger.error(f"Erreur update_system_metrics: {e}")
            # Reprogram même en cas d'erreur
            self.root.after(5000, self.update_system_metrics)
    
    def _update_task_display_loop(self):
        """Boucle de mise à jour de l'affichage des tâches"""
        try:
            if hasattr(self, 'app_manager') and self.app_manager:
                # Obtenir les informations de tâche du CFR trainer
                if hasattr(self.app_manager, 'cfr_trainer') and self.app_manager.cfr_trainer:
                    trainer = self.app_manager.cfr_trainer
                    if hasattr(trainer, 'get_training_statistics'):
                        stats = trainer.get_training_statistics()
                        
                        if stats.get('is_training', False):
                            # Calculer et afficher le temps restant
                            iterations = stats.get('iterations', 0)
                            target = stats.get('target_iterations', 100000)
                            progress = stats.get('progress_percentage', 0)
                            time_remaining = stats.get('estimated_time_remaining', 0)
                            
                            # Nom de la tâche en cours
                            task_name = f"Entraînement CFR - Itération {iterations:,}/{target:,}"
                            
                            # Formatage du temps restant
                            if time_remaining > 0:
                                if time_remaining > 3600:  # Plus d'1 heure
                                    hours = int(time_remaining // 3600)
                                    minutes = int((time_remaining % 3600) // 60)
                                    time_text = f"Temps restant: {hours}h {minutes}min ({progress:.1f}%)"
                                elif time_remaining > 60:  # Plus d'1 minute
                                    minutes = int(time_remaining // 60)
                                    seconds = int(time_remaining % 60)
                                    time_text = f"Temps restant: {minutes}min {seconds}s ({progress:.1f}%)"
                                else:  # Moins d'1 minute
                                    time_text = f"Temps restant: {int(time_remaining)}s ({progress:.1f}%)"
                            else:
                                time_text = f"Progression: {progress:.1f}%"
                            
                            # Mise à jour de l'affichage
                            self.update_task_display(task_name, time_text)
                        else:
                            # Pas d'entraînement en cours - vérifier génération continue
                            if hasattr(self.app_manager, 'continuous_generator') and self.app_manager.continuous_generator:
                                if hasattr(self.app_manager.continuous_generator, 'is_running') and self.app_manager.continuous_generator.is_running:
                                    gen_stats = getattr(self.app_manager.continuous_generator, '_last_stats', {})
                                    hands_generated = gen_stats.get('total_generated', 0)
                                    rate = gen_stats.get('generation_rate', 0)
                                    task_name = "Génération continue de mains"
                                    time_text = f"{hands_generated:,} mains générées ({rate:.1f}/s)"
                                    self.update_task_display(task_name, time_text)
                                else:
                                    self.update_task_display("Système en attente", "Prêt pour l'analyse")
                            else:
                                self.update_task_display("Système en attente", "Prêt pour l'analyse")
                else:
                    self.update_task_display("Initialisation du système...", "Chargement des composants")
            else:
                self.update_task_display("Initialisation système...", "Chargement des composants")
            
        except Exception as e:
            print(f"Erreur loop tâche: {e}")
        
        # Programmer la prochaine mise à jour
        self.root.after(2000, self._update_task_display_loop)
    
    def toggle_probabilities_display(self):
        """Masque/affiche les probabilités de victoire"""
        try:
            show_probs = self.show_probabilities.get()
            
            # Sauvegarder le paramètre
            if hasattr(self, 'app_manager') and self.app_manager:
                self.app_manager.update_settings({'show_probabilities': show_probs})
            
            # Masquer/afficher les éléments de probabilité
            if hasattr(self, 'left_rec'):
                if show_probs:
                    self.left_rec.pack(side='left')
                else:
                    self.left_rec.pack_forget()
            
            print(f"✅ Probabilités {'affichées' if show_probs else 'masquées'}")
            
        except Exception as e:
            print(f"Erreur toggle probabilités: {e}")
    
    def toggle_recommendations_display(self):
        """Masque/affiche toute la section recommandations"""
        try:
            show_recs = self.show_recommendations.get()
            
            # Sauvegarder le paramètre
            if hasattr(self, 'app_manager') and self.app_manager:
                self.app_manager.update_settings({'show_recommendations': show_recs})
            
            # Masquer/afficher toute la frame de recommandation
            if hasattr(self, 'rec_frame'):
                if show_recs:
                    self.rec_frame.pack(fill='x', pady=(0, 10))
                else:
                    self.rec_frame.pack_forget()
            
            print(f"✅ Recommandations {'affichées' if show_recs else 'masquées'}")
            
        except Exception as e:
            print(f"Erreur toggle recommandations: {e}")
    
    def toggle_statistics_display(self):
        """Masque/affiche la colonne statistiques des joueurs"""
        try:
            show_stats = self.show_statistics.get()
            
            # Sauvegarder le paramètre
            if hasattr(self, 'app_manager') and self.app_manager:
                self.app_manager.update_settings({'show_statistics': show_stats})
            
            # Masquer/afficher la colonne droite avec les statistiques
            if hasattr(self, 'right_column'):
                if show_stats:
                    self.right_column.pack(side='right', fill='y', padx=(0, 0))
                else:
                    self.right_column.pack_forget()
            
            print(f"✅ Statistiques {'affichées' if show_stats else 'masquées'}")
            
        except Exception as e:
            print(f"Erreur toggle statistiques: {e}")
    
    def load_display_settings(self):
        """Charge les paramètres d'affichage depuis les settings"""
        try:
            if hasattr(self, 'app_manager') and self.app_manager and hasattr(self.app_manager, 'settings'):
                settings = self.app_manager.settings
                
                # Charger et appliquer les paramètres d'affichage
                show_probs = getattr(settings, 'show_probabilities', True)
                show_recs = getattr(settings, 'show_recommendations', True)  
                show_stats = getattr(settings, 'show_statistics', True)
                
                # Mettre à jour les checkboxes
                if hasattr(self, 'show_probabilities'):
                    if show_probs:
                        self.show_probabilities.select()
                    else:
                        self.show_probabilities.deselect()
                        
                if hasattr(self, 'show_recommendations'):
                    if show_recs:
                        self.show_recommendations.select()
                    else:
                        self.show_recommendations.deselect()
                        
                if hasattr(self, 'show_statistics'):
                    if show_stats:
                        self.show_statistics.select()
                    else:
                        self.show_statistics.deselect()
                
                # Appliquer l'état initial
                self.toggle_probabilities_display()
                self.toggle_recommendations_display()
                self.toggle_statistics_display()
                
                print("✅ Paramètres d'affichage chargés")
        
        except Exception as e:
            print(f"Erreur chargement paramètres d'affichage: {e}")
    
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
    
    def _init_performance_profiles(self):
        """Initialise les profils de performance"""
        try:
            from src.config.performance_profiles import get_performance_manager
            
            self.profile_manager = get_performance_manager()
            current_profile_name = self.profile_manager.current_profile
            
            # Mapping des noms de profils
            profile_display_names = {
                "eco": "💚 Éco",
                "equilibre": "⚖️ Équilibré", 
                "performance": "🚀 Performance"
            }
            
            # Définir la valeur par défaut
            display_name = profile_display_names.get(current_profile_name, "⚖️ Équilibré")
            self.performance_profile_dropdown.set(display_name)
            
            # Mettre à jour la description
            self._update_profile_description(current_profile_name)
            
        except Exception as e:
            print(f"Erreur initialisation profils: {e}")
    
    def _load_current_profile(self):
        """Charge le profil actuel au démarrage"""
        try:
            from src.config.performance_profiles import get_performance_manager
            
            profile_manager = get_performance_manager()
            current_profile = profile_manager.get_current_profile()
            
            # Appliquer les paramètres aux sliders si l'interface est créée
            self.after(1000, lambda: self._apply_profile_to_interface(current_profile))
            
        except Exception as e:
            print(f"Erreur chargement profil: {e}")
    
    def on_profile_changed(self, selected_value):
        """Appelé quand l'utilisateur change de profil"""
        try:
            # Mapping inverse
            profile_names = {
                "💚 Éco": "eco",
                "⚖️ Équilibré": "equilibre",
                "🚀 Performance": "performance"
            }
            
            profile_name = profile_names.get(selected_value, "equilibre")
            self._update_profile_description(profile_name)
            
            # Indiquer qu'un changement est en attente
            if hasattr(self, 'profile_status_label') and self.profile_status_label:
                self.profile_status_label.configure(text="⏳ Changement en attente...", text_color="orange")
            
        except Exception as e:
            print(f"Erreur changement profil: {e}")
    
    def _update_profile_description(self, profile_name):
        """Met à jour la description du profil sélectionné"""
        try:
            from src.config.performance_profiles import get_performance_manager
            
            profile_manager = get_performance_manager()
            profile = profile_manager.get_profile(profile_name)
            
            if hasattr(self, 'profile_description_label') and self.profile_description_label:
                self.profile_description_label.configure(text=profile.description)
            
        except Exception as e:
            print(f"Erreur description profil: {e}")
    
    def apply_selected_profile(self):
        """Applique le profil sélectionné"""
        try:
            from src.config.performance_profiles import get_performance_manager
            
            # Récupérer le profil sélectionné
            selected_display = self.performance_profile_dropdown.get()
            profile_names = {
                "💚 Éco": "eco",
                "⚖️ Équilibré": "equilibre", 
                "🚀 Performance": "performance"
            }
            
            profile_name = profile_names.get(selected_display, "equilibre")
            
            # Appliquer le profil
            profile_manager = get_performance_manager()
            success = profile_manager.set_current_profile(profile_name)
            
            if success:
                profile = profile_manager.get_current_profile()
                
                # Appliquer à l'interface
                self._apply_profile_to_interface(profile)
                
                # Appliquer au moteur CFR si disponible
                if hasattr(self, 'app_manager') and self.app_manager:
                    self.app_manager.cfr_engine._apply_performance_profile(profile)
                
                # Redémarrer les processus selon le nouveau profil
                self._restart_cfr_with_profile(profile)
                
                if hasattr(self, 'profile_status_label') and self.profile_status_label:
                    self.profile_status_label.configure(
                        text=f"✅ Profil {profile.name} appliqué", 
                        text_color="#00b300"
                    )
                    
                    # Effacer le message après 3 secondes
                    self.after(3000, lambda: self.profile_status_label.configure(text=""))
                
            else:
                if hasattr(self, 'profile_status_label') and self.profile_status_label:
                    self.profile_status_label.configure(
                        text="❌ Erreur application", 
                        text_color="red"
                    )
        
        except Exception as e:
            print(f"Erreur application profil: {e}")
            if hasattr(self, 'profile_status_label') and self.profile_status_label:
                self.profile_status_label.configure(
                    text="❌ Erreur application", 
                    text_color="red"
                )
    
    def _apply_profile_to_interface(self, profile):
        """Applique les paramètres du profil aux éléments de l'interface"""
        try:
            # Appliquer aux sliders CPU/RAM si ils existent
            if hasattr(self, 'cpu_limit_slider') and self.cpu_limit_slider:
                cpu_percent = int(profile.cpu_usage_limit * 100)
                self.cpu_limit_slider.set(cpu_percent)
                if hasattr(self, 'cpu_limit_label'):
                    self.cpu_limit_label.configure(text=f"{cpu_percent}%")
            
            # Appliquer aux paramètres GPU si ils existent
            if hasattr(self, 'gpu_enabled_checkbox') and self.gpu_enabled_checkbox:
                if profile.prefer_gpu:
                    self.gpu_enabled_checkbox.select()
                else:
                    self.gpu_enabled_checkbox.deselect()
            
            # Appliquer d'autres paramètres selon le profil
            if hasattr(self, 'system_optimizer') and self.system_optimizer:
                # Convertir le profil RTPA vers le système existant
                self.system_optimizer.set_custom_limits(
                    profile.cpu_usage_limit * 100,
                    70.0,  # RAM par défaut
                    profile.prefer_gpu,
                    60.0   # GPU memory par défaut
                )
            
        except Exception as e:
            print(f"Erreur application interface: {e}")
    
    def _restart_cfr_with_profile(self, profile):
        """Redémarre les processus CFR avec le nouveau profil"""
        try:
            if hasattr(self, 'app_manager') and self.app_manager:
                cfr_engine = self.app_manager.cfr_engine
                
                # Arrêter les processus actuels si nécessaire
                if hasattr(cfr_engine, 'cfr_trainer') and cfr_engine.cfr_trainer:
                    if not profile.continuous_generation:
                        cfr_engine.cfr_trainer.stop_continuous_generation()
                    
                    if profile.continuous_generation and hasattr(cfr_engine.cfr_trainer, 'continuous_generator'):
                        if not cfr_engine.cfr_trainer.continuous_generator.running:
                            cfr_engine.cfr_trainer.start_continuous_generation()
                
        except Exception as e:
            print(f"Erreur redémarrage CFR: {e}")
    
    def update_system_metrics(self):
        """Met à jour les métriques système en temps réel (CPU/RAM/GPU)"""
        try:
            import psutil
            
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if hasattr(self, 'cpu_usage_bar'):
                self.cpu_usage_bar.set(cpu_percent / 100.0)
            if hasattr(self, 'cpu_usage_label'):
                self.cpu_usage_label.configure(text=f"{cpu_percent:.1f}%")
            
            # RAM Usage
            memory = psutil.virtual_memory()
            ram_percent = memory.percent
            if hasattr(self, 'ram_usage_bar'):
                self.ram_usage_bar.set(ram_percent / 100.0)
            if hasattr(self, 'ram_usage_label'):
                self.ram_usage_label.configure(text=f"{ram_percent:.1f}%")
            
            # GPU Usage (si PyTorch disponible)
            gpu_usage = 0.0
            gpu_text = "N/A"
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_memory_used = torch.cuda.memory_allocated(0)
                    gpu_memory_total = torch.cuda.get_device_properties(0).total_memory
                    gpu_percent = (gpu_memory_used / gpu_memory_total) * 100
                    gpu_usage = gpu_percent / 100.0
                    gpu_text = f"{gpu_percent:.1f}%"
            except Exception:
                pass
            
            if hasattr(self, 'gpu_usage_bar'):
                self.gpu_usage_bar.set(gpu_usage)
            if hasattr(self, 'gpu_usage_label'):
                self.gpu_usage_label.configure(text=gpu_text)
            
            # Programmer la prochaine mise à jour
            self.root.after(2000, self.update_system_metrics)  # Toutes les 2 secondes
            
        except Exception as e:
            print(f"Erreur update system metrics: {e}")
            # Reprogram même en cas d'erreur
            self.root.after(5000, self.update_system_metrics)

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
                    # Appliquer la limite CPU réelle (convertir pourcentage en décimal)
                    self.app_manager.cfr_trainer.configure_generation_resources(
                        cpu_percent=cpu_value
                    )
                    print(f"✅ Limite CPU CFR appliquée et sauvegardée: {cpu_value}%")
                    
                    # Vérifier que la limite est bien appliquée
                    if hasattr(self.app_manager.cfr_trainer, 'continuous_generator') and self.app_manager.cfr_trainer.continuous_generator:
                        actual_limit = self.app_manager.cfr_trainer.continuous_generator.settings.cpu_usage_limit
                        print(f"🔍 Vérification: limite CPU active = {actual_limit*100:.1f}%")
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
                    
                    # Vérifier que la limite est bien appliquée
                    if hasattr(self.app_manager.cfr_trainer, 'continuous_generator') and self.app_manager.cfr_trainer.continuous_generator:
                        actual_queue = self.app_manager.cfr_trainer.continuous_generator.settings.max_queue_size
                        print(f"🔍 Vérification: queue mémoire active = {actual_queue} mains")
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
    
    def export_cfr_database(self):
        """Exporte la base de données CFR/Nash"""
        try:
            import tkinter.filedialog as fd
            import os
            from datetime import datetime
            
            # Dialogue de sauvegarde
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"cfr_database_{timestamp}.json.gz"
            
            file_path = fd.asksaveasfilename(
                title="Exporter la base CFR/Nash",
                defaultextension=".json.gz",
                filetypes=[("Fichiers CFR compressés", "*.json.gz"), ("Tous les fichiers", "*.*")],
                initialname=default_name
            )
            
            if file_path:
                self.cfr_status_label.configure(text="Exportation en cours...", text_color="orange")
                self.export_cfr_btn.configure(state="disabled", text="📤 Export...")
                
                # Thread pour éviter de bloquer l'interface
                import threading
                thread = threading.Thread(target=self._export_cfr_worker, args=(file_path,), daemon=True)
                thread.start()
        
        except Exception as e:
            print(f"Erreur export CFR: {e}")
            self.cfr_status_label.configure(text="Erreur d'export", text_color="red")
    
    def _export_cfr_worker(self, file_path):
        """Worker thread pour l'export CFR"""
        try:
            success = False
            
            # Essayer avec le CFR trainer si disponible
            if hasattr(self, 'app_manager') and self.app_manager:
                if hasattr(self.app_manager, 'cfr_trainer') and self.app_manager.cfr_trainer:
                    success = self.app_manager.cfr_trainer.export_optimized_database(file_path)
                elif hasattr(self.app_manager, 'database') and self.app_manager.database:
                    success = self.app_manager.database.export_database(file_path)
            
            # Mise à jour de l'interface
            if success:
                self.root.after(0, lambda: self.cfr_status_label.configure(
                    text="✅ Export réussi", text_color="green"
                ))
                print(f"✅ Base CFR exportée: {file_path}")
            else:
                self.root.after(0, lambda: self.cfr_status_label.configure(
                    text="❌ Échec d'export", text_color="red"
                ))
                
        except Exception as e:
            print(f"Erreur export worker: {e}")
            self.root.after(0, lambda: self.cfr_status_label.configure(
                text="❌ Erreur export", text_color="red"
            ))
        finally:
            self.root.after(0, lambda: self.export_cfr_btn.configure(
                state="normal", text="📤 Exporter CFR"
            ))
    
    def import_cfr_database(self):
        """Importe une base de données CFR/Nash"""
        try:
            import tkinter.filedialog as fd
            import tkinter.messagebox as msgbox
            
            # Dialogue de sélection
            file_path = fd.askopenfilename(
                title="Importer une base CFR/Nash",
                filetypes=[("Fichiers CFR compressés", "*.json.gz"), ("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
            )
            
            if file_path:
                # Confirmation car cela écrase les données actuelles
                result = msgbox.askyesno(
                    "Confirmation d'import",
                    "L'import va remplacer les données CFR actuelles.\n\nVoulez-vous continuer?"
                )
                
                if result:
                    self.cfr_status_label.configure(text="Import en cours...", text_color="orange")
                    self.import_cfr_btn.configure(state="disabled", text="📥 Import...")
                    
                    # Thread pour éviter de bloquer l'interface
                    import threading
                    thread = threading.Thread(target=self._import_cfr_worker, args=(file_path,), daemon=True)
                    thread.start()
        
        except Exception as e:
            print(f"Erreur import CFR: {e}")
            self.cfr_status_label.configure(text="Erreur d'import", text_color="red")
    
    def _import_cfr_worker(self, file_path):
        """Worker thread pour l'import CFR"""
        try:
            success = False
            
            # Essayer d'importer via le manager
            if hasattr(self, 'app_manager') and self.app_manager:
                if hasattr(self.app_manager, 'database') and self.app_manager.database:
                    success = self.app_manager.database.import_database(file_path, self.app_manager.cfr_engine)
            
            # Mise à jour de l'interface
            if success:
                self.root.after(0, lambda: self.cfr_status_label.configure(
                    text="✅ Import réussi", text_color="green"
                ))
                print(f"✅ Base CFR importée: {file_path}")
            else:
                self.root.after(0, lambda: self.cfr_status_label.configure(
                    text="❌ Échec d'import", text_color="red"
                ))
                
        except Exception as e:
            print(f"Erreur import worker: {e}")
            self.root.after(0, lambda: self.cfr_status_label.configure(
                text="❌ Erreur import", text_color="red"
            ))
        finally:
            self.root.after(0, lambda: self.import_cfr_btn.configure(
                state="normal", text="📥 Importer CFR"
            ))
    
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