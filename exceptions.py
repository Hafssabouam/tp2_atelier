"""Les erreurs métier de l'application de supervision."""


class AtelierError(Exception):
    """Classe mère de toutes les erreurs de l'application."""


class FichierInvalide(AtelierError):
    """Le fichier entier est inutilisable (colonnes manquantes, identifiants en double...)."""


class ReleveInvalide(AtelierError):
    """Une ligne de relevé est invalide ; on garde le numéro de ligne et le champ fautif."""

    def __init__(self, message: str, ligne: int, champ: str):
        raise NotImplementedError("à compléter")
