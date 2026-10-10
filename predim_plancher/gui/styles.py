"""Design system : palette et feuilles de style (QSS).

Ambiance « Le Corbusier » : fond blanc ivoire, cartes blanches ombrées,
bleu outremer pour les titres, vert olive pour les actions positives,
terracotta pour les actions destructives et ocre chaud pour le corps creux.
"""

# --------------------------------------------------------------------------
# Palette — thème « Le Corbusier »
# --------------------------------------------------------------------------
BG_APP = "#F5F3EF"          # fond ivoire
CARD_BG = "#FFFFFF"         # fond des cartes
BORDER = "#E7E1D6"
BORDER_FOCUS = "#3B5998"
DIVIDER = "#EFEBE3"

TEXT_TITLE = "#2C4A7C"      # titres — bleu outremer
TEXT_DARK = "#4A4A4A"       # libellés / texte courant
TEXT_MUTED = "#8A8A8A"      # unités / indications
PLACEHOLDER = "#A9A29A"

ACCENT = "#2C4A7C"          # bleu outremer — comme l'en-tête du tableau
ACCENT_HOVER = "#3B5998"
ACCENT_PRESSED = "#22395F"

SUCCESS = "#5A8A6B"         # action positive — vert olive
SUCCESS_HOVER = "#4C7759"
SUCCESS_PRESSED = "#3F654B"

DANGER = "#B85C4A"          # action destructive — terre cuite
DANGER_HOVER = "#A44E3D"
DANGER_PRESSED = "#8E4234"
DANGER_BG = "#FBEDE9"
DANGER_BORDER = "#E6C3B8"
DANGER_TEXT = "#8E4234"

# En-têtes de section / fonds de cellules
DP_HEADER_BG = "#D6E4F0"    # bleu pâle (dalle pleine)
CC_HEADER_BG = "#E8A857"    # ocre chaud (corps creux)
DP_CELL_BG = "#EAF1F9"
CC_CELL_BG = "#FCF2E2"
ERROR_CELL_BG = "#FBEDE9"
ERROR_TEXT = "#8E4234"
HEADER_TEXT = "#000000"

# Mise en évidence des épaisseurs maximales
DP_MAX_BG = "#FFF3CD"       # jaune pâle (Dalle pleine max)
CC_MAX_BG = "#FDE2E4"       # rose pâle (Corps creux max)
MAX_BADGE = "★"

SELECTION_BG = "#DCE8F5"
SELECTION_TEXT = "#2C4A7C"
ALTERNATE_ROW_BG = "#F8F6F1"
TABLE_HEADER_BG = "#2C4A7C"

FONT = "Segoe UI"


# --------------------------------------------------------------------------
# Application / cartes
# --------------------------------------------------------------------------
def app_background_style() -> str:
    return (
        f"#central {{ background: {BG_APP}; }} "
        f"QMainWindow {{ background: {BG_APP}; }}"
    )


def card_style() -> str:
    return f"""
        QFrame#card {{
            background: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 12px;
        }}
    """


def card_title_style() -> str:
    return (
        f"color: {TEXT_TITLE}; font-size: 11.5pt; font-weight: bold; "
        "padding: 0;"
    )


def hint_style() -> str:
    return f"color: {TEXT_MUTED}; font-size: 9.5pt;"


def field_label_style() -> str:
    return f"color: {TEXT_DARK}; font-size: 10pt; font-weight: 600;"


def subtitle_style() -> str:
    return f"color: {TEXT_TITLE}; font-size: 9.5pt; font-weight: bold;"


# --------------------------------------------------------------------------
# Champs de saisie
# --------------------------------------------------------------------------
def spin_style() -> str:
    return f"""
        QDoubleSpinBox {{
            color: {TEXT_DARK};
            background: #ffffff;
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 4px 4px 4px 8px;
            font-size: 11pt;
            selection-background-color: {SELECTION_BG};
            selection-color: {SELECTION_TEXT};
        }}
        /* Valeur à 0 : texte grisé façon « placeholder » */
        QDoubleSpinBox[empty="true"] {{ color: {PLACEHOLDER}; }}
        QDoubleSpinBox:hover {{ border: 1px solid #c8d3e6; }}
        QDoubleSpinBox:focus {{ border: 1px solid {BORDER_FOCUS}; }}
        /* Boutons haut / bas : les triangles sont dessinés par
           PlaceholderSpinBox.paintEvent (aucun fichier image). */
        QDoubleSpinBox::up-button {{
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 18px;
            border: none;
            border-left: 1px solid {BORDER};
            border-top-right-radius: 7px;
            background: {BG_APP};
        }}
        QDoubleSpinBox::down-button {{
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 18px;
            border: none;
            border-left: 1px solid {BORDER};
            border-top: 1px solid {BORDER};
            border-bottom-right-radius: 7px;
            background: {BG_APP};
        }}
        QDoubleSpinBox::up-button:hover,
        QDoubleSpinBox::down-button:hover {{ background: {DP_CELL_BG}; }}
        QDoubleSpinBox::up-button:pressed,
        QDoubleSpinBox::down-button:pressed {{ background: {SELECTION_BG}; }}
        QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {{
            width: 0; height: 0; image: none;
        }}
    """


# --------------------------------------------------------------------------
# Boutons
# --------------------------------------------------------------------------
def _button_style(bg: str, hover: str, pressed: str, fg: str = "white",
                  border: str = "none", padding: str = "8px 16px",
                  radius: str = "8px") -> str:
    return f"""
        QPushButton {{
            background-color: {bg};
            color: {fg};
            border: {border};
            padding: {padding};
            border-radius: {radius};
            font-weight: bold;
            font-size: 11pt;
        }}
        QPushButton:hover {{ background-color: {hover}; }}
        QPushButton:pressed {{ background-color: {pressed}; }}
        QPushButton:disabled {{ background-color: #e6eaf1; color: #aab3c0; }}
    """


def primary_button_style() -> str:
    return _button_style(ACCENT, ACCENT_HOVER, ACCENT_PRESSED)


def success_button_style() -> str:
    return _button_style(SUCCESS, SUCCESS_HOVER, SUCCESS_PRESSED)


def accent_small_button_style() -> str:
    # Variante compacte du bouton principal (Ajouter, sur la ligne des champs)
    return _button_style(
        ACCENT, ACCENT_HOVER, ACCENT_PRESSED,
        padding="6px 10px", radius="8px",
    )


def danger_button_style() -> str:
    return _button_style(
        DANGER_BG, DANGER_BG, DANGER_BG, fg=DANGER_TEXT,
        border=f"1px solid {DANGER_BORDER}",
    )


def ghost_button_style() -> str:
    return f"""
        QPushButton {{
            background: transparent; color: {ACCENT};
            border: 1px solid transparent; padding: 4px 8px;
            border-radius: 6px; font-weight: 600; font-size: 9.5pt;
        }}
        QPushButton:hover {{ background: {DP_CELL_BG}; }}
        QPushButton:pressed {{ background: {SELECTION_BG}; }}
    """


def delete_button_style() -> str:
    return f"""
        QPushButton#btnSuppr {{
            background: transparent; color: {TEXT_MUTED};
            border: none; font-size: 12pt; font-weight: normal;
            padding: 0;
        }}
        QPushButton#btnSuppr:hover {{
            color: {DANGER}; background: {DANGER_BG}; border-radius: 9px;
        }}
        QPushButton#btnSuppr:pressed {{ color: {DANGER_PRESSED}; }}
    """


def collapse_header_style() -> str:
    return f"""
        QPushButton#collapseHeader {{
            text-align: left;
            background: transparent;
            border: none;
            color: {TEXT_TITLE};
            font-size: 13pt;
            font-weight: bold;
            padding: 4px 2px;
            border-radius: 8px;
        }}
        QPushButton#collapseHeader:hover {{ background: {DP_CELL_BG}; }}
        QPushButton#collapseHeader:pressed {{ background: {SELECTION_BG}; }}
    """


# --------------------------------------------------------------------------
# Tableaux
# --------------------------------------------------------------------------
def dim_table_style() -> str:
    return f"""
        QTableWidget {{
            background: #ffffff;
            alternate-background-color: {ALTERNATE_ROW_BG};
            border: 1px solid {BORDER};
            border-radius: 10px;
            color: {TEXT_DARK};
            font-size: 11pt;
            gridline-color: {DIVIDER};
            selection-background-color: {SELECTION_BG};
            selection-color: {SELECTION_TEXT};
        }}
        QTableWidget::item {{ padding: 5px; }}
        QHeaderView::section {{
            background: {BG_APP};
            color: {TEXT_TITLE};
            padding: 6px 10px;
            border: none;
            border-bottom: 1px solid {BORDER};
            font-weight: bold;
            font-size: 10pt;
        }}
    """


def table_style() -> str:
    return f"""
        QTableWidget {{
            background: #ffffff;
            alternate-background-color: {ALTERNATE_ROW_BG};
            border: none;
            border-radius: 8px;
            color: {TEXT_DARK};
            font-size: 10pt;
            gridline-color: {DIVIDER};
            selection-background-color: {SELECTION_BG};
            selection-color: {SELECTION_TEXT};
        }}
        QTableWidget::item {{ padding: 5px 6px; }}
        QHeaderView::section {{
            background: {TABLE_HEADER_BG};
            color: white;
            padding: 6px 8px;
            border: none;
            font-weight: bold;
            font-size: 9.5pt;
        }}
    """


def group_header_style() -> str:
    return "QTableWidget#grpTable { border: none; background: #ffffff; }"


def status_bar_style() -> str:
    return (
        f"QStatusBar {{ color: {TEXT_DARK}; background: {BG_APP}; "
        f"border-top: 1px solid {BORDER}; font-size: 10pt; padding: 2px 8px; }}"
    )


def signature_style() -> str:
    return f"color: {TEXT_MUTED}; font-size: 6pt; padding-right: 2px;"
