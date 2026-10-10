"""Point d'entrée racine.

Permet de lancer l'application sans installation :

    python main.py
"""

import sys

from predim_plancher.gui.app import main

if __name__ == "__main__":
    sys.exit(main())
