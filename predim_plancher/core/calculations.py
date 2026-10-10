"""Calculs de prédimensionnement comparatif dalle pleine / corps creux."""

import logging
from typing import Any

from .enums import AppuisPlancher
from .models import Plancher

log = logging.getLogger("predim")


def predim_plancher(
    d1: float,
    d2: float,
    appuis: AppuisPlancher,
    nom: str = "P1",
) -> dict[str, Any]:
    """Prédimensionne un plancher pour les deux types (DP et CC).

    Renvoie un dictionnaire prêt à alimenter l'interface.
    """
    lx, ly = min(d1, d2), max(d1, d2)
    p = Plancher(name=nom, lx_m=lx, ly_m=ly, appuis_plancher=appuis)
    log.debug(
        "Calcul %s : portées %sLx=%.2f m, Ly=%.2f m, alpha=%.3f",
        nom, "2 sens " if p.alpha >= 0.4 else "1 sens ", lx, ly, p.alpha,
    )

    ligne: dict[str, Any] = {
        "nom": nom,
        "lx": lx,
        "ly": ly,
        "alpha": p.alpha,
        "dp_ep": None, "dp_details": None, "dp_statut": "Succès",
        "cc_ep": None, "cc_format": None, "cc_details": None,
        "cc_max_depasse": False, "cc_min_cm": None, "cc_statut": "Succès",
    }

    try:
        ligne["dp_ep"] = p.predim_dalle_pleine()
        ligne["dp_details"] = p.comportement_dp()
    except Exception as e:  # noqa: BLE001 - on remonte le message à l'UI
        ligne["dp_statut"] = str(e)
        log.error("Dalle pleine %s : %s", nom, e)

    try:
        ep_cc = p.predim_corps_creux()
        ligne["cc_ep"] = ep_cc
        ligne["cc_format"] = p.format_corps_creux(ep_cc)
        ligne["cc_details"] = p.comportement_cc()
        ligne["cc_max_depasse"] = p.depasse_max_cc
        ligne["cc_min_cm"] = p.epaisseur_min_cc
    except Exception as e:  # noqa: BLE001 - on remonte le message à l'UI
        ligne["cc_statut"] = str(e)
        log.error("Corps creux %s : %s", nom, e)

    dp = (
        f"{ligne['dp_ep']:.0f} cm ({ligne['dp_details']})"
        if ligne["dp_ep"] is not None
        else ligne["dp_statut"]
    )
    cc = (
        f"{ligne['cc_ep']} cm ({ligne['cc_format']})"
        if ligne["cc_ep"] is not None
        else ligne["cc_statut"]
    )
    log.info(
        "Résultat %s : Lx=%.2f m, Ly=%.2f m | DP %s | CC %s%s",
        nom, lx, ly, dp, cc,
        " — Épaisseur max du corps creux (30 cm) dépassée" if ligne["cc_max_depasse"] else "",
    )
    return ligne


def predim_compare(
    dimensions: list[tuple[float, float]],
    appuis: AppuisPlancher,
) -> list[dict[str, Any]]:
    """Prédimensionne une liste de planchers et renvoie leurs résultats."""
    log.debug("Prédimensionnement de %d plancher(s)", len(dimensions))
    return [
        predim_plancher(d1, d2, appuis, nom=f"P{i}")
        for i, (d1, d2) in enumerate(dimensions, start=1)
    ]
