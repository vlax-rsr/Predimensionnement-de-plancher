"""Modèle métier : le plancher et ses règles de prédimensionnement."""

import math
from dataclasses import dataclass

from .constants import CORPS_CREUX, M_TO_CM
from .enums import AppuisPlancher


@dataclass
class Plancher:
    """Un plancher rectangulaire défini par ses portées et ses appuis.

    Les portées sont réordonnées automatiquement : ``lx`` correspond toujours
    à la plus petite dimension et ``ly`` à la plus grande.
    """

    name: str
    lx_m: float
    ly_m: float
    appuis_plancher: AppuisPlancher

    def __post_init__(self) -> None:
        if self.lx_m <= 0 or self.ly_m <= 0:
            raise ValueError("Les dimensions doivent être positives.")
        if self.lx_m > self.ly_m:
            self.lx_m, self.ly_m = self.ly_m, self.lx_m

    @property
    def alpha(self) -> float:
        """Rapport de portées lx / ly."""
        return self.lx_m / self.ly_m

    # ------------------------------------------------------------------
    # Dalle pleine
    # ------------------------------------------------------------------
    @property
    def epaisseur_min_dp(self) -> float:
        """Épaisseur minimale d'une dalle pleine, en centimètres."""
        if self.appuis_plancher == AppuisPlancher.Simple:
            h_m = self.lx_m / 20
        elif self.appuis_plancher == AppuisPlancher.Continu:
            h_m = self.lx_m / (30 if self.alpha < 0.4 else 40)
        else:
            raise ValueError("Type d'appui non pris en charge")
        return h_m * M_TO_CM

    def predim_dalle_pleine(self) -> float:
        """Épaisseur d'une dalle pleine arrondie au multiple de 5 cm."""
        e = math.ceil(self.epaisseur_min_dp / 5) * 5
        return max(10, e)

    # ------------------------------------------------------------------
    # Corps creux
    # ------------------------------------------------------------------
    @property
    def epaisseur_min_cc(self) -> float:
        """Épaisseur minimale d'un plancher à corps creux, en centimètres."""
        return (self.lx_m / 22.5) * M_TO_CM

    @property
    def depasse_max_cc(self) -> bool:
        """True si l'épaisseur minimale requise dépasse le catalogue (30 cm)."""
        return self.epaisseur_min_cc > max(CORPS_CREUX)

    def predim_corps_creux(self) -> int:
        """Épaisseur normalisée de corps creux retenue, en centimètres.

        Si la portée exige une épaisseur supérieure au catalogue, on renvoie
        l'épaisseur maximale (30 cm) ; l'avertissement est signalé par
        ``depasse_max_cc``.
        """
        ep_min = self.epaisseur_min_cc
        for e in sorted(CORPS_CREUX):
            if e >= ep_min:
                return e
        return max(CORPS_CREUX)

    @staticmethod
    def format_corps_creux(ep: int) -> str:
        """Désignation (ex. ``16+4``) associée à une épaisseur de corps creux."""
        return CORPS_CREUX.get(ep, f"{ep}")

    # ------------------------------------------------------------------
    # Comportement structurel
    # ------------------------------------------------------------------
    def comportement_dp(self) -> str:
        if self.alpha < 0.4:
            return "Poutre-dalle"
        if self.alpha <= 1.0:
            return "Dalle sur 4 appuis"
        return "1 sens"

    @staticmethod
    def comportement_cc() -> str:
        return "1 sens"
