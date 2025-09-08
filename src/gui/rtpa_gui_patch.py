"""
PATCH TEMPORAIRE pour corriger le freeze des widgets
À ajouter dans rtpa_gui.py après la fonction create_players_display
"""

def update_players_display_optimized(self, players_data=None):
    """Met à jour les widgets joueurs SANS les recréer (PATTERN OPTIMISÉ ANTI-FREEZE)"""
    
    if not hasattr(self, 'player_widgets'):
        print("❌ Widgets joueurs pas encore créés, création en cours...")
        self.create_players_display(players_data)
        return
    
    if players_data is None:
        players_data = []
    
    print(f"✅ Mise à jour OPTIMISÉE de {len(self.player_widgets)} widgets joueurs (sans recréation)")
    
    # Créer un dictionnaire des joueurs par position
    players_by_position = {}
    if players_data:
        for player in players_data:
            pos_index = player.get('position', 0)
            players_by_position[pos_index] = player
    
    # Mettre à jour chaque widget existant (AUCUNE destruction)
    for i, widget_data in enumerate(self.player_widgets):
        player = players_by_position.get(i)
        
        # Références aux widgets existants
        name_label = widget_data['name_label']
        stack_label = widget_data['stack_label'] 
        status_label = widget_data['status_label']
        position_name = widget_data['position_name']
        
        if player:
            # Position occupée - mettre à jour les textes
            name = player.get('name', 'Inconnu')
            stack = player.get('stack', '0€')
            status = player.get('status', 'En jeu')
            
            name_color = '#0066cc' if player.get('is_hero', False) else '#000000'
            status_color = '#28a745' if status == 'actif' else '#6c757d'
            
            # MISE À JOUR des textes seulement (pas de destroy/create)
            name_label.configure(text=f"{position_name}: {name}", fg=name_color)
            stack_label.configure(text=f"Stack: {stack}")
            status_label.configure(text=f"Status: {status}", fg=status_color)
            
        else:
            # Position vide - réinitialiser
            name_label.configure(text=f"{position_name}: (vide)", fg='#666666')
            stack_label.configure(text="Stack: —")
            status_label.configure(text="Status: Absent", fg='#cc0000')