"""Tests de l'analyse de la saisie."""

from predim_plancher.core import parse_dimensions


def test_saisie_valide_virgule():
    dims, erreurs = parse_dimensions("4.0, 4.5\n3.0, 4.0")
    assert erreurs == []
    assert dims == [(4.0, 4.5), (3.0, 4.0)]


def test_separateurs_multiples():
    dims, erreurs = parse_dimensions("3;4\n5.0 3.0")
    assert erreurs == []
    assert dims == [(3.0, 4.0), (5.0, 3.0)]


def test_lignes_vides_ignorees():
    dims, erreurs = parse_dimensions("\n4.0, 4.5\n\n")
    assert erreurs == []
    assert dims == [(4.0, 4.5)]


def test_ligne_invalide():
    dims, erreurs = parse_dimensions("4.0, 4.5, 6.0")
    assert dims == []
    assert len(erreurs) == 1


def test_valeurs_non_positives():
    dims, erreurs = parse_dimensions("-1, 2")
    assert dims == []
    assert len(erreurs) == 1
