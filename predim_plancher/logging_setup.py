"""Configuration du journal (logging) de l'application.

Le journal est écrit dans un fichier texte (rotation et archivage) et répliqué
sur la console. Le dossier de journaux (« logs/ » par défaut) est ignoré par
git : les journaux ne sont jamais poussés sur GitHub.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Nom du logger applicatif (unique dans toute l'application).
APP_LOGGER_NAME = "predim"

# Répertoire des journaux, relatif au dossier de lancement.
LOG_DIR_NAME = "logs"

# Fichier journal : rotation au-delà de 1 Mo, 3 archives conservées.
LOG_FILE_NAME = "predim.log"
MAX_BYTES = 1_000_000
BACKUP_COUNT = 3

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(module)s | %(message)s"
_LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"


def _log_directory() -> Path:
    """Dossier des journaux.

    Priorité : variable ``PREDIM_LOG_DIR`` > exécutable gelé (à côté du
    ``.exe``) > dossier courant.
    """
    env = os.environ.get("PREDIM_LOG_DIR")
    if env:
        return Path(env)
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / LOG_DIR_NAME
    return Path.cwd() / LOG_DIR_NAME


def get_logger() -> logging.Logger:
    """Renvoie le logger de l'application (avant ou après configuration)."""
    return logging.getLogger(APP_LOGGER_NAME)


def setup_logging() -> logging.Logger:
    """Configure le logger applicatif : fichier rotatif + console.

    Niveau *DEBUG* dans le fichier, *INFO* sur la console. Appel idempotent :
    une seconde exécution ne duplique pas les handlers.
    """
    logger = get_logger()
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATEFMT)

    # Console uniquement si un flux est disponible (indisponible en .exe fenêtré).
    if sys.stderr is not None:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        logger.addHandler(console)

    try:
        dossier = _log_directory()
        dossier.mkdir(parents=True, exist_ok=True)
        fichier = RotatingFileHandler(
            dossier / LOG_FILE_NAME,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )
        fichier.setLevel(logging.DEBUG)
        fichier.setFormatter(formatter)
        logger.addHandler(fichier)
    except OSError:
        logger.warning(
            "Impossible de créer le dossier de journaux %r",
            str(_log_directory()),
            exc_info=True,
        )

    logger.info(
        "Journalisation initialisée (fichier : %s)",
        str(_log_directory() / LOG_FILE_NAME),
    )
    return logger