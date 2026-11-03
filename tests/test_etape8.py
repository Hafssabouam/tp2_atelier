"""Étape 8 (à la maison) : le journal des événements avec les expressions régulières."""
import inspect

from atelier import lire_evenements, temps_arret


def test_generateur():
    assert inspect.isgeneratorfunction(lire_evenements)


def test_lignes_valides(donnees):
    evenements = list(lire_evenements(donnees / "evenements.log"))
    assert len(evenements) == 8                  # la coupure réseau et [M-1] sont sautées


def test_groupes_nommes(donnees):
    premier, second = list(lire_evenements(donnees / "evenements.log"))[:2]
    assert premier == {"machine": "M-01", "type": "DEMARRAGE", "code": "D00", "heure": "07:58:10", "duree": None}
    assert second == {"machine": "M-03", "type": "ARRET", "code": "E42", "heure": "08:15:02", "duree": 12}


def test_temps_arret(donnees):
    assert temps_arret(lire_evenements(donnees / "evenements.log")) == {"M-03": 20, "M-02": 25, "M-01": 40}
