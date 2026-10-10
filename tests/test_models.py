"""Tests du modèle : Plancher et ses règles de prédimensionnement."""

import pytest

from predim_plancher.core import AppuisPlancher, Plancher


def test_portees_reordonnees():
    p = Plancher("P1", lx_m=6.0, ly_m=4.0, appuis_plancher=AppuisPlancher.Continu)
    assert p.lx_m == 4.0
    assert p.ly_m == 6.0


def test_dimensions_positives_obligatoires():
    with pytest.raises(ValueError):
        Plancher("P1", lx_m=0.0, ly_m=4.0, appuis_plancher=AppuisPlancher.Continu)


def test_alpha():
    p = Plancher("P1", lx_m=2.0, ly_m=6.0, appuis_plancher=AppuisPlancher.Continu)
    assert p.alpha == pytest.approx(2.0 / 6.0)


@pytest.mark.parametrize(
    "lx, ly, appuis, attendu",
    [
        (4.0, 4.5, AppuisPlancher.Continu, 10.0),
        (2.0, 6.0, AppuisPlancher.Continu, 10.0),  # alpha < 0.4 -> lx/30
        (4.0, 4.5, AppuisPlancher.Simple, 20.0),   # lx/20
    ],
)
def test_predim_dalle_pleine(lx, ly, appuis, attendu):
    p = Plancher("P1", lx_m=lx, ly_m=ly, appuis_plancher=appuis)
    assert p.predim_dalle_pleine() == attendu


@pytest.mark.parametrize(
    "lx, ep_attendu, format_attendu",
    [
        (4.0, 20, "16+4"),
        (3.0, 16, "12+4"),
        (5.0, 25, "20+5"),
    ],
)
def test_predim_corps_creux(lx, ep_attendu, format_attendu):
    p = Plancher("P1", lx_m=lx, ly_m=lx + 0.5,
                 appuis_plancher=AppuisPlancher.Continu)
    ep = p.predim_corps_creux()
    assert ep == ep_attendu
    assert p.format_corps_creux(ep) == format_attendu


def test_corps_creux_depasse_maximum():
    p = Plancher("P1", lx_m=7.0, ly_m=8.0, appuis_plancher=AppuisPlancher.Continu)
    assert p.depasse_max_cc is True
    assert p.predim_corps_creux() == 30  # épaisseur max du catalogue


def test_corps_creux_sous_maximum():
    p = Plancher("P1", lx_m=6.0, ly_m=6.5, appuis_plancher=AppuisPlancher.Continu)
    assert p.depasse_max_cc is False
    assert p.predim_corps_creux() == 30  # épaisseur normalisée atteinte sans dépassement


def test_comportement_dp():
    poutre = Plancher("P1", lx_m=1.0, ly_m=3.0, appuis_plancher=AppuisPlancher.Continu)
    assert poutre.comportement_dp() == "Poutre-dalle"
