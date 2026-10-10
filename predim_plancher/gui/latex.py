"""Rendu de formules LaTeX (via matplotlib mathtext) en images Qt."""

from functools import lru_cache
from io import BytesIO

from PySide6.QtGui import QPixmap


@lru_cache(maxsize=128)
def render_math(
    latex: str,
    fontsize: int = 16,
    dpi: int = 200,
    scale: float = 2.0,
) -> QPixmap | None:
    """Rend une expression LaTeX en :class:`QPixmap` (fond transparent).

    Renvoie ``None`` si matplotlib n'est pas disponible ou si le rendu échoue,
    afin de laisser l'appelant retomber sur un texte simple.
    """
    try:
        from matplotlib.font_manager import FontProperties
        from matplotlib.mathtext import math_to_image
    except Exception:  # noqa: BLE001 - dépendance optionnelle
        return None

    buffer = BytesIO()
    try:
        math_to_image(
            latex,
            buffer,
            prop=FontProperties(size=fontsize),
            dpi=dpi,
            format="png",
        )
    except Exception:  # noqa: BLE001 - expression invalide
        return None

    pixmap = QPixmap()
    if not pixmap.loadFromData(buffer.getvalue(), "PNG"):
        return None
    pixmap.setDevicePixelRatio(scale)
    return pixmap
