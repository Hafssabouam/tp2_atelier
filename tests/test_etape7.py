"""Étape 7 : le rapport JSON et le programme principal."""
import json

import main
from atelier import construire_rapport, ecrire_rapport, lire_releves


def test_construire_rapport(donnees, machines):
    releves, erreurs = lire_releves(donnees / "releves.csv", machines)
    rapport = construire_rapport(releves, erreurs, machines)
    assert rapport["releves_valides"] == 14
    assert rapport["lignes_rejetees"] == 5
    assert rapport["moyennes"]["M-03"] == {"temperature": 49.6, "vibration": 5.57}
    assert rapport["alertes"][0] == {"machine": "M-02", "heure": "09:00", "motif": "température 77.4 > 75"}
    assert rapport["classement"] == ["M-01", "M-02", "M-04", "M-03"]
    assert rapport["machines_silencieuses"] == ["M-05"]


def test_rapport_serialisable(donnees, machines):
    releves, erreurs = lire_releves(donnees / "releves.csv", machines)
    json.dumps(construire_rapport(releves, erreurs, machines))   # ni datetime ni set à l'intérieur


def test_ecrire_rapport(tmp_path):
    chemin = tmp_path / "rapport.json"
    ecrire_rapport({"atelier": "Utilités"}, chemin)
    texte = chemin.read_text(encoding="utf-8")
    assert "Utilités" in texte                      # ensure_ascii=False
    assert json.loads(texte) == {"atelier": "Utilités"}


def test_main(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(main, "SORTIES", tmp_path / "sorties")
    assert main.main() == 0
    sortie = capsys.readouterr().out
    assert "14 relevés valides, 5 lignes rejetées" in sortie
    assert "Sans relevé : M-05" in sortie
    assert json.loads((tmp_path / "sorties" / "rapport.json").read_text(encoding="utf-8"))["releves_valides"] == 14
    assert (tmp_path / "sorties" / "rejets.csv").exists()


def test_main_fichier_absent(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(main, "DONNEES", tmp_path)
    assert main.main() == 1
    assert capsys.readouterr().out.startswith("Erreur : ")
