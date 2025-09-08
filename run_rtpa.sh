#!/bin/bash

# RTPA Studio C++20 - Script de lancement optimisé
# Compatible Windows/Linux avec détection automatique matérielle

echo "🚀 RTPA Studio C++20 - Lancement optimisé"
echo "   ⚡ Performance: Calculs natifs ultra-rapides"
echo "   🎨 Interface: Qt6 moderne et responsive"  
echo "   👁️  OCR: OpenCV + Tesseract natif"
echo

# Vérification environnement
if [ ! -f "build/rtpa_studio" ] && [ ! -f "build/rtpa_studio.exe" ]; then
    echo "❌ Exécutable non trouvé. Build requis:"
    echo "   python3 build_rtpa.py"
    exit 1
fi

# Détection OS et lancement
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    echo "🏠 Windows détecté"
    if [ -f "build/rtpa_studio.exe" ]; then
        echo "🎯 Lancement RTPA Studio Windows..."
        cd build && ./rtpa_studio.exe
    else
        echo "❌ rtpa_studio.exe non trouvé dans build/"
        exit 1
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Linux détecté"
    if [ -f "build/rtpa_studio" ]; then
        echo "🎯 Lancement RTPA Studio Linux..."
        cd build && ./rtpa_studio
    else
        echo "❌ rtpa_studio non trouvé dans build/"
        exit 1
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS détecté"
    if [ -f "build/rtpa_studio" ]; then
        echo "🎯 Lancement RTPA Studio macOS..."
        cd build && ./rtpa_studio
    else
        echo "❌ rtpa_studio non trouvé dans build/"
        exit 1
    fi
else
    echo "⚠️  OS non reconnu: $OSTYPE"
    echo "Tentative de lancement standard..."
    cd build && ./rtpa_studio
fi

echo
echo "✅ RTPA Studio terminé"