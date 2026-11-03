"""Étape 1 : charger le référentiel JSON des machines."""
import json

import pytest

from atelier import ateliers, charger_machines
from exceptions import FichierInvalide


def test_cles_identifiants(machines):
    assert list(machines) == ["M-01", "M-02", "M-03", "M-04", "M-05"]


def test_fiche_complete(machines):
    assert machines["M-03"] == {"id": "M-03", "nom": "Presse hydraulique", "atelier": "Emboutissage",
                                "temp_max": 65, "vib_max": 6.0}


def test_accents_conserves(machines):
    assert machines["M-04"]["atelier"] == "Utilités"


def test_ateliers(machines):
    assert ateliers(machines) == {"Usinage", "Emboutissage", "Utilités", "Assemblage"}


def test_identifiant_en_double(tmp_path):
    chemin = tmp_path / "machines.json"
    fiche = {"id": "M-01", "nom": "Tour", "atelier": "Usinage", "temp_max": 70, "vib_max": 4.5}
    chemin.write_text(json.dumps([fiche, fiche]), encoding="utf-8")
    with pytest.raises(FichierInvalide, match="M-01"):
        charger_machines(chemin)


def test_fichier_absent(tmp_path):
    with pytest.raises(FileNotFoundError):
        charger_machines(tmp_path / "absent.json")
