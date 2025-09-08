/**
 * Fenêtre principale Qt6 moderne
 * Remplacement de CustomTkinter par interface native haute performance
 */

#pragma once

#include <QMainWindow>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QLabel>
#include <QPushButton>
#include <QProgressBar>
#include <QTextEdit>
#include <QTableWidget>
#include <QTabWidget>
#include <QMenuBar>
#include <QStatusBar>
#include <QTimer>
#include <QSplitter>
#include <QtCharts>
#include <QSystemTrayIcon>
#include <memory>

#include "types/PokerTypes.h"
#include "types/ConfigTypes.h"

QT_BEGIN_NAMESPACE
class QAction;
class QMenu;
class QTextEdit;
QT_END_NAMESPACE

namespace rtpa::core {
    class AppManager;
}

namespace rtpa::gui {

class GameTable;
class ConfigDialog;
class StatsWidget;

/**
 * Fenêtre principale RTPA Studio
 * Interface moderne Qt6 avec thème sombre et réactivité optimale
 */
class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

    void setAppManager(rtpa::core::AppManager* manager);

protected:
    void closeEvent(QCloseEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;

private slots:
    // Menu actions
    void newSession();
    void openSession();
    void saveSession();
    void showPreferences();
    void showAbout();
    void exitApplication();

    // CFR Training
    void startTraining();
    void stopTraining();
    void resetTraining();
    void intensiveTraining();

    // OCR Control
    void startOCR();
    void stopOCR();
    void calibrateOCR();
    void testOCR();

    // Real-time updates
    void updateGameState();
    void updateStrategy();
    void updateStatistics();
    void updatePerformanceMetrics();

    // System tray
    void showWindow();
    void hideToTray();
    void trayIconActivated(QSystemTrayIcon::ActivationReason reason);

private:
    void createMenus();
    void createStatusBar();
    void createCentralWidget();
    void createSystemTray();
    void setupTimers();
    void setupConnections();
    void applyDarkTheme();

    // UI Update methods
    void updateWindowTitle();
    void displayRecommendation(const types::Strategy& strategy);
    void displayGameInfo(const types::GameState& state);
    void displayPerformanceStats(const types::PerformanceStats& stats);

    // Core components
    rtpa::core::AppManager* appManager_;

    // Central widget and layout
    QWidget* centralWidget_;
    QSplitter* mainSplitter_;
    QSplitter* rightSplitter_;

    // Main panels
    GameTable* gameTableWidget_;
    StatsWidget* statsWidget_;
    QTextEdit* logTextEdit_;
    QTabWidget* infoTabWidget_;

    // Strategy display
    QWidget* strategyWidget_;
    QGridLayout* strategyLayout_;
    std::vector<QPushButton*> actionButtons_;
    QLabel* recommendationLabel_;
    QLabel* winProbabilityLabel_;
    QLabel* expectedValueLabel_;

    // Performance monitoring
    QWidget* performanceWidget_;
    QLabel* cfrIterationsLabel_;
    QLabel* simulationsLabel_;
    QLabel* ocrOperationsLabel_;
    QProgressBar* cpuUsageBar_;
    QProgressBar* memoryUsageBar_;
    QProgressBar* gpuUsageBar_;

    // Charts
    QtCharts::QChart* convergenceChart_;
    QtCharts::QLineSeries* convergenceSeries_;
    QtCharts::QChartView* convergenceChartView_;

    QtCharts::QChart* winRateChart_;
    QtCharts::QPieSeries* winRateSeries_;
    QtCharts::QChartView* winRateChartView_;

    // Control panels
    QWidget* controlWidget_;
    QPushButton* startTrainingButton_;
    QPushButton* stopTrainingButton_;
    QPushButton* resetButton_;
    QPushButton* intensiveButton_;
    
    QPushButton* startOCRButton_;
    QPushButton* stopOCRButton_;
    QPushButton* calibrateButton_;
    QPushButton* testOCRButton_;

    // Menu and actions
    QMenuBar* menuBar_;
    QMenu* fileMenu_;
    QMenu* cfrMenu_;
    QMenu* ocrMenu_;
    QMenu* toolsMenu_;
    QMenu* helpMenu_;

    QAction* newAction_;
    QAction* openAction_;
    QAction* saveAction_;
    QAction* preferencesAction_;
    QAction* exitAction_;

    QAction* startTrainingAction_;
    QAction* stopTrainingAction_;
    QAction* intensiveTrainingAction_;

    QAction* calibrateOCRAction_;
    QAction* aboutAction_;

    // Status bar
    QStatusBar* statusBar_;
    QLabel* engineStatusLabel_;
    QLabel* ocrStatusLabel_;
    QLabel* performanceLabel_;

    // System tray
    QSystemTrayIcon* trayIcon_;
    QMenu* trayMenu_;
    QAction* showAction_;
    QAction* hideAction_;

    // Timers for real-time updates
    QTimer* gameStateTimer_;
    QTimer* strategyTimer_;
    QTimer* statsTimer_;
    QTimer* performanceTimer_;

    // State
    bool trainingActive_;
    bool ocrActive_;
    types::GameState currentGameState_;
    types::Strategy currentStrategy_;
    types::PerformanceStats currentStats_;

    // Configuration
    types::UIConfig uiConfig_;
};

} // namespace rtpa::gui