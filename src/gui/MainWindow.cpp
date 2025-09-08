/**
 * Implémentation fenêtre principale Qt6
 */

#include "MainWindow.h"
#include "GameTable.h"
#include "StatsWidget.h"
#include "ConfigDialog.h"
#include "core/AppManager.h"
#include "utils/Logger.h"

#include <QApplication>
#include <QMenuBar>
#include <QStatusBar>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QSplitter>
#include <QTabWidget>
#include <QLabel>
#include <QPushButton>
#include <QProgressBar>
#include <QTextEdit>
#include <QTimer>
#include <QCloseEvent>
#include <QMessageBox>
#include <QFileDialog>
#include <QSystemTrayIcon>
#include <QMenu>
#include <QAction>
#include <QtCharts/QChart>
#include <QtCharts/QLineSeries>
#include <QtCharts/QPieSeries>
#include <QtCharts/QChartView>
#include <QtCharts/QValueAxis>

using namespace rtpa::gui;
using namespace rtpa::types;

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , appManager_(nullptr)
    , trainingActive_(false)
    , ocrActive_(false)
{
    setWindowTitle("RTPA Studio - Real-Time Poker Assistant");
    setMinimumSize(1200, 800);
    resize(1400, 900);

    // Application de thème sombre
    applyDarkTheme();

    // Création des composants UI
    createMenus();
    createStatusBar();
    createCentralWidget();
    createSystemTray();
    setupTimers();

    // État initial
    updateWindowTitle();
    
    utils::Logger::info("✅ Interface principale Qt6 créée");
}

MainWindow::~MainWindow() {
    // Cleanup timers
    if (gameStateTimer_) gameStateTimer_->stop();
    if (strategyTimer_) strategyTimer_->stop();
    if (statsTimer_) statsTimer_->stop();
    if (performanceTimer_) performanceTimer_->stop();
}

void MainWindow::setAppManager(rtpa::core::AppManager* manager) {
    appManager_ = manager;
    
    if (appManager_) {
        setupConnections();
        utils::Logger::info("✅ AppManager connecté à l'interface");
    }
}

void MainWindow::createMenus() {
    menuBar_ = menuBar();

    // Menu Fichier
    fileMenu_ = menuBar_->addMenu("&Fichier");
    
    newAction_ = fileMenu_->addAction("&Nouvelle session", this, &MainWindow::newSession);
    newAction_->setShortcut(QKeySequence::New);
    
    openAction_ = fileMenu_->addAction("&Ouvrir session...", this, &MainWindow::openSession);
    openAction_->setShortcut(QKeySequence::Open);
    
    saveAction_ = fileMenu_->addAction("&Sauvegarder session", this, &MainWindow::saveSession);
    saveAction_->setShortcut(QKeySequence::Save);
    
    fileMenu_->addSeparator();
    
    preferencesAction_ = fileMenu_->addAction("&Préférences...", this, &MainWindow::showPreferences);
    preferencesAction_->setShortcut(QKeySequence::Preferences);
    
    fileMenu_->addSeparator();
    
    exitAction_ = fileMenu_->addAction("&Quitter", this, &MainWindow::exitApplication);
    exitAction_->setShortcut(QKeySequence::Quit);

    // Menu CFR
    cfrMenu_ = menuBar_->addMenu("&CFR Engine");
    
    startTrainingAction_ = cfrMenu_->addAction("▶️ &Démarrer training", this, &MainWindow::startTraining);
    stopTrainingAction_ = cfrMenu_->addAction("⏹️ &Arrêter training", this, &MainWindow::stopTraining);
    stopTrainingAction_->setEnabled(false);
    
    cfrMenu_->addSeparator();
    
    intensiveTrainingAction_ = cfrMenu_->addAction("🔥 Training &intensif", this, &MainWindow::intensiveTraining);
    cfrMenu_->addAction("🔄 &Reset CFR", this, &MainWindow::resetTraining);

    // Menu OCR
    ocrMenu_ = menuBar_->addMenu("&OCR");
    
    ocrMenu_->addAction("▶️ Démarrer &OCR", this, &MainWindow::startOCR);
    ocrMenu_->addAction("⏹️ Arrêter O&CR", this, &MainWindow::stopOCR);
    ocrMenu_->addSeparator();
    
    calibrateOCRAction_ = ocrMenu_->addAction("🎯 &Calibrer OCR", this, &MainWindow::calibrateOCR);
    ocrMenu_->addAction("🧪 &Tester OCR", this, &MainWindow::testOCR);

    // Menu Outils
    toolsMenu_ = menuBar_->addMenu("&Outils");
    toolsMenu_->addAction("📊 Statistiques détaillées", this, &MainWindow::updateStatistics);
    toolsMenu_->addAction("⚡ Métriques performance", this, &MainWindow::updatePerformanceMetrics);

    // Menu Aide
    helpMenu_ = menuBar_->addMenu("&Aide");
    aboutAction_ = helpMenu_->addAction("À &propos", this, &MainWindow::showAbout);
}

void MainWindow::createStatusBar() {
    statusBar_ = statusBar();

    engineStatusLabel_ = new QLabel("CFR Engine: Arrêté");
    ocrStatusLabel_ = new QLabel("OCR: Arrêté");
    performanceLabel_ = new QLabel("CPU: 0% | RAM: 0MB");

    statusBar_->addWidget(engineStatusLabel_);
    statusBar_->addPermanentWidget(ocrStatusLabel_);
    statusBar_->addPermanentWidget(performanceLabel_);
}

void MainWindow::createCentralWidget() {
    centralWidget_ = new QWidget;
    setCentralWidget(centralWidget_);

    // Layout principal avec splitters
    auto mainLayout = new QVBoxLayout(centralWidget_);
    mainSplitter_ = new QSplitter(Qt::Horizontal);
    mainLayout->addWidget(mainSplitter_);

    // Panneau gauche - Table de jeu
    gameTableWidget_ = new GameTable;
    mainSplitter_->addWidget(gameTableWidget_);

    // Panneau droit avec splitter vertical
    rightSplitter_ = new QSplitter(Qt::Vertical);
    mainSplitter_->addWidget(rightSplitter_);

    // Création du widget de stratégie
    createStrategyWidget();
    rightSplitter_->addWidget(strategyWidget_);

    // Création du widget de performance
    createPerformanceWidget();
    rightSplitter_->addWidget(performanceWidget_);

    // Panneau contrôles
    createControlWidget();
    rightSplitter_->addWidget(controlWidget_);

    // Onglets informations
    createInfoTabs();
    rightSplitter_->addWidget(infoTabWidget_);

    // Proportions des splitters
    mainSplitter_->setStretchFactor(0, 3); // Table de jeu plus large
    mainSplitter_->setStretchFactor(1, 2);

    rightSplitter_->setStretchFactor(0, 2); // Stratégie
    rightSplitter_->setStretchFactor(1, 1); // Performance
    rightSplitter_->setStretchFactor(2, 1); // Contrôles
    rightSplitter_->setStretchFactor(3, 2); // Info tabs
}

void MainWindow::createStrategyWidget() {
    strategyWidget_ = new QWidget;
    strategyWidget_->setMaximumHeight(200);
    
    strategyLayout_ = new QGridLayout(strategyWidget_);

    // Titre
    auto titleLabel = new QLabel("🎯 Stratégie CFR Optimale");
    titleLabel->setStyleSheet("font-weight: bold; font-size: 14px; color: #4CAF50;");
    strategyLayout_->addWidget(titleLabel, 0, 0, 1, 3);

    // Recommandation principale
    recommendationLabel_ = new QLabel("Action recommandée: -");
    recommendationLabel_->setStyleSheet("font-size: 16px; font-weight: bold; color: #FFC107;");
    strategyLayout_->addWidget(recommendationLabel_, 1, 0, 1, 3);

    // Probabilités détaillées
    std::vector<std::string> actions = {"Fold", "Call", "Check", "Bet", "Raise", "All-in"};
    actionButtons_.reserve(actions.size());

    for (size_t i = 0; i < actions.size(); ++i) {
        auto button = new QPushButton(QString::fromStdString(actions[i]) + ": 0%");
        button->setEnabled(false);
        button->setStyleSheet(
            "QPushButton { "
            "background-color: #37474F; "
            "border: 2px solid #546E7A; "
            "border-radius: 8px; "
            "color: white; "
            "font-size: 12px; "
            "padding: 8px; "
            "}"
        );
        
        strategyLayout_->addWidget(button, 2 + i / 3, i % 3);
        actionButtons_.push_back(button);
    }

    // Métriques de performance
    winProbabilityLabel_ = new QLabel("Win %: 0.0%");
    expectedValueLabel_ = new QLabel("EV: +0.00 BB");
    
    winProbabilityLabel_->setStyleSheet("color: #4CAF50; font-weight: bold;");
    expectedValueLabel_->setStyleSheet("color: #2196F3; font-weight: bold;");
    
    strategyLayout_->addWidget(winProbabilityLabel_, 4, 0);
    strategyLayout_->addWidget(expectedValueLabel_, 4, 1, 1, 2);
}

void MainWindow::createPerformanceWidget() {
    performanceWidget_ = new QWidget;
    performanceWidget_->setMaximumHeight(150);
    
    auto layout = new QGridLayout(performanceWidget_);

    // Titre
    auto titleLabel = new QLabel("⚡ Performance Système");
    titleLabel->setStyleSheet("font-weight: bold; font-size: 14px; color: #FF9800;");
    layout->addWidget(titleLabel, 0, 0, 1, 3);

    // Métriques CFR
    cfrIterationsLabel_ = new QLabel("Itérations CFR: 0");
    simulationsLabel_ = new QLabel("Simulations MC: 0");
    ocrOperationsLabel_ = new QLabel("Opérations OCR: 0");
    
    layout->addWidget(cfrIterationsLabel_, 1, 0);
    layout->addWidget(simulationsLabel_, 1, 1);
    layout->addWidget(ocrOperationsLabel_, 1, 2);

    // Barres de progression système
    auto cpuLabel = new QLabel("CPU:");
    cpuUsageBar_ = new QProgressBar;
    cpuUsageBar_->setMaximum(100);
    cpuUsageBar_->setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }");
    
    auto memLabel = new QLabel("RAM:");
    memoryUsageBar_ = new QProgressBar;
    memoryUsageBar_->setMaximum(100);
    memoryUsageBar_->setStyleSheet("QProgressBar::chunk { background-color: #2196F3; }");
    
    auto gpuLabel = new QLabel("GPU:");
    gpuUsageBar_ = new QProgressBar;
    gpuUsageBar_->setMaximum(100);
    gpuUsageBar_->setStyleSheet("QProgressBar::chunk { background-color: #FF9800; }");
    
    layout->addWidget(cpuLabel, 2, 0);
    layout->addWidget(cpuUsageBar_, 2, 1, 1, 2);
    layout->addWidget(memLabel, 3, 0);
    layout->addWidget(memoryUsageBar_, 3, 1, 1, 2);
    layout->addWidget(gpuLabel, 4, 0);
    layout->addWidget(gpuUsageBar_, 4, 1, 1, 2);
}

void MainWindow::createControlWidget() {
    controlWidget_ = new QWidget;
    controlWidget_->setMaximumHeight(120);
    
    auto layout = new QGridLayout(controlWidget_);

    // Titre
    auto titleLabel = new QLabel("🎛️ Contrôles");
    titleLabel->setStyleSheet("font-weight: bold; font-size: 14px; color: #9C27B0;");
    layout->addWidget(titleLabel, 0, 0, 1, 4);

    // Boutons CFR
    startTrainingButton_ = new QPushButton("▶️ Démarrer CFR");
    stopTrainingButton_ = new QPushButton("⏹️ Arrêter CFR");
    resetButton_ = new QPushButton("🔄 Reset");
    intensiveButton_ = new QPushButton("🔥 Intensif");
    
    startTrainingButton_->setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; border-radius: 6px; }");
    stopTrainingButton_->setStyleSheet("QPushButton { background-color: #F44336; color: white; font-weight: bold; padding: 8px; border-radius: 6px; }");
    resetButton_->setStyleSheet("QPushButton { background-color: #FF9800; color: white; font-weight: bold; padding: 8px; border-radius: 6px; }");
    intensiveButton_->setStyleSheet("QPushButton { background-color: #E91E63; color: white; font-weight: bold; padding: 8px; border-radius: 6px; }");
    
    stopTrainingButton_->setEnabled(false);
    
    layout->addWidget(startTrainingButton_, 1, 0);
    layout->addWidget(stopTrainingButton_, 1, 1);
    layout->addWidget(resetButton_, 1, 2);
    layout->addWidget(intensiveButton_, 1, 3);

    // Boutons OCR
    startOCRButton_ = new QPushButton("👁️ OCR ON");
    stopOCRButton_ = new QPushButton("👁️ OCR OFF");
    calibrateButton_ = new QPushButton("🎯 Calibrer");
    testOCRButton_ = new QPushButton("🧪 Test");
    
    startOCRButton_->setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; padding: 8px; border-radius: 6px; }");
    stopOCRButton_->setStyleSheet("QPushButton { background-color: #607D8B; color: white; font-weight: bold; padding: 8px; border-radius: 6px; }");
    calibrateButton_->setStyleSheet("QPushButton { background-color: #795548; color: white; font-weight: bold; padding: 8px; border-radius: 6px; }");
    testOCRButton_->setStyleSheet("QPushButton { background-color: #009688; color: white; font-weight: bold; padding: 8px; border-radius: 6px; }");
    
    stopOCRButton_->setEnabled(false);
    
    layout->addWidget(startOCRButton_, 2, 0);
    layout->addWidget(stopOCRButton_, 2, 1);
    layout->addWidget(calibrateButton_, 2, 2);
    layout->addWidget(testOCRButton_, 2, 3);

    // Connexions des boutons
    connect(startTrainingButton_, &QPushButton::clicked, this, &MainWindow::startTraining);
    connect(stopTrainingButton_, &QPushButton::clicked, this, &MainWindow::stopTraining);
    connect(resetButton_, &QPushButton::clicked, this, &MainWindow::resetTraining);
    connect(intensiveButton_, &QPushButton::clicked, this, &MainWindow::intensiveTraining);
    
    connect(startOCRButton_, &QPushButton::clicked, this, &MainWindow::startOCR);
    connect(stopOCRButton_, &QPushButton::clicked, this, &MainWindow::stopOCR);
    connect(calibrateButton_, &QPushButton::clicked, this, &MainWindow::calibrateOCR);
    connect(testOCRButton_, &QPushButton::clicked, this, &MainWindow::testOCR);
}

void MainWindow::createInfoTabs() {
    infoTabWidget_ = new QTabWidget;

    // Onglet Logs
    logTextEdit_ = new QTextEdit;
    logTextEdit_->setReadOnly(true);
    logTextEdit_->setStyleSheet(
        "QTextEdit { "
        "background-color: #1E1E1E; "
        "color: #E0E0E0; "
        "font-family: 'Consolas', monospace; "
        "font-size: 11px; "
        "border: 1px solid #424242; "
        "}"
    );
    logTextEdit_->append("🚀 RTPA Studio C++20 démarré");
    logTextEdit_->append("⚡ Moteur CFR natif prêt");
    logTextEdit_->append("👁️ Système OCR initialisé");
    
    infoTabWidget_->addTab(logTextEdit_, "📝 Logs");

    // Onglet Statistiques
    statsWidget_ = new StatsWidget;
    infoTabWidget_->addTab(statsWidget_, "📊 Stats");

    // Onglet Graphiques
    createChartsTab();
}

void MainWindow::createChartsTab() {
    auto chartsWidget = new QWidget;
    auto chartsLayout = new QVBoxLayout(chartsWidget);

    // Graphique de convergence CFR
    convergenceChart_ = new QtCharts::QChart();
    convergenceChart_->setTitle("🎯 Convergence CFR");
    convergenceChart_->setTheme(QtCharts::QChart::ChartThemeDark);
    
    convergenceSeries_ = new QtCharts::QLineSeries();
    convergenceSeries_->setName("Convergence");
    convergenceChart_->addSeries(convergenceSeries_);
    
    convergenceChartView_ = new QtCharts::QChartView(convergenceChart_);
    convergenceChartView_->setRenderHint(QPainter::Antialiasing);
    
    // Graphique win rate
    winRateChart_ = new QtCharts::QChart();
    winRateChart_->setTitle("🎯 Distribution Win Rate");
    winRateChart_->setTheme(QtCharts::QChart::ChartThemeDark);
    
    winRateSeries_ = new QtCharts::QPieSeries();
    winRateSeries_->append("Wins", 60);
    winRateSeries_->append("Losses", 30);
    winRateSeries_->append("Ties", 10);
    winRateChart_->addSeries(winRateSeries_);
    
    winRateChartView_ = new QtCharts::QChartView(winRateChart_);
    winRateChartView_->setRenderHint(QPainter::Antialiasing);

    // Layout des graphiques
    auto chartsHLayout = new QHBoxLayout;
    chartsHLayout->addWidget(convergenceChartView_);
    chartsHLayout->addWidget(winRateChartView_);
    chartsLayout->addLayout(chartsHLayout);

    infoTabWidget_->addTab(chartsWidget, "📈 Graphiques");
}

// Implementation des slots
void MainWindow::startTraining() {
    if (appManager_) {
        trainingActive_ = true;
        startTrainingButton_->setEnabled(false);
        stopTrainingButton_->setEnabled(true);
        engineStatusLabel_->setText("CFR Engine: Training actif");
        logTextEdit_->append("🚀 Démarrage training CFR...");
        
        // Démarrage du training via AppManager
        // appManager_->startCfrTraining();
    }
}

void MainWindow::stopTraining() {
    trainingActive_ = false;
    startTrainingButton_->setEnabled(true);
    stopTrainingButton_->setEnabled(false);
    engineStatusLabel_->setText("CFR Engine: Arrêté");
    logTextEdit_->append("⏹️ Training CFR arrêté");
}

void MainWindow::startOCR() {
    if (appManager_) {
        ocrActive_ = true;
        startOCRButton_->setEnabled(false);
        stopOCRButton_->setEnabled(true);
        ocrStatusLabel_->setText("OCR: Actif");
        logTextEdit_->append("👁️ Démarrage OCR...");
    }
}

void MainWindow::stopOCR() {
    ocrActive_ = false;
    startOCRButton_->setEnabled(true);
    stopOCRButton_->setEnabled(false);
    ocrStatusLabel_->setText("OCR: Arrêté");
    logTextEdit_->append("👁️ OCR arrêté");
}

void MainWindow::setupTimers() {
    // Timer mise à jour état jeu (temps réel)
    gameStateTimer_ = new QTimer(this);
    connect(gameStateTimer_, &QTimer::timeout, this, &MainWindow::updateGameState);
    gameStateTimer_->start(1000); // 1 seconde

    // Timer stratégie (temps réel)
    strategyTimer_ = new QTimer(this);
    connect(strategyTimer_, &QTimer::timeout, this, &MainWindow::updateStrategy);
    strategyTimer_->start(2000); // 2 secondes

    // Timer statistiques (moins fréquent)
    statsTimer_ = new QTimer(this);
    connect(statsTimer_, &QTimer::timeout, this, &MainWindow::updateStatistics);
    statsTimer_->start(5000); // 5 secondes

    // Timer performance (monitoring)
    performanceTimer_ = new QTimer(this);
    connect(performanceTimer_, &QTimer::timeout, this, &MainWindow::updatePerformanceMetrics);
    performanceTimer_->start(3000); // 3 secondes
}

void MainWindow::applyDarkTheme() {
    setStyleSheet(
        "QMainWindow { "
        "    background-color: #2B2B2B; "
        "    color: #FFFFFF; "
        "} "
        "QWidget { "
        "    background-color: #2B2B2B; "
        "    color: #FFFFFF; "
        "} "
        "QTabWidget::pane { "
        "    border: 1px solid #555555; "
        "    background-color: #353535; "
        "} "
        "QTabBar::tab { "
        "    background-color: #404040; "
        "    color: #FFFFFF; "
        "    padding: 8px 12px; "
        "    margin: 2px; "
        "    border-top-left-radius: 6px; "
        "    border-top-right-radius: 6px; "
        "} "
        "QTabBar::tab:selected { "
        "    background-color: #4CAF50; "
        "    font-weight: bold; "
        "} "
        "QSplitter::handle { "
        "    background-color: #555555; "
        "} "
        "QMenuBar { "
        "    background-color: #353535; "
        "    color: #FFFFFF; "
        "} "
        "QMenuBar::item:selected { "
        "    background-color: #4CAF50; "
        "} "
        "QMenu { "
        "    background-color: #353535; "
        "    color: #FFFFFF; "
        "    border: 1px solid #555555; "
        "} "
        "QMenu::item:selected { "
        "    background-color: #4CAF50; "
        "} "
        "QStatusBar { "
        "    background-color: #353535; "
        "    color: #FFFFFF; "
        "    border-top: 1px solid #555555; "
        "} "
    );
}

// Stubs pour méthodes manquantes
void MainWindow::setupConnections() {}
void MainWindow::createSystemTray() {}
void MainWindow::newSession() {}
void MainWindow::openSession() {}
void MainWindow::saveSession() {}
void MainWindow::showPreferences() {}
void MainWindow::showAbout() {}
void MainWindow::exitApplication() { QApplication::quit(); }
void MainWindow::resetTraining() {}
void MainWindow::intensiveTraining() {}
void MainWindow::calibrateOCR() {}
void MainWindow::testOCR() {}
void MainWindow::updateGameState() {}
void MainWindow::updateStrategy() {}
void MainWindow::updateStatistics() {}
void MainWindow::updatePerformanceMetrics() {}
void MainWindow::showWindow() {}
void MainWindow::hideToTray() {}
void MainWindow::trayIconActivated(QSystemTrayIcon::ActivationReason) {}
void MainWindow::closeEvent(QCloseEvent *event) { event->accept(); }
void MainWindow::resizeEvent(QResizeEvent *event) { QMainWindow::resizeEvent(event); }
void MainWindow::updateWindowTitle() {}
void MainWindow::displayRecommendation(const Strategy&) {}
void MainWindow::displayGameInfo(const GameState&) {}
void MainWindow::displayPerformanceStats(const PerformanceStats&) {}

#include "MainWindow.moc"