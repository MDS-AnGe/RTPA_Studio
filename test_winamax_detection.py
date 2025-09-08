#!/usr/bin/env python3
"""
Test de la détection Winamax améliorée
Teste la capacité de détecter lobby et tables séparément
"""

import sys
import os
sys.path.append('.')

def test_winamax_detection():
    """Test de la détection Winamax améliorée"""
    
    print("🧪 Test de détection Winamax améliorée")
    print("=" * 50)
    
    try:
        from src.utils.platform_detector import PlatformDetector
        
        detector = PlatformDetector()
        
        # Test 1: Détection générale
        print("\n📊 1. Détection générale des plateformes:")
        detection_result = detector.force_detection()
        print(f"   Plateformes actives: {detection_result['platform_names']}")
        
        # Test 2: Informations détaillées
        print("\n🔍 2. Analyse détaillée:")
        detailed_info = detector.get_detection_info()
        
        print(f"   Processus trouvés: {len(detailed_info['all_processes'])}")
        print(f"   Processus correspondants: {detailed_info['matching_processes']}")
        
        if 'all_windows' in detailed_info:
            print(f"   Fenêtres trouvées: {len(detailed_info['all_windows'])}")
            if detailed_info['matching_windows']:
                print(f"   Fenêtres Winamax détectées:")
                for window, platform in detailed_info['matching_windows']:
                    print(f"     - {window}")
        
        # Test 3: Détection spécialisée Winamax
        print("\n🎯 3. Détection spécialisée Winamax:")
        winamax_info = detector.detect_winamax_tables()
        
        print(f"   Processus Winamax: {'✅' if winamax_info['process_detected'] else '❌'}")
        print(f"   Lobby détecté: {'✅' if winamax_info['lobby_detected'] else '❌'}")
        print(f"   Tables détectées: {len(winamax_info['tables_detected'])}")
        
        if winamax_info['all_winamax_windows']:
            print(f"   Fenêtres Winamax:")
            for window in winamax_info['all_winamax_windows']:
                print(f"     - {window}")
        
        if winamax_info['tables_detected']:
            print(f"   Tables spécifiques:")
            for table in winamax_info['tables_detected']:
                print(f"     - {table}")
        
        # Recommandations
        print("\n💡 Recommandations:")
        if not winamax_info['process_detected']:
            print("   ⚠️  Winamax n'est pas détecté - ouvrez le client")
        elif winamax_info['lobby_detected'] and not winamax_info['tables_detected']:
            print("   ⚠️  Seul le lobby est ouvert - ouvrez une table")
        elif winamax_info['tables_detected']:
            print("   ✅ Tables détectées - RTPA devrait fonctionner")
        else:
            print("   ❓ État incertain - vérifiez la configuration")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test de détection Winamax pour RTPA Studio")
    print("Assurez-vous que Winamax soit ouvert pour des tests complets\n")
    
    success = test_winamax_detection()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Test terminé avec succès")
    else:
        print("❌ Test échoué")
    
    input("\nAppuyez sur Entrée pour fermer...")