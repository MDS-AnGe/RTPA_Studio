/**
 * Widget statistiques et métriques
 */

#pragma once

#include <QWidget>
#include <QVBoxLayout>
#include <QLabel>
#include "types/PokerTypes.h"

namespace rtpa::gui {

class StatsWidget : public QWidget {
    Q_OBJECT

public:
    explicit StatsWidget(QWidget *parent = nullptr);
    
    void updateStats(const types::PerformanceStats& stats);

private:
    QVBoxLayout* layout_;
    QLabel* cfrStatsLabel_;
    QLabel* ocrStatsLabel_;
    QLabel* performanceLabel_;
};

} // namespace rtpa::gui