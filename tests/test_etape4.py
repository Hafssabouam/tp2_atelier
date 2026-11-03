"""Étape 4 : lire le fichier CSV, collecter les erreurs, écrire les rejets."""
import inspect

import pytest

from atelier import ecrire_rejets, lignes_csv, lire_releves
from exceptions import FichierInvalide, ReleveInvalide


def test_lignes_csv_est_un_generateur(donnees):
    assert inspect.isgeneratorfunction(lignes_csv)
    numero, brut = next(lignes_csv(donnees / "releves.csv"))
    assert numero == 2
    assert brut["machine"] == "M-01"          # pas de "﻿machine" : le BOM est retiré


def test_nombre_de_lignes(donnees):
    assert sum(1 for _ in lignes_csv(donnees / "releves.csv")) == 19


def test_colonne_manquante(tmp_path):
    chemin = tmp_path / "releves.csv"
    chemin.write_text("machine;horodatage;temperature\nM-01;2026-10-12 08:00;52,3\n", encoding="utf-8")
    with pytest.raises(FichierInvalide, match="vibration"):
        list(lignes_csv(chemin))


def test_lire_releves(donnees, machines):
    releves, erreurs = lire_releves(donnees / "releves.csv", machines)
    assert len(releves) == 14
    assert [e.ligne for e in erreurs] == [9, 10, 13, 16, 20]
    assert all(isinstance(e, ReleveInvalide) for e in erreurs)


def test_ecrire_rejets(tmp_path):
    chemin = tmp_path / "rejets.csv"
    ecrire_rejets([ReleveInvalide("valeur manquante", 9, "temperature"),
                   ReleveInvalide("machine inconnue : 'M-07'", 10, "machine")], chemin)
    assert chemin.read_text(encoding="utf-8-sig").splitlines() == [
        "ligne;champ;message",
        "9;temperature;valeur manquante",
        "10;machine;machine inconnue : 'M-07'",
    ]


def test_rejets_lisibles_par_excel(tmp_path):
    chemin = tmp_path / "rejets.csv"
    ecrire_rejets([], chemin)
    assert chemin.read_bytes().startswith(b"\xef\xbb\xbf")   # BOM : Excel reconnaît l'UTF-8
