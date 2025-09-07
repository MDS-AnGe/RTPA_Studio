"""
Parseur d'historiques de mains poker pour entraînement CFR
Supporte les formats ACPC, PokerStars et format compact
"""

import re
import time
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ..utils.logger import get_logger

class HandFormat(Enum):
    ACPC = "acpc"
    POKERSTARS = "pokerstars"
    COMPACT = "compact"
    UNKNOWN = "unknown"

@dataclass
class ParsedHand:
    """Main de poker parsée et normalisée"""
    hand_id: str
    hero_cards: Tuple[str, str]
    board_cards: List[str]
    actions: List[str]  # Séquence d'actions: f, c, r200, etc.
    pot_size: float
    hero_stack: float
    villain_stack: float
    position: int  # 0 = small blind, 1 = big blind
    blinds: Tuple[float, float]  # (small_blind, big_blind)
    result: float  # Gain/perte pour le héros
    street: int  # 0=preflop, 1=flop, 2=turn, 3=river
    
class HandParser:
    """Parseur multi-format pour historiques de mains"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.hands_parsed = 0
        self.errors = 0
        
        # Expressions régulières pour les différents formats
        self._init_regex_patterns()
    
    def _init_regex_patterns(self):
        """Initialise les patterns regex pour le parsing"""
        
        # Format ACPC
        self.acpc_pattern = re.compile(
            r'STATE:(\d+):(\d+)\|(\d+):(\d+)\|(\d+):([^:]+):([^:]*):([^:]+):(.+)'
        )
        
        # Format PokerStars
        self.pokerstars_hand_pattern = re.compile(
            r'PokerStars Hand #(\d+).*\$(\d+)/\$(\d+)'
        )
        self.pokerstars_cards_pattern = re.compile(
            r'Dealt to \w+ \[([2-9TJQKA][shdc]) ([2-9TJQKA][shdc])\]'
        )
        self.pokerstars_board_pattern = re.compile(
            r'\[([2-9TJQKA][shdc](?:\s+[2-9TJQKA][shdc])*)\]'
        )
        
        # Format compact
        self.compact_pattern = re.compile(
            r'(\d+):([^:]+):([^:]*):([^:]+):([^:]*):([^:]+)'
        )
    
    def detect_format(self, line: str) -> HandFormat:
        """Détecte le format d'une ligne de main"""
        if line.startswith('STATE:'):
            return HandFormat.ACPC
        elif 'PokerStars Hand' in line:
            return HandFormat.POKERSTARS
        elif ':' in line and ',' in line and '|' in line:
            return HandFormat.COMPACT
        else:
            return HandFormat.UNKNOWN
    
    def parse_file(self, file_path: str) -> List[ParsedHand]:
        """Parse un fichier complet de mains"""
        hands = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Détection du format majoritaire
            lines = content.split('\n')
            format_counts = {fmt: 0 for fmt in HandFormat}
            
            for line in lines[:100]:  # Échantillon
                if line.strip():
                    fmt = self.detect_format(line)
                    format_counts[fmt] += 1
            
            main_format = max(format_counts.items(), key=lambda x: x[1])[0]
            
            if main_format == HandFormat.ACPC:
                hands = self._parse_acpc_file(content)
            elif main_format == HandFormat.POKERSTARS:
                hands = self._parse_pokerstars_file(content)
            elif main_format == HandFormat.COMPACT:
                hands = self._parse_compact_file(content)
            
            self.logger.info(f"Parsé {len(hands)} mains depuis {file_path}")
            
        except Exception as e:
            self.logger.error(f"Erreur parsing fichier {file_path}: {e}")
            
        return hands
    
    def _parse_acpc_file(self, content: str) -> List[ParsedHand]:
        """Parse format ACPC"""
        hands = []
        
        for line in content.split('\n'):
            if line.startswith('STATE:'):
                hand = self._parse_acpc_line(line)
                if hand:
                    hands.append(hand)
        
        return hands
    
    def _parse_acpc_line(self, line: str) -> Optional[ParsedHand]:
        """Parse une ligne ACPC"""
        try:
            match = self.acpc_pattern.match(line)
            if not match:
                return None
            
            hand_id, hero_stack, villain_stack, sb, bb, actions, cards, result, players = match.groups()
            
            # Parse cartes
            if '|' in cards:
                hero_cards_str, board_str = cards.split('|', 1)
                hero_cards = self._parse_card_pair(hero_cards_str)
                board_cards = self._parse_board_cards(board_str)
            else:
                hero_cards = self._parse_card_pair(cards)
                board_cards = []
            
            # Parse actions
            action_list = self._parse_acpc_actions(actions)
            
            # Parse résultat
            result_parts = result.split(':')
            hero_result = 0.0
            if len(result_parts) >= 2:
                try:
                    hero_result = float(result_parts[0])
                except:
                    pass
            
            # Déterminer street
            street = self._determine_street(board_cards)
            
            return ParsedHand(
                hand_id=hand_id,
                hero_cards=hero_cards,
                board_cards=board_cards,
                actions=action_list,
                pot_size=float(sb) + float(bb),
                hero_stack=float(hero_stack),
                villain_stack=float(villain_stack),
                position=0,  # À déterminer selon le format
                blinds=(float(sb), float(bb)),
                result=hero_result,
                street=street
            )
            
        except Exception as e:
            self.logger.error(f"Erreur parsing ligne ACPC: {e}")
            return None
    
    def _parse_pokerstars_file(self, content: str) -> List[ParsedHand]:
        """Parse format PokerStars"""
        hands = []
        hand_blocks = content.split('PokerStars Hand')
        
        for i, block in enumerate(hand_blocks[1:], 1):  # Skip premier block vide
            hand = self._parse_pokerstars_block(f"PokerStars Hand{block}", str(i))
            if hand:
                hands.append(hand)
        
        return hands
    
    def _parse_pokerstars_block(self, block: str, hand_id: str) -> Optional[ParsedHand]:
        """Parse un block PokerStars complet"""
        try:
            lines = block.split('\n')
            
            # Parse blinds depuis header
            header_match = self.pokerstars_hand_pattern.search(block)
            if not header_match:
                return None
            
            actual_hand_id, sb, bb = header_match.groups()
            
            # Parse cartes héros
            cards_match = self.pokerstars_cards_pattern.search(block)
            if not cards_match:
                return None
            
            hero_cards = (cards_match.group(1), cards_match.group(2))
            
            # Parse board
            board_matches = self.pokerstars_board_pattern.findall(block)
            board_cards = []
            if board_matches:
                # Prendre le board le plus complet (river)
                last_board = board_matches[-1]
                board_cards = last_board.split()
            
            # Parse actions (simplifié)
            actions = self._parse_pokerstars_actions(block)
            
            # Parse résultat (basique)
            result = 0.0
            if 'collected' in block:
                # Extraction simplifiée du gain
                if 'DeepStack collected' in block:
                    result_match = re.search(r'collected \$(\d+)', block)
                    if result_match:
                        result = float(result_match.group(1))
            
            return ParsedHand(
                hand_id=actual_hand_id,
                hero_cards=hero_cards,
                board_cards=board_cards,
                actions=actions,
                pot_size=float(sb) + float(bb),
                hero_stack=20000.0,  # Stack standard DeepStack
                villain_stack=20000.0,
                position=0,
                blinds=(float(sb), float(bb)),
                result=result,
                street=len(board_cards) // 3 if board_cards else 0
            )
            
        except Exception as e:
            self.logger.error(f"Erreur parsing block PokerStars: {e}")
            return None
    
    def _parse_compact_file(self, content: str) -> List[ParsedHand]:
        """Parse format compact"""
        hands = []
        
        for line in content.split('\n'):
            if ':' in line and ',' in line:
                hand = self._parse_compact_line(line)
                if hand:
                    hands.append(hand)
        
        return hands
    
    def _parse_compact_line(self, line: str) -> Optional[ParsedHand]:
        """Parse ligne format compact"""
        try:
            match = self.compact_pattern.match(line.strip())
            if not match:
                return None
            
            hand_id, players, actions, cards, board_info, result_info = match.groups()
            
            # Parse cartes
            if ',' in cards:
                cards_split = cards.split(',')
                if len(cards_split) >= 2:
                    hero_cards = self._parse_card_pair(cards_split[0])
                else:
                    return None
            else:
                return None
            
            # Parse board
            board_cards = []
            if '/' in board_info:
                board_parts = board_info.split('/')
                for part in board_parts[1:]:  # Skip premier qui est vide
                    if part:
                        board_cards.extend(self._parse_board_cards(part))
            
            # Parse actions
            action_list = self._parse_compact_actions(actions)
            
            # Parse résultat
            result = 0.0
            if ':' in result_info:
                result_parts = result_info.split(':')
                if len(result_parts) >= 2:
                    try:
                        result = float(result_parts[0])
                    except:
                        pass
            
            return ParsedHand(
                hand_id=hand_id,
                hero_cards=hero_cards,
                board_cards=board_cards,
                actions=action_list,
                pot_size=100.0,  # Valeur par défaut
                hero_stack=20000.0,
                villain_stack=20000.0,
                position=0,
                blinds=(50.0, 100.0),
                result=result,
                street=self._determine_street(board_cards)
            )
            
        except Exception as e:
            self.logger.error(f"Erreur parsing ligne compact: {e}")
            return None
    
    def _parse_card_pair(self, cards_str: str) -> Tuple[str, str]:
        """Parse une paire de cartes"""
        cards_str = cards_str.strip()
        
        if len(cards_str) == 4:  # Format "AcKh"
            return (cards_str[:2], cards_str[2:])
        elif ' ' in cards_str:  # Format "Ac Kh"
            parts = cards_str.split()
            if len(parts) >= 2:
                return (parts[0], parts[1])
        
        return ("", "")
    
    def _parse_board_cards(self, board_str: str) -> List[str]:
        """Parse les cartes du board"""
        if not board_str:
            return []
        
        # Nettoie et split
        board_str = board_str.strip()
        cards = []
        
        # Différents formats possibles
        if ' ' in board_str:
            cards = board_str.split()
        else:
            # Format compact "AcKhQs"
            i = 0
            while i < len(board_str) - 1:
                if i + 1 < len(board_str):
                    card = board_str[i:i+2]
                    if len(card) == 2:
                        cards.append(card)
                        i += 2
                    else:
                        i += 1
                else:
                    break
        
        return [card for card in cards if len(card) == 2]
    
    def _parse_acpc_actions(self, actions_str: str) -> List[str]:
        """Parse actions format ACPC"""
        actions = []
        
        # Split par streets
        streets = actions_str.split('/')
        
        for street in streets:
            i = 0
            while i < len(street):
                if street[i] == 'f':
                    actions.append('fold')
                    i += 1
                elif street[i] == 'c':
                    actions.append('call')
                    i += 1
                elif street[i] == 'r':
                    # Extract bet size
                    j = i + 1
                    while j < len(street) and street[j].isdigit():
                        j += 1
                    if j > i + 1:
                        bet_size = street[i+1:j]
                        actions.append(f'raise_{bet_size}')
                        i = j
                    else:
                        actions.append('raise')
                        i += 1
                else:
                    i += 1
        
        return actions
    
    def _parse_pokerstars_actions(self, block: str) -> List[str]:
        """Parse actions format PokerStars (simplifié)"""
        actions = []
        
        # Recherche des patterns d'actions
        if 'folds' in block:
            actions.append('fold')
        if 'calls' in block:
            actions.append('call')
        if 'raises' in block:
            actions.append('raise')
        if 'bets' in block:
            actions.append('bet')
        if 'checks' in block:
            actions.append('check')
        
        return actions
    
    def _parse_compact_actions(self, actions_str: str) -> List[str]:
        """Parse actions format compact"""
        actions = []
        
        # Format type "cc/cc/cr200r19700f"
        streets = actions_str.split('/')
        
        for street in streets:
            i = 0
            while i < len(street):
                if street[i] == 'f':
                    actions.append('fold')
                    i += 1
                elif street[i] == 'c':
                    actions.append('call')
                    i += 1
                elif street[i] == 'r':
                    # Extract bet size
                    j = i + 1
                    while j < len(street) and street[j].isdigit():
                        j += 1
                    if j > i + 1:
                        bet_size = street[i+1:j]
                        actions.append(f'raise_{bet_size}')
                        i = j
                    else:
                        actions.append('raise')
                        i += 1
                else:
                    i += 1
        
        return actions
    
    def _determine_street(self, board_cards: List[str]) -> int:
        """Détermine la street selon le nombre de cartes board"""
        if not board_cards:
            return 0  # preflop
        elif len(board_cards) == 3:
            return 1  # flop
        elif len(board_cards) == 4:
            return 2  # turn
        elif len(board_cards) == 5:
            return 3  # river
        else:
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de parsing"""
        return {
            'hands_parsed': self.hands_parsed,
            'errors': self.errors,
            'success_rate': (self.hands_parsed / max(1, self.hands_parsed + self.errors)) * 100
        }