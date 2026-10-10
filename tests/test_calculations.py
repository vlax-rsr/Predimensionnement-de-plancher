"""Tests des calculs de prédimensionnement."""

from predim_plancher.core import AppuisPlancher, predim_compare, predim_plancher


def test_predim_plancher_succes():
    ligne = predim_plancher(4.0, 4.5, AppuisPlancher.Continu, nom="P1")
    assert ligne["nom"] == "P1"
    assert ligne["lx"] == 4.0
    assert ligne["ly"] == 4.5
    assert ligne["dp_statut"] == "Succès"
    assert ligne["cc_statut"] == "Succès"
    assert ligne["dp_ep"] == 10.0
    assert ligne["cc_ep"] == 20
    assert ligne["cc_format"] == "16+4"


def test_predim_plancher_epaisseur_max_cc_avertie():
    ligne = predim_plancher(7.0, 8.0, AppuisPlancher.Continu)
    assert ligne["cc_statut"] == "Succès"
    assert ligne["cc_ep"] == 30  # épaisseur max du catalogue
    assert ligne["cc_max_depasse"] is True
    assert ligne["cc_min_cm"] > 30
    assert ligne["dp_statut"] == "Succès"


def test_predim_plancher_cc_normal():
    ligne = predim_plancher(4.0, 4.5, AppuisPlancher.Continu)
    assert ligne["cc_max_depasse"] is False


def test_predim_compare_liste():
    resultats = predim_compare(
        [(4.0, 4.5), (3.0, 4.0)], AppuisPlancher.Continu
    )
    assert len(resultats) == 2
    assert [r["nom"] for r in resultats] == ["P1", "P2"]
