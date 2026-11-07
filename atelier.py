"""Supervision d'un atelier : référentiel des machines, relevés capteurs, alertes et rapport."""
import csv
import json
import math
import re
from datetime import datetime
from pathlib import Path

from exceptions import FichierInvalide, ReleveInvalide

COLONNES = ("machine", "horodatage", "temperature", "vibration")

# Un relevé valide est un tuple : (machine, horodatage, temperature, vibration)
Releve = tuple[str, datetime, float, float]


# --- Étape 1 : le référentiel des machines (JSON, dictionnaires, ensembles) --------------------
def charger_machines(chemin: Path) -> dict[str, dict]:
    """Lit machines.json et renvoie un dictionnaire {identifiant: fiche de la machine}.

    Lève FichierInvalide si un identifiant apparaît deux fois.
    """
    with open(chemin, encoding="utf-8") as fichier:
        fiches = json.load(fichier)

    machines = {}
    for fiche in fiches:
        identifiant = fiche["id"]
        if identifiant in machines:
            raise FichierInvalide(f"identifiant en double : {identifiant}")
        machines[identifiant] = fiche
    return machines 

    
    



def ateliers(machines: dict[str, dict]) -> set[str]:
    """L'ensemble des ateliers où se trouvent les machines."""
    return {fiche["atelier"] for fiche in machines.values()}


# --- Étape 3 : valider une ligne (exceptions, tuples) -------------------------------------------
def lire_nombre(texte: str, champ: str, numero: int) -> float:
    """Convertit "52,3" en 52.3 ; lève ReleveInvalide si la valeur est vide ou non numérique."""
    texte = texte.strip()

    if not texte :
        raise ReleveInvalide("valeur manquante", numero, champ)
    
    texte = texte.replace(",",".")

    try:
        nomber = float(texte)
    except ValueError:
        raise ReleveInvalide(
            f"valeur non numérique : {texte!r}", numero, champ
        ) from None
    if not math.isfinite(nomber):
        raise ReleveInvalide(
            f"valeur non finie : {texte!r}", numero, champ
        )
    return nomber 







def parser_releve(brut: dict[str, str], numero: int, machines: dict[str, dict]) -> Releve:
    """Transforme une ligne brute du CSV (dictionnaire de textes) en relevé typé.

    Lève ReleveInvalide (avec le numéro de ligne et le champ fautif) au premier problème.
    """
    machine = brut["machine"].strip().upper()
    if machine not in machines :
        raise ReleveInvalide(
        f"machine inconnue : {machine!r}",
        numero,
        "machine"
    )
    
    horod= brut["horodatage"].strip()
    try:
        horodatage = datetime.fromisoformat(horod)
    except ValueError: 
        raise ReleveInvalide(
            f"horodatage invalide : {horod!r}",
            numero,
            "horodatage"
        ) from None
    temperature = lire_nombre(brut["temperature"], "temperature", numero)
    vibration = lire_nombre(brut["vibration"], "vibration", numero)
    if vibration < 0:
        raise ReleveInvalide(
            f"vibration négative : {vibration}",
            numero,
            "vibration"
        )

    return (machine, horodatage, temperature, vibration)


# --- Étape 4 : lire le fichier (CSV, générateur, collecte des erreurs) ---------------------------
def lignes_csv(chemin: Path):
    """Générateur : produit (numero, ligne_brute) pour chaque ligne de données du CSV.

    Le numéro est celui de la ligne dans le fichier (l'en-tête est la ligne 1).
    Lève FichierInvalide si une colonne attendue manque.
    """
    with open(chemin, "r", encoding="utf-8-sig", newline="") as fichier:
            lecteur = csv.DictReader(fichier, delimiter=";")

            manquantes = [
               colonne for colonne in COLONNES
               if colonne not in lecteur.fieldnames
            ]

            if manquantes:
                raise FichierInvalide(
                f"colonnes manquantes : {', '.join(manquantes)}"
             )

            for numero, brut in enumerate(lecteur, start=2):
                yield numero, brut


def lire_releves(chemin: Path, machines: dict[str, dict]) -> tuple[list[Releve], list[ReleveInvalide]]:
    """Lit tout le fichier et renvoie (releves_valides, erreurs) sans s'arrêter sur une ligne invalide."""
    releves = []
    erreurs = []

    for numero, brut in lignes_csv(chemin):
        try:
            releve = parser_releve(brut, numero, machines)
            releves.append(releve)

        except ReleveInvalide as err:
            erreurs.append(err)

    return releves, erreurs


def ecrire_rejets(erreurs: list[ReleveInvalide], chemin: Path) -> None:
    """Écrit les lignes rejetées dans un CSV ligne;champ;message, lisible par Excel."""
    with open(chemin, "w", encoding="utf-8-sig", newline="") as fichier:
        writer = csv.writer(fichier, delimiter=";")

        writer.writerow(["ligne", "champ", "message"])

        for err in erreurs:
            writer.writerow([err.ligne, err.champ, err.message])


# --- Étape 5 : analyser (dictionnaires, compréhensions) ------------------------------------------
def par_machine(releves: list[Releve]) -> dict[str, list[Releve]]:
    """Regroupe les relevés par machine : {machine: [relevés dans l'ordre du fichier]}."""
    groupes = {}

    for releve in releves:
        machine = releve[0]
        groupes.setdefault(machine, []).append(releve)

    return groupes


def moyennes(releves: list[Releve]) -> dict[str, tuple[float, float]]:
    """{machine: (température moyenne arrondie à 0,1 ; vibration moyenne arrondie à 0,01)}."""
    return {
        machine: (
            round(sum(r[2] for r in liste) / len(liste), 1),
            round(sum(r[3] for r in liste) / len(liste), 2)
        )
        for machine, liste in par_machine(releves).items()
    }


def alertes(releves: list[Releve], machines: dict[str, dict]) -> list[tuple[str, datetime, str]]:
    """Liste des dépassements de seuil (machine, horodatage, motif), triée par horodatage puis machine."""
    alertes_temp = [
        (r[0], r[1], f"température {r[2]} > {machines[r[0]]['temp_max']}")
        for r in releves
        if r[2] > machines[r[0]]["temp_max"]
    ]

    alertes_vib = [
        (r[0], r[1], f"vibration {r[3]} > {machines[r[0]]['vib_max']}")
        for r in releves
        if r[3] > machines[r[0]]["vib_max"]
    ]

    resultat = alertes_temp + alertes_vib
    resultat.sort(key=lambda a: (a[1], a[0]))

    return resultat




def machines_silencieuses(releves: list[Releve], machines: dict[str, dict]) -> set[str]:
    """Les machines du référentiel qui n'ont envoyé aucun relevé valide (capteur en panne ?)."""
    return set(machines) - {r[0] for r in releves}


# --- Étape 6 : trier ---------------------------------------------------------------------------
def classement(releves: list[Releve], machines: dict[str, dict]) -> list[tuple[str, int]]:
    """[(machine, nombre d'alertes)] pour TOUTES les machines, la plus alertée d'abord, puis par identifiant."""
    compteurs  = {m: 0 for m in machines}
    for machine, h, motif in alertes(releves, machines):
        compteurs[machine] += 1
    return sorted(compteurs.items(), key=lambda x: (-x[1], x[0]))


def top_vibrations(releves: list[Releve], n: int = 3) -> list[Releve]:
    """Les n relevés de plus forte vibration, du plus fort au plus faible."""
    return sorted(releves, key=lambda r: r[3], reverse=True)[:n]


# --- Étape 7 : le rapport JSON ------------------------------------------------------------------
def construire_rapport(releves: list[Releve], erreurs: list[ReleveInvalide], machines: dict[str, dict]) -> dict:
    """Le rapport sous forme d'un dictionnaire prêt pour json.dump (pas de datetime, pas d'ensemble)."""
    resultat_moyennes = {}
    for machine, valeurs in moyennes(releves).items():
        temperature, vibration = valeurs

        resultat_moyennes[machine] = {
            "temperature": temperature,
            "vibration": vibration
        }
        resultat_alertes = []

    for machine, heure, motif in alertes(releves, machines):
        resultat_alertes.append({
            "machine": machine,
            "heure": heure.strftime("%H:%M"),
            "motif": motif
        })
    classement_machines = [
        machine
        for machine, nombre in classement(releves, machines)
        if nombre > 0
    ]
    silencieuses = sorted(
        machines_silencieuses(releves, machines)
    )
    rapport = {
    "releves_valides": len(releves),
    "lignes_rejetees": len(erreurs),
    "moyennes": resultat_moyennes,
    "alertes": resultat_alertes,
    "classement": classement_machines,
    "machines_silencieuses": silencieuses
    }
    return rapport

def ecrire_rapport(rapport: dict, chemin: Path) -> None:
    """Écrit le rapport en JSON indenté, accents conservés."""
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(
            rapport,
            fichier,
            ensure_ascii=False,
            indent=2
        )


# --- Étape 8 (à la maison) : le journal des événements (expressions régulières) ------------------
MOTIF_EVENEMENT = re.compile( 
    r"(?P<date>\d{4}-\d{2}-\d{2}) "
    r"(?P<heure>\d{2}:\d{2}:\d{2}) "
    r"\[(?P<machine>M-\d{2})\] "
    r"(?P<type>[A-Z]+) "
    r"code=(?P<code>[A-Z]\d{2})"
    r"(?: duree=(?P<duree>\d+))?")   # étape 8


def lire_evenements(chemin: Path):
    """Générateur : un dictionnaire par ligne valide du journal, les lignes mal formées sont sautées.

    Clés : machine, type, code, heure, duree (entier en minutes, ou None si absente).
    """
    with open(chemin, encoding="utf-8") as fichier:
        for ligne in fichier:
            match = MOTIF_EVENEMENT.fullmatch(ligne.strip())

            if match is None:
                continue

            donnees = match.groupdict()

            yield {
                "machine": donnees["machine"],
                "type": donnees["type"],
                "code": donnees["code"],
                "heure": donnees["heure"],
                "duree": int(donnees["duree"]) if donnees["duree"] is not None else None
            }


def temps_arret(evenements) -> dict[str, int]:
    """Durée totale des ARRET par machine, en minutes."""
    resultat = {}
    for evenement in evenements:
        if evenement["type"]=="ARRET"and evenement["duree"] is not None:
            machine = evenement["machine"]
            resultat[machine] = resultat.get(machine, 0) + evenement["duree"]
    return resultat
