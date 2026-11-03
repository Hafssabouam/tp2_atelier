"""Objets partagés par les tests : chemins des données fournies et référentiel chargé."""
from pathlib import Path

import pytest

DONNEES = Path(__file__).resolve().parent.parent / "donnees"


@pytest.fixture
def donnees():
    return DONNEES


@pytest.fixture
def machines():
    from atelier import charger_machines
    return charger_machines(DONNEES / "machines.json")


@pytest.fixture
def releves(machines):
    from atelier import lire_releves
    valides, _ = lire_releves(DONNEES / "releves.csv", machines)
    return valides
