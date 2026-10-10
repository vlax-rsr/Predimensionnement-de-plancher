"""Énumérations métier du prédimensionnement des planchers."""

from enum import Enum


class TypePlancher(Enum):
    """Types de planchers supportés."""

    DP = "Dalle pleine"
    CC = "Plancher à corps creux"


class AppuisPlancher(Enum):
    """Conditions d'appuis du plancher."""

    Simple = "Simple"
    Continu = "Continue"
