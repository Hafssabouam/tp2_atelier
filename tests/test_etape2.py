"""Étape 2 : les exceptions du projet."""
import pytest

from exceptions import AtelierError, FichierInvalide, ReleveInvalide


def test_hierarchie():
    assert issubclass(AtelierError, Exception)
    assert issubclass(FichierInvalide, AtelierError)
    assert issubclass(ReleveInvalide, AtelierError)


def test_attributs():
    err = ReleveInvalide("valeur manquante", 9, "temperature")
    assert (err.message, err.ligne, err.champ) == ("valeur manquante", 9, "temperature")


def test_message_lisible():
    assert str(ReleveInvalide("valeur manquante", 9, "temperature")) == \
        "ligne 9, champ 'temperature' : valeur manquante"


def test_attrapee_par_la_classe_mere():
    with pytest.raises(AtelierError):
        raise ReleveInvalide("x", 2, "machine")


def test_pas_confondue_avec_value_error():
    assert not issubclass(ReleveInvalide, ValueError)
