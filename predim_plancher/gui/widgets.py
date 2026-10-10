"""Widgets personnalisés réutilisables par l'interface."""

from PySide6.QtCore import QEvent, QPointF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QPainter, QPolygonF
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QDoubleSpinBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QHeaderView,
    QLabel,
    QPushButton,
    QStyle,
    QStyleOptionSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from . import styles
from .latex import render_math


def make_item(
    text: str,
    align: int = Qt.AlignLeft | Qt.AlignVCenter,
    bold: bool = False,
    bg: QColor | None = None,
    fg: QColor | None = None,
    tooltip: str | None = None,
) -> QTableWidgetItem:
    """Construit un :class:`QTableWidgetItem` formaté."""
    item = QTableWidgetItem(str(text))
    item.setTextAlignment(align)
    if bold:
        font = item.font()
        font.setBold(True)
        item.setFont(font)
    if bg is not None:
        item.setBackground(QBrush(bg))
    if fg is not None:
        item.setForeground(QBrush(fg))
    if tooltip:
        item.setToolTip(tooltip)
    return item


class GroupHeaderBand(QTableWidget):
    """Bandeau de regroupement de colonnes, affiché au-dessus de l'en-tête.

    Chaque groupe est un tuple ``(colonne_de_départ, largeur, texte, couleur)``.
    """

    def __init__(
        self,
        column_count: int,
        groups: list[tuple[int, int, str, str]],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("grpTable")
        self.setColumnCount(column_count)
        self.setRowCount(1)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)
        self.setShowGrid(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(styles.group_header_style())

        for column in range(column_count):
            self.horizontalHeader().setSectionResizeMode(
                column, QHeaderView.Fixed
            )

        for start, span, text, color in groups:
            self.setItem(
                0,
                start,
                make_item(text, align=Qt.AlignCenter, bold=True,
                          bg=QColor(color), fg=QColor(styles.HEADER_TEXT)),
            )
            self.setSpan(0, start, 1, span)

        self.setFixedHeight(28)

    def sync_to(self, table: QTableWidget) -> None:
        """Aligne le bandeau sur les colonnes du tableau de résultats."""
        self.setFixedWidth(table.viewport().width())
        for column in range(table.columnCount()):
            self.setColumnWidth(column, table.columnWidth(column))


class Card(QFrame):
    """Carte blanche à coins arrondis avec ombre portée légère.

    Le contenu se place dans ``card.body`` (un :class:`QVBoxLayout`).
    """

    def __init__(self, title: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(styles.card_style())

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(22)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(60, 50, 35, 35))
        self.setGraphicsEffect(shadow)

        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(16, 12, 16, 12)
        self.body.setSpacing(9)

        if title:
            label = QLabel(title)
            label.setStyleSheet(styles.card_title_style())
            self.body.addWidget(label)


class CollapsibleCard(Card):
    """Carte dont le contenu peut être replié/déplié via son titre.

    Le contenu se place dans ``card.content_layout``. État initial : replié.
    """

    def __init__(self, title: str, collapsed: bool = True, parent=None) -> None:
        super().__init__("", parent)
        self._title = title
        self.body.setSpacing(6)

        self._header = QPushButton()
        self._header.setObjectName("collapseHeader")
        self._header.setCursor(Qt.PointingHandCursor)
        self._header.setCheckable(True)
        self._header.setStyleSheet(styles.collapse_header_style())
        self._header.clicked.connect(self._on_header_clicked)
        self.body.addWidget(self._header)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(2, 0, 2, 0)
        self.content_layout.setSpacing(10)
        self.body.addWidget(self.content)

        self._collapsed = collapsed
        self.set_collapsed(collapsed)

    def _on_header_clicked(self) -> None:
        self.set_collapsed(not self._collapsed)

    def is_collapsed(self) -> bool:
        return self._collapsed

    def set_collapsed(self, collapsed: bool) -> None:
        self._collapsed = collapsed
        self.content.setVisible(not collapsed)
        self._header.setChecked(not collapsed)
        arrow = "▶" if collapsed else "▼"
        self._header.setText(f"{arrow}   {self._title}")


class PlaceholderSpinBox(QDoubleSpinBox):
    """Spinbox décimal avec « 0.00 » grisé façon placeholder et flèches ▲▼.

    - Tant que la valeur vaut 0, le texte est grisé ; dès qu'une valeur est
      saisie, il reprend la couleur normale du thème.
    - Au focus, tout le texte est sélectionné : la frappe *remplace* « 0.00 »
      au lieu de s'y ajouter (pas de « 0.005 » en tapant 5).
    - Les flèches haut/bas sont dessinées ici (aucun fichier image requis).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.setKeyboardTracking(False)
        self.setStyleSheet(styles.spin_style())
        self.lineEdit().installEventFilter(self)
        self.valueChanged.connect(lambda _v: self._refresh_empty_flag())
        self._refresh_empty_flag()

    # -- placeholder ------------------------------------------------------
    def _refresh_empty_flag(self) -> None:
        empty = self.value() == 0.0
        if self.property("empty") != empty:
            self.setProperty("empty", empty)
            # Force la réévaluation de la feuille de style (sélecteur [empty])
            self.style().unpolish(self)
            self.style().polish(self)

    # -- sélection au focus ----------------------------------------------
    def eventFilter(self, obj, event) -> bool:  # noqa: N802 - API Qt
        if obj is self.lineEdit() and event.type() == QEvent.FocusIn:
            # Différé : le clic souris repositionne le curseur après le focus.
            QTimer.singleShot(0, self.lineEdit().selectAll)
        return super().eventFilter(obj, event)

    # -- flèches ▲ ▼ -------------------------------------------------------
    def paintEvent(self, event) -> None:  # noqa: N802 - API Qt
        super().paintEvent(event)

        opt = QStyleOptionSpinBox()
        self.initStyleOption(opt)
        style = self.style()
        enabled = self.stepEnabled()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        for sub, up, flag in (
            (QStyle.SC_SpinBoxUp, True, QAbstractSpinBox.StepUpEnabled),
            (QStyle.SC_SpinBoxDown, False, QAbstractSpinBox.StepDownEnabled),
        ):
            rect = style.subControlRect(QStyle.CC_SpinBox, opt, sub, self)
            if rect.isEmpty():
                continue
            active = bool(enabled & flag) and self.isEnabled()
            painter.setBrush(QColor(styles.ACCENT if active else "#C9CED6"))
            cx, cy = rect.center().x() + 0.5, rect.center().y() + 0.5
            w, h = 3.5, 2.5
            if up:
                pts = [QPointF(cx - w, cy + h), QPointF(cx + w, cy + h),
                       QPointF(cx, cy - h)]
            else:
                pts = [QPointF(cx - w, cy - h), QPointF(cx + w, cy - h),
                       QPointF(cx, cy + h)]
            painter.drawPolygon(QPolygonF(pts))
        painter.end()


class MathLabel(QLabel):
    """QLabel affichant une formule LaTeX rendue en image.

    Si le rendu LaTeX est indisponible, retombe sur ``fallback`` (texte simple).
    """

    def __init__(
        self,
        latex: str,
        fallback: str = "",
        fontsize: int = 16,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        pixmap = render_math(latex, fontsize)
        if pixmap is not None:
            self.setPixmap(pixmap)
            self.setToolTip(fallback or latex)
        else:
            self.setText(fallback or latex)
