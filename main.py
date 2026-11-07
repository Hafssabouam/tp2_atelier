"""Programme principal : lit les relevés du jour, écrit les rejets et le rapport, affiche un résumé."""
from pathlib import Path

from atelier import (charger_machines, construire_rapport, ecrire_rapport, ecrire_rejets, lire_releves, lire_evenements, temps_arret)
from exceptions import AtelierError
ICI = Path(__file__).parent
DONNEES = ICI / "donnees"
SORTIES = ICI / "sorties"


def main() -> int:
    """Renvoie 0 si tout s'est bien passé, 1 si un fichier est inutilisable."""
    try:
        machines = charger_machines(DONNEES / "machines.json")
        releves, erreurs = lire_releves(
            DONNEES / "releves.csv", machines
        )

    except (AtelierError, FileNotFoundError) as err:
        print(f"Erreur : {err}")
        return 1

    SORTIES.mkdir(exist_ok=True)

    ecrire_rejets(erreurs, SORTIES / "rejets.csv")

    rapport = construire_rapport(releves, erreurs, machines)
    
    evenements = list(lire_evenements(DONNEES / "evenements.log"))
    rapport["temps_arret"] = temps_arret(evenements)
    ecrire_rapport(rapport, SORTIES / "rapport.json")
    

    print(f"{len(releves)} relevés valides, {len(erreurs)} lignes rejetées")

    print(
        f"{len(rapport['alertes'])} alertes ; "
        f"machines à surveiller : {', '.join(rapport['classement'])}"
    )

    print(
        f"Sans relevé : "
        f"{', '.join(rapport['machines_silencieuses'])}"
    )

    print("Fichiers écrits dans sorties/ : rejets.csv, rapport.json")

    return 0



if __name__ == "__main__":
    raise SystemExit(main())
