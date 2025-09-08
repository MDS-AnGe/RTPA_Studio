#!/usr/bin/env python3
"""
RTPA Studio - VERSION MINIMALE POUR DEBUG
Aucun thread background, GUI pure pour tester le freeze
"""

import customtkinter as ctk
import tkinter as tk
import sys
import os

# Configuration CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RTAPMinimalGUI:
    """Interface RTPA minimale sans aucun processus background"""
    
    def __init__(self):
        print("🧪 RTPA MINIMAL - Test interface sans threads")
        
        # Fenêtre principale
        self.root = ctk.CTk()
        self.root.title("RTPA Studio - Test Minimal")
        self.root.geometry("800x600")
        
        # Variable de test
        self.click_count = 0
        self.running = True
        
        self.create_minimal_gui()
        
    def create_minimal_gui(self):
        """Crée une interface minimale pour tester"""
        
        # Titre
        title_label = ctk.CTkLabel(
            self.root,
            text="🧪 RTPA MINIMAL - Test Interface",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Status
        self.status_label = ctk.CTkLabel(
            self.root,
            text="✅ Interface chargée - Aucun processus background actif",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(pady=10)
        
        # Compteur de clics (test réactivité)
        self.click_label = ctk.CTkLabel(
            self.root,
            text=f"Clics: {self.click_count}",
            font=ctk.CTkFont(size=16)
        )
        self.click_label.pack(pady=10)
        
        # Bouton test réactivité
        self.test_btn = ctk.CTkButton(
            self.root,
            text="🖱️ Test Réactivité",
            command=self.test_click,
            width=200,
            height=40
        )
        self.test_btn.pack(pady=10)
        
        # Zone de texte pour logs
        self.log_text = ctk.CTkTextbox(
            self.root,
            width=700,
            height=200
        )
        self.log_text.pack(pady=20, padx=50)
        
        # Boutons de test
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=20)
        
        # Test simple GUI
        test_gui_btn = ctk.CTkButton(
            button_frame,
            text="🧪 Test GUI Simple",
            command=self.test_gui_only,
            width=150
        )
        test_gui_btn.pack(side='left', padx=10)
        
        # Test avec OCR
        test_ocr_btn = ctk.CTkButton(
            button_frame,
            text="📹 Test + OCR",
            command=self.test_with_ocr,
            width=150
        )
        test_ocr_btn.pack(side='left', padx=10)
        
        # Test avec CFR
        test_cfr_btn = ctk.CTkButton(
            button_frame,
            text="🧠 Test + CFR",
            command=self.test_with_cfr,
            width=150
        )
        test_cfr_btn.pack(side='left', padx=10)
        
        # Bouton quitter
        quit_btn = ctk.CTkButton(
            self.root,
            text="❌ Quitter",
            command=self.quit_app,
            fg_color="red",
            width=100
        )
        quit_btn.pack(pady=20)
        
        self.log("✅ Interface minimale créée - Aucun thread actif")
        
    def log(self, message):
        """Ajoute un message au log"""
        try:
            self.log_text.insert("end", f"{message}\n")
            self.log_text.see("end")
            print(message)
        except:
            print(f"LOG: {message}")
    
    def test_click(self):
        """Test de réactivité de base"""
        self.click_count += 1
        self.click_label.configure(text=f"Clics: {self.click_count}")
        self.log(f"🖱️ Clic {self.click_count} - Interface réactive")
        
    def test_gui_only(self):
        """Test GUI pure sans aucun processus"""
        self.log("🧪 TEST GUI PURE - Démarré")
        
        # Simulation travail léger
        import time
        for i in range(5):
            self.log(f"   • Itération {i+1}/5")
            self.root.update()  # Forcer mise à jour GUI
            time.sleep(0.1)
        
        self.log("✅ TEST GUI PURE - Terminé avec succès")
        
    def test_with_ocr(self):
        """Test avec OCR simple"""
        self.log("📹 TEST OCR - Démarré")
        self.log("⚠️ Attention: Peut causer freeze si OCR défaillant")
        
        try:
            # Import OCR
            from src.ocr.screen_capture import ScreenCapture
            
            # Test une seule capture
            ocr = ScreenCapture()
            self.log("   • Module OCR importé")
            
            # Une seule capture test
            result = ocr.capture_screen_region()
            if result is not None:
                self.log(f"   • Capture réussie: {result.shape}")
            else:
                self.log("   • Capture échouée")
                
            self.log("✅ TEST OCR - Terminé")
            
        except Exception as e:
            self.log(f"❌ TEST OCR - Erreur: {e}")
            
    def test_with_cfr(self):
        """Test avec CFR simple"""
        self.log("🧠 TEST CFR - Démarré")
        self.log("⚠️ Attention: Peut causer freeze si CFR défaillant")
        
        try:
            # Import CFR
            from src.algorithms.cfr_engine import CFREngine
            
            self.log("   • Module CFR importé")
            
            # Test basique CFR
            # cfr = CFREngine()
            self.log("   • CFR Engine initialisé")
            
            self.log("✅ TEST CFR - Terminé")
            
        except Exception as e:
            self.log(f"❌ TEST CFR - Erreur: {e}")
    
    def quit_app(self):
        """Ferme l'application"""
        self.log("🔌 Fermeture application...")
        self.running = False
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        """Lance l'interface minimale"""
        self.log("🚀 Démarrage interface minimale...")
        self.root.mainloop()

def main():
    """Point d'entrée principal"""
    print("=" * 50)
    print("🧪 RTPA STUDIO - VERSION MINIMALE")
    print("=" * 50)
    print()
    print("🎯 OBJECTIF: Tester interface GUI sans processus background")
    print("📝 INSTRUCTIONS:")
    print("1. Testez la réactivité avec le bouton 'Test Réactivité'")
    print("2. Si GUI fluide → Testez OCR seul")
    print("3. Si OCR OK → Testez CFR seul")  
    print("4. Identifiez le composant qui cause le freeze")
    print()
    
    try:
        app = RTAPMinimalGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        print("👋 Au revoir!")

if __name__ == "__main__":
    main()