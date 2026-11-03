"""Étape 3 : valider une ligne de relevé."""
from datetime import datetime

import pytest

from atelier import lire_nombre, parser_releve
from exceptions import ReleveInvalide


def brut(machine="M-01", horodatage="2026-10-12 08:00", temperature="52,3", vibration="2,1"):
    return {"machine": machine, "horodatage": horodatage, "temperature": temperature, "vibration": vibration}


def test_lire_nombre():
    assert lire_nombre("52,3", "temperature", 2) == 52.3
    assert lire_nombre(" 4.5 ", "vibration", 2) == 4.5


@pytest.mark.parametrize("texte, morceau", [("", "valeur manquante"), ("  ", "valeur manquante"),
                                            ("abc", "non numérique : 'abc'"), ("nan", "non finie")])
def test_lire_nombre_invalide(texte, morceau):
    with pytest.raises(ReleveInvalide, match=morceau) as info:
        lire_nombre(texte, "temperature", 7)
    assert (info.value.ligne, info.value.champ) == (7, "temperature")


def test_releve_valide(machines):
    assert parser_releve(brut(), 2, machines) == ("M-01", datetime(2026, 10, 12, 8, 0), 52.3, 2.1)


def test_identifiant_nettoye(machines):
    assert parser_releve(brut(machine=" m-01 "), 2, machines)[0] == "M-01"


@pytest.mark.parametrize("champs, champ_fautif", [
    ({"machine": "M-07"}, "machine"),
    ({"horodatage": "2026-10-12 25:00"}, "horodatage"),
    ({"horodatage": "12/10/2026"}, "horodatage"),
    ({"temperature": ""}, "temperature"),
    ({"vibration": "abc"}, "vibration"),
    ({"vibration": "-0,4"}, "vibration"),
])
def test_champ_fautif(machines, champs, champ_fautif):
    with pytest.raises(ReleveInvalide) as info:
        parser_releve(brut(**champs), 5, machines)
    assert info.value.champ == champ_fautif
    assert info.value.ligne == 5


def test_message_machine_inconnue(machines):
    with pytest.raises(ReleveInvalide, match="machine inconnue : 'M-07'"):
        parser_releve(brut(machine="M-07"), 5, machines)
