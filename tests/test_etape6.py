"""Étape 6 : trier."""
from datetime import datetime

from atelier import classement, top_vibrations


def test_classement(releves, machines):
    assert classement(releves, machines) == [("M-01", 3), ("M-02", 2), ("M-04", 2), ("M-03", 1), ("M-05", 0)]


def test_egalite_departagee_par_identifiant(releves, machines):
    noms = [m for m, _ in classement(releves, machines)]
    assert noms.index("M-02") < noms.index("M-04")


def test_top_vibrations(releves):
    assert [(r[0], r[3]) for r in top_vibrations(releves)] == [("M-03", 6.8), ("M-03", 5.9), ("M-01", 5.3)]


def test_top_n(releves):
    assert len(top_vibrations(releves, n=5)) == 5
    assert top_vibrations([], n=3) == []


def test_ordre_original_conserve(releves):
    avant = list(releves)
    top_vibrations(releves)
    assert releves == avant
    assert releves[0] == ("M-01", datetime(2026, 10, 12, 8, 0), 52.3, 2.1)
