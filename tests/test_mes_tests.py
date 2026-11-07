from pathlib import Path
from atelier import lire_evenements, temps_arret


def test_temps_arret():
    evenements = list(
        lire_evenements(Path("donnees/evenements.log"))
    )

    resultat = temps_arret(evenements)

    assert resultat == {
        "M-03": 20,
        "M-02": 25,
        "M-01": 40
    }