"""Fenêtre principale de l'application de prédimensionnement.

Design : deux colonnes (saisie à gauche ~35 %, analyse à droite ~65 %),
cartes blanches ombrées, formules LaTeX, tableau de résultats coloré.
"""

from typing import Any

from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from ..core import AppuisPlancher, predim_compare
from ..logging_setup import get_logger
from . import styles
from .icons import app_icon
from .widgets import (
    Card,
    CollapsibleCard,
    GroupHeaderBand,
    MathLabel,
    PlaceholderSpinBox,
    make_item,
)

log = get_logger()

# Le script est dédié aux planchers à appuis continus.
APPUIS: AppuisPlancher = AppuisPlancher.Continu

COLUMNS = [
    "N°", "Lx (m)", "Ly (m)", "α",
    "Ép. (cm)", "Comportement",
    "Ép. (cm)", "Désignation",
]

FORMULES = [
    ("Corps creux :", r"$e = \dfrac{L_x}{22{,}5}$"),
    ("Dalle pleine — appuis simples :", r"$e = \dfrac{L_x}{20}$"),
    ("Dalle pleine — α < 0,4 (1 sens) :", r"$e = \dfrac{L_x}{30}$"),
    ("Dalle pleine — α ≥ 0,4 (2 sens) :", r"$e = \dfrac{L_x}{40}$"),
]

# Largeurs minimales (px) et pondérations pour répartir l'espace restant.
# Les colonnes sont calculées à partir de la largeur disponible : jamais
# de barre de défilement horizontale.
RESULT_MIN_WIDTHS = (34, 54, 54, 48, 62, 120, 62, 90)
RESULT_WEIGHTS = (1, 2, 2, 2, 3, 6, 3, 4)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Prédimensionnement Planchers — DP vs CC")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(940, 600)
        self.resize(940, 600)

        # Dimensions saisies (lx <= ly), alimentées par la zone d'ajout
        self._dimensions: list[tuple[float, float]] = []

        self.setFont(QFont(styles.FONT, 10))

        palette = self.palette()
        palette.setColor(QPalette.WindowText, QColor(styles.TEXT_DARK))
        palette.setColor(QPalette.Text, QColor(styles.TEXT_DARK))
        palette.setColor(QPalette.ButtonText, QColor(styles.TEXT_DARK))
        palette.setColor(QPalette.PlaceholderText, QColor(styles.PLACEHOLDER))
        self.setPalette(palette)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        self.setStyleSheet(styles.app_background_style())

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 14, 16, 10)
        main_layout.setSpacing(12)

        main_layout.addWidget(self._build_header())

        columns = QHBoxLayout()
        columns.setSpacing(14)
        columns.addWidget(self._build_input_card(), 30)
        columns.addLayout(self._build_analysis_column(), 70)
        main_layout.addLayout(columns, stretch=1)

        self.status = self.statusBar()
        self.status.setStyleSheet(styles.status_bar_style())

        # Signature en bas à droite (widget permanent de la barre de statut)
        self.signature = QLabel("© 2026 R. Stellia")
        self.signature.setStyleSheet(styles.signature_style())
        self.status.addPermanentWidget(self.signature)

        self._set_status("Prêt. Saisissez les portées puis cliquez sur « Calculer ».")

        log.info(
            "Fenêtre principale initialisée (%d x %d)",
            self.width(), self.height(),
        )
        QTimer.singleShot(0, self._sync_group_columns)

    # ------------------------------------------------------------------
    # En-tête
    # ------------------------------------------------------------------
    def _build_header(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(2)

        titre = QLabel("Prédimensionnement de planchers")
        titre.setStyleSheet(
            f"color: {styles.TEXT_TITLE}; font-size: 17pt; font-weight: bold;"
        )
        sous_titre = QLabel(
            "Comparaison dalle pleine vs plancher à corps creux"
        )
        sous_titre.setStyleSheet(styles.hint_style())

        layout.addWidget(titre)
        layout.addWidget(sous_titre)
        return widget

    # ------------------------------------------------------------------
    # Colonne gauche — saisie
    # ------------------------------------------------------------------
    def _build_input_card(self) -> Card:
        card = Card("Données d'entrée")
        card.body.setSpacing(8)

        row_input = QHBoxLayout()
        row_input.setSpacing(6)
        box_lx, self.spin_dim1 = self._build_field("Lx (m)")
        box_ly, self.spin_dim2 = self._build_field("Ly (m)")

        self.btn_ajouter = QPushButton("Ajouter")
        self.btn_ajouter.setStyleSheet(styles.accent_small_button_style())
        self.btn_ajouter.setCursor(Qt.PointingHandCursor)
        self.btn_ajouter.setFixedSize(78, 34)
        self.btn_ajouter.clicked.connect(self.on_ajouter_dimension)

        row_input.addWidget(box_lx)
        row_input.addWidget(box_ly)
        row_input.addWidget(self.btn_ajouter, 0, Qt.AlignBottom)
        row_input.addStretch()
        card.body.addLayout(row_input)

        # La touche Entrée déclenche l'ajout
        self.spin_dim1.lineEdit().returnPressed.connect(self.on_ajouter_dimension)
        self.spin_dim2.lineEdit().returnPressed.connect(self.on_ajouter_dimension)

        card.body.addWidget(self._subtitle("Planchers ajoutés"))
        card.body.addWidget(self._build_dim_table(), 1)

        # Barre d'actions : Calculer (bleu canard) + Effacer (outline terracotta)
        self.btn_calc = QPushButton("Calculer")
        self.btn_calc.setStyleSheet(styles.primary_button_style())
        self.btn_calc.setCursor(Qt.PointingHandCursor)
        self.btn_calc.setMinimumHeight(38)
        self.btn_calc.clicked.connect(self.on_calculer)

        self.btn_clear = QPushButton("Effacer")
        self.btn_clear.setStyleSheet(styles.danger_button_style())
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.setMinimumHeight(36)
        self.btn_clear.clicked.connect(self.on_effacer)

        card.body.addWidget(self.btn_calc)
        card.body.addWidget(self.btn_clear)
        return card

    def _build_field(self, placeholder: str) -> tuple[QWidget, QDoubleSpinBox]:
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        label = QLabel(placeholder)
        label.setStyleSheet(styles.field_label_style())

        spin = PlaceholderSpinBox()
        spin.setRange(0.0, 100.0)
        spin.setDecimals(2)
        spin.setSingleStep(0.5)
        spin.setValue(0.0)
        # Trace chaque modification de valeur (saisie, flèches, reset).
        spin.valueChanged.connect(
            lambda valeur, champ=placeholder: log.debug(
                "Saisie %s : %.2f", champ, valeur
            )
        )
        # Champ compact (place pour « 00.00 » + flèches), 34 px de haut
        spin.setMinimumWidth(72)
        spin.setMaximumWidth(92)
        spin.setFixedHeight(34)

        layout.addWidget(label)
        layout.addWidget(spin)
        return box, spin

    def _build_dim_table(self) -> QTableWidget:
        table = QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(["Lx (m)", "Ly (m)", ""])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setStyleSheet(styles.dim_table_style())
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setTextElideMode(Qt.ElideRight)
        table.verticalHeader().setDefaultSectionSize(34)
        # Remplit toute la largeur disponible de la carte
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        table.setColumnWidth(2, 40)

        self.table_dims = table
        return table

    # ------------------------------------------------------------------
    # Colonne droite — analyse
    # ------------------------------------------------------------------
    def _build_analysis_column(self) -> QVBoxLayout:
        column = QVBoxLayout()
        column.setSpacing(12)
        # Résultats en haut (zone principale), formules repliables en bas.
        column.addWidget(self._build_result_card(), 1)
        column.addWidget(self._build_formula_card(), 0)
        return column

    def _build_formula_card(self) -> CollapsibleCard:
        # Section repliable ; repliée par défaut pour laisser place aux résultats.
        card = CollapsibleCard("Formules de prédimensionnement utilisées", collapsed=True)
        card.content_layout.addWidget(
            self._muted("Épaisseurs minimales en centimètres (Lx en mètres).")
        )

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)
        for row, (description, latex) in enumerate(FORMULES):
            label = QLabel(description)
            label.setStyleSheet(
                f"color: {styles.TEXT_DARK}; font-size: 11pt;"
            )
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            grid.addWidget(label, row, 0)

            math = MathLabel(latex, fallback=latex.replace("$", ""), fontsize=12)
            grid.addWidget(math, row, 1)
        grid.setColumnStretch(1, 1)
        card.content_layout.addLayout(grid)
        card.content_layout.addStretch()

        # L'état réel est déjà basculé par le handler interne au moment de ce slot.
        card._header.clicked.connect(
            lambda: log.info(
                "Carte « Formules de prédimensionnement » %s",
                "repliée" if card.is_collapsed() else "dépliée",
            )
        )
        return card

    def _build_result_card(self) -> Card:
        card = Card("Résultats")
        card.body.setSpacing(0)
        # Zone principale : occupe tout l'espace vertical disponible.
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.grp_band = GroupHeaderBand(
            column_count=len(COLUMNS),
            groups=[
                (4, 2, "Dalle pleine", styles.DP_HEADER_BG),
                (6, 2, "Plancher à corps creux", styles.CC_HEADER_BG),
            ],
        )
        card.body.addWidget(self.grp_band)

        self.table = QTableWidget()
        self.table.setColumnCount(len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(styles.table_style())
        # Remplit toute la largeur et la hauteur de la carte
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Jamais de défilement horizontal : texte tronqué (infobulle au survol)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setTextElideMode(Qt.ElideRight)
        # Hauteur de ligne uniforme et compacte (6+ lignes visibles)
        self.table.verticalHeader().setDefaultSectionSize(34)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setStretchLastSection(False)
        # Refit si la largeur utile change (ex. apparition de la barre verticale)
        self.table.viewport().installEventFilter(self)

        card.body.addWidget(self.table, 1)
        return card

    # ------------------------------------------------------------------
    # Petits helpers de libellés
    # ------------------------------------------------------------------
    @staticmethod
    def _muted(text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(styles.hint_style())
        label.setWordWrap(True)
        return label

    @staticmethod
    def _subtitle(text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(styles.subtitle_style())
        return label

    # ------------------------------------------------------------------
    # Alignement du bandeau de regroupement
    # ------------------------------------------------------------------
    def _fit_columns(self) -> None:
        """Répartit exactement la largeur disponible entre les colonnes.

        Chaque colonne reçoit sa largeur minimale, puis l'espace restant est
        distribué selon les pondérations ; si la place manque, tout est réduit
        proportionnellement. La somme égale toujours la largeur du viewport.
        """
        view = self.table.viewport().width()
        if view <= 0:
            return
        mins = RESULT_MIN_WIDTHS
        total_min = sum(mins)
        if view <= total_min:
            widths = [max(int(m * view / total_min), 1) for m in mins]
        else:
            extra = view - total_min
            s = sum(RESULT_WEIGHTS)
            widths = [m + int(extra * w / s)
                      for m, w in zip(mins, RESULT_WEIGHTS)]
        # Le reliquat d'arrondi va à la dernière colonne
        widths[-1] += view - sum(widths)

        header = self.table.horizontalHeader()
        header.blockSignals(True)
        for i, w in enumerate(widths):
            self.table.setColumnWidth(i, w)
        header.blockSignals(False)
        self._sync_group_columns()

    def _sync_group_columns(self) -> None:
        if hasattr(self, "grp_band"):
            self.grp_band.sync_to(self.table)

    def eventFilter(self, obj, event) -> bool:  # noqa: N802 - API Qt
        if (
            hasattr(self, "table")
            and obj is self.table.viewport()
            and event.type() == QEvent.Resize
        ):
            self._fit_columns()
        return super().eventFilter(obj, event)

    def showEvent(self, event) -> None:  # noqa: N802 - API Qt
        super().showEvent(event)
        QTimer.singleShot(0, self._fit_columns)

    def closeEvent(self, event) -> None:  # noqa: N802 - API Qt
        log.info("Application fermée par l'utilisateur")
        super().closeEvent(event)

    # ------------------------------------------------------------------
    # Statut
    # ------------------------------------------------------------------
    def _set_status(self, message: str) -> None:
        self.status.showMessage(message)

    # ------------------------------------------------------------------
    # Gestion des dimensions
    # ------------------------------------------------------------------
    def on_ajouter_dimension(self) -> None:
        d1 = self.spin_dim1.value()
        d2 = self.spin_dim2.value()
        lx, ly = min(d1, d2), max(d1, d2)
        if lx <= 0 or d2 <= 0:
            log.warning("Ajout refusé : portées invalides (Lx=%.2f, Ly=%.2f)", d1, d2)
            QMessageBox.warning(
                self, "Dimension invalide",
                "Les deux portées doivent être strictement positives.",
            )
            return
        self._dimensions.append((lx, ly))
        log.info("Plancher ajouté : Lx=%.2f m, Ly=%.2f m", lx, ly)
        self._refresh_dim_table()
        self.spin_dim1.setValue(0.0)
        self.spin_dim2.setValue(0.0)
        self.spin_dim1.setFocus()
        self._set_status(
            f"Dimension ajoutée (Lx = {lx:.2f} m ; Ly = {ly:.2f} m)."
        )

    def on_supprimer_dimension(self, index: int) -> None:
        if 0 <= index < len(self._dimensions):
            lx, ly = self._dimensions[index]
            log.info(
                "Plancher supprimé (index %d) : Lx=%.2f m, Ly=%.2f m",
                index, lx, ly,
            )
            self._dimensions.pop(index)
            self._refresh_dim_table()
            self._set_status("Plancher supprimé.")

    def _refresh_dim_table(self) -> None:
        self.table_dims.setRowCount(0)
        for index, (lx, ly) in enumerate(self._dimensions):
            row = self.table_dims.rowCount()
            self.table_dims.insertRow(row)
            self.table_dims.setItem(
                row, 0, make_item(f"{lx:.2f}", align=Qt.AlignCenter)
            )
            self.table_dims.setItem(
                row, 1, make_item(f"{ly:.2f}", align=Qt.AlignCenter)
            )

            btn_del = QPushButton("✕")
            btn_del.setObjectName("btnSuppr")
            btn_del.setFixedSize(22, 22)
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.setToolTip("Supprimer ce plancher")
            btn_del.setStyleSheet(styles.delete_button_style())
            btn_del.clicked.connect(
                lambda _=False, i=index: self.on_supprimer_dimension(i)
            )

            holder = QWidget()
            holder_layout = QHBoxLayout(holder)
            holder_layout.setContentsMargins(2, 0, 2, 0)
            holder_layout.addWidget(btn_del, 0, Qt.AlignCenter)
            self.table_dims.setCellWidget(row, 2, holder)

    def _set_dimensions(self, dimensions: list[tuple[float, float]]) -> None:
        self._dimensions = list(dimensions)
        self._refresh_dim_table()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def on_effacer(self) -> None:
        log.info(
            "Effacement de %d plancher(s) et des résultats",
            len(self._dimensions),
        )
        self._set_dimensions([])
        self.table.setRowCount(0)
        self._set_status("Champs effacés.")

    def on_calculer(self) -> None:
        if not self._dimensions:
            log.warning("Calcul annulé : aucune dimension saisie")
            QMessageBox.warning(
                self, "Saisie vide",
                "Veuillez ajouter au moins un plancher.",
            )
            return

        try:
            resultats = predim_compare(self._dimensions, APPUIS)
        except Exception as e:  # noqa: BLE001 - remonté à l'utilisateur
            log.exception("Échec du calcul : %s", e)
            QMessageBox.critical(self, "Erreur de calcul", str(e))
            return

        self._remplir_tableau(resultats)
        depasse = [r["nom"] for r in resultats if r.get("cc_max_depasse")]
        if depasse:
            noms = ", ".join(depasse)
            log.warning(
                "Épaisseur max du corps creux (30 cm) dépassée pour : %s",
                noms,
            )
            self._set_status(
                f"Attention : épaisseur max du corps creux (30 cm) "
                f"dépassée pour {noms}."
            )
        else:
            log.info("Calcul effectué pour %d plancher(s)", len(resultats))
            self._set_status(f"{len(resultats)} plancher(s) calculé(s).")

    # ------------------------------------------------------------------
    # Remplissage du tableau de résultats
    # ------------------------------------------------------------------
    def _remplir_tableau(self, resultats: list[dict[str, Any]]) -> None:
        self.table.setRowCount(len(resultats))

        col_dp = QColor(styles.DP_CELL_BG)
        col_cc = QColor(styles.CC_CELL_BG)
        col_err = QColor(styles.ERROR_CELL_BG)
        fg_err = QColor(styles.ERROR_TEXT)
        col_dp_max = QColor(styles.DP_MAX_BG)
        col_cc_max = QColor(styles.CC_MAX_BG)

        # Épaisseurs maximales à mettre en évidence (tous les ex æquo)
        dp_vals = [r["dp_ep"] for r in resultats if r["dp_statut"] == "Succès"]
        cc_vals = [r["cc_ep"] for r in resultats if r["cc_statut"] == "Succès"]
        max_dp = max(dp_vals) if dp_vals else None
        max_cc = max(cc_vals) if cc_vals else None

        for row, r in enumerate(resultats):
            items = [
                make_item(f"{row + 1}", align=Qt.AlignCenter, bold=True),
                make_item(f"{r['lx']:.2f}", align=Qt.AlignCenter),
                make_item(f"{r['ly']:.2f}", align=Qt.AlignCenter),
                make_item(f"{r['alpha']:.2f}", align=Qt.AlignCenter),
            ]

            if r["dp_statut"] == "Succès":
                is_max = r["dp_ep"] == max_dp
                badge = f" {styles.MAX_BADGE}" if is_max else ""
                items.append(make_item(
                    f"{r['dp_ep']:.0f}{badge}", align=Qt.AlignCenter,
                    bold=is_max, bg=col_dp_max if is_max else col_dp,
                    tooltip="Épaisseur maximale (Dalle pleine)" if is_max else "",
                ))
                items.append(make_item(r["dp_details"], bg=col_dp,
                                       tooltip=r["dp_details"]))
            else:
                items.append(make_item("—", align=Qt.AlignCenter,
                                       bg=col_err, fg=fg_err))
                items.append(make_item(r["dp_statut"], bg=col_err, fg=fg_err,
                                       tooltip=r["dp_statut"]))

            if r["cc_statut"] == "Succès":
                is_max = r["cc_ep"] == max_cc
                badge = f" {styles.MAX_BADGE}" if is_max else ""
                over = bool(r["cc_max_depasse"])
                if over:
                    tip = (
                        f"Épaisseur requise {r['cc_min_cm']:.1f} cm dépasse "
                        "le maximum du corps creux (30 cm)."
                    )
                else:
                    tip = (
                        "Épaisseur maximale (Corps creux)" if is_max else ""
                    )
                items.append(make_item(
                    f"{r['cc_ep']:.0f}{badge}", align=Qt.AlignCenter,
                    bold=is_max, bg=col_cc_max if is_max else col_cc,
                    tooltip=tip,
                ))
                if over:
                    items.append(make_item(
                        f"{r['cc_format']} ⚠", align=Qt.AlignCenter,
                        bold=True, bg=QColor(styles.DANGER_BG),
                        fg=QColor(styles.DANGER_TEXT), tooltip=tip,
                    ))
                else:
                    items.append(make_item(r["cc_format"], align=Qt.AlignCenter,
                                           bold=True, bg=col_cc))
            else:
                items.append(make_item("—", align=Qt.AlignCenter,
                                       bg=col_err, fg=fg_err))
                items.append(make_item(r["cc_statut"], bg=col_err, fg=fg_err,
                                       tooltip=r["cc_statut"]))

            for col, item in enumerate(items):
                self.table.setItem(row, col, item)

        self._fit_columns()


def application() -> QApplication:
    """Renvoie l'instance unique de :class:`QApplication`."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        app.setStyle("Fusion")
        app.setWindowIcon(app_icon())
    return app
