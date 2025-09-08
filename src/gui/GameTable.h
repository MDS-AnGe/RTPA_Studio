/**
 * Widget table de jeu - Affichage visuel de l'état poker
 */

#pragma once

#include <QWidget>
#include <QPainter>
#include <QTimer>
#include "types/PokerTypes.h"

namespace rtpa::gui {

class GameTable : public QWidget {
    Q_OBJECT

public:
    explicit GameTable(QWidget *parent = nullptr);
    
    void updateGameState(const types::GameState& state);
    void updateStrategy(const types::Strategy& strategy);

protected:
    void paintEvent(QPaintEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;

private:
    void drawTable(QPainter& painter);
    void drawCards(QPainter& painter);
    void drawPot(QPainter& painter);
    void drawRecommendation(QPainter& painter);

    types::GameState gameState_;
    types::Strategy currentStrategy_;
};

} // namespace rtpa::gui