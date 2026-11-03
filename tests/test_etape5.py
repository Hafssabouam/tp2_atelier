"""Étape 5 : regrouper, calculer des moyennes, détecter les alertes."""
import copy
from datetime import datetime

from atelier import alertes, machines_silencieuses, moyennes, par_machine


def test_par_machine(releves):
    groupes = par_machine(releves)
    assert sorted(groupes) == ["M-01", "M-02", "M-03", "M-04"]
    assert [r[2] for r in groupes["M-01"]] == [52.3, 58.9, 66.2, 71.4, 69.0]


def test_moyennes(releves):
    assert moyennes(releves) == {"M-01": (63.6, 3.86), "M-02": (72.7, 3.73),
                                 "M-03": (49.6, 5.57), "M-04": (83.9, 3.17)}


def test_moyennes_liste_vide():
    assert moyennes([]) == {}


def test_alertes(releves, machines):
    resultat = alertes(releves, machines)
    assert len(resultat) == 8
    assert resultat[0] == ("M-02", datetime(2026, 10, 12, 9, 0), "température 77.4 > 75")
    assert resultat[1] == ("M-03", datetime(2026, 10, 12, 9, 0), "vibration 6.8 > 6.0")


def test_alertes_triees(releves, machines):
    cles = [(h, m) for m, h, _ in alertes(releves, machines)]
    assert cles == sorted(cles)


def test_seuil_strict(machines):
    pile = [("M-01", datetime(2026, 10, 12, 8, 0), 70.0, 4.5)]   # égal au seuil : pas d'alerte
    assert alertes(pile, machines) == []


def test_machines_silencieuses(releves, machines):
    assert machines_silencieuses(releves, machines) == {"M-05"}
    assert machines_silencieuses([], machines) == set(machines)


def test_entrees_non_modifiees(releves, machines):
    avant_r, avant_m = list(releves), copy.deepcopy(machines)
    par_machine(releves), moyennes(releves), alertes(releves, machines), machines_silencieuses(releves, machines)
    assert releves == avant_r and machines == avant_m
