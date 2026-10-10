"""Icône de l'application, générée à l'exécution (aucun fichier externe).

Motif : trois barres horizontales évoquant la coupe d'un plancher/poutre
sur fond bleu outremer, cohérent avec le thème « Le Corbusier ».
"""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap

_BASE_SIZE = 256

_APP_ICON: QIcon | None = None


def make_app_pixmap(size: int = _BASE_SIZE) -> QPixmap:
    """Dessine l'icône à la taille demandée."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = size * 0.06
    rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)

    # Fond : bleu outremer arrondi
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#2C4A7C"))
    painter.drawRoundedRect(rect, size * 0.18, size * 0.18)

    # Barres horizontales : coupe de plancher
    bar_colors = ("#FFFFFF", "#D6E4F0", "#D6E4F0")
    bar_widths = (0.74, 0.88, 0.6)
    bar_h = size * 0.075
    y0 = rect.top() + size * 0.26
    for i, (color, ratio) in enumerate(zip(bar_colors, bar_widths)):
        bar_w = rect.width() * ratio
        x = rect.center().x() - bar_w / 2
        y = y0 + i * (bar_h + size * 0.065)
        painter.setBrush(QColor(color))
        painter.drawRoundedRect(
            QRectF(x, y, bar_w, bar_h), size * 0.045, size * 0.045
        )

    painter.end()
    return pixmap


def make_app_icon() -> QIcon:
    """Icône déclinée aux tailles d'affichage standard."""
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(make_app_pixmap(size))
    return icon


def app_icon() -> QIcon:
    """Renvoie une icône unique mise en cache."""
    global _APP_ICON
    if _APP_ICON is None:
        _APP_ICON = make_app_icon()
    return _APP_ICON