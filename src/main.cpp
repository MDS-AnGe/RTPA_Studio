/**
 * RTPA Studio - Real-Time Poker Assistant
 * Architecture C++20 haute performance
 * 
 * Version 2.0 - Migration complète Python/Rust vers C++ moderne
 * Technologies: C++20 + Qt6 + OpenCV + Tesseract + CUDA
 */

#include <QApplication>
#include <QStyleFactory>
#include <QDir>
#include <QStandardPaths>
#include <iostream>
#include <memory>

#include "core/AppManager.h"
#include "gui/MainWindow.h"
#include "utils/Logger.h"

int main(int argc, char *argv[])
{
    // Configuration Qt Application
    QApplication app(argc, argv);
    app.setApplicationName("RTPA Studio");
    app.setApplicationVersion("2.0.0");
    app.setOrganizationName("RTPA");
    app.setApplicationDisplayName("RTPA Studio - Real-Time Poker Assistant");

    // Style moderne
    app.setStyle(QStyleFactory::create("Fusion"));
    
    // Palette sombre moderne
    QPalette darkPalette;
    darkPalette.setColor(QPalette::Window, QColor(53, 53, 53));
    darkPalette.setColor(QPalette::WindowText, Qt::white);
    darkPalette.setColor(QPalette::Base, QColor(25, 25, 25));
    darkPalette.setColor(QPalette::AlternateBase, QColor(53, 53, 53));
    darkPalette.setColor(QPalette::ToolTipBase, Qt::white);
    darkPalette.setColor(QPalette::ToolTipText, Qt::white);
    darkPalette.setColor(QPalette::Text, Qt::white);
    darkPalette.setColor(QPalette::Button, QColor(53, 53, 53));
    darkPalette.setColor(QPalette::ButtonText, Qt::white);
    darkPalette.setColor(QPalette::BrightText, Qt::red);
    darkPalette.setColor(QPalette::Link, QColor(42, 130, 218));
    darkPalette.setColor(QPalette::Highlight, QColor(42, 130, 218));
    darkPalette.setColor(QPalette::HighlightedText, Qt::black);
    app.setPalette(darkPalette);

    // Initialisation logger
    rtpa::utils::Logger::initialize();
    
    std::cout << "🚀 RTPA Studio C++20 - Démarrage" << std::endl;
    std::cout << "   ⚡ Performance: Calculs natifs ultra-rapides" << std::endl;
    std::cout << "   🎨 Interface: Qt6 moderne et responsive" << std::endl;
    std::cout << "   👁️  OCR: OpenCV + Tesseract natif" << std::endl;
    
    #ifdef RTPA_CUDA_ENABLED
    std::cout << "   🔥 GPU: CUDA acceleration disponible" << std::endl;
    #endif
    
    try {
        // Initialisation du gestionnaire d'application
        auto appManager = std::make_unique<rtpa::core::AppManager>();
        if (!appManager->initialize()) {
            std::cerr << "❌ Erreur initialisation AppManager" << std::endl;
            return -1;
        }

        // Création fenêtre principale
        rtpa::gui::MainWindow mainWindow;
        mainWindow.setAppManager(appManager.get());
        
        // Configuration taille et position
        mainWindow.resize(1400, 900);
        mainWindow.show();

        std::cout << "✅ RTPA Studio initialisé avec succès" << std::endl;
        std::cout << "🎯 Prêt pour analyse poker temps réel" << std::endl;

        // Démarrage event loop Qt
        int result = app.exec();
        
        // Cleanup
        appManager->shutdown();
        
        return result;

    } catch (const std::exception& e) {
        std::cerr << "💥 Erreur critique: " << e.what() << std::endl;
        return -1;
    }
}