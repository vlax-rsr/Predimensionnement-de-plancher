"""Point d'entrée de l'application graphique."""

import sys

from ..logging_setup import setup_logging
from .main_window import MainWindow, application


def main() -> int:
    """Lance l'application et renvoie le code de sortie."""
    setup_logging()
    app = application()
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
