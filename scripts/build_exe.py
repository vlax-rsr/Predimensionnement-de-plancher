"""Génère un exécutable Windows autonome de l'application (PyInstaller).

Par défaut : un fichier unique dans ``dist/`` (démarrage plus lent, ~193 Mo à
décompresser). L'option ``--onedir`` produit un dossier (démarrage rapide).

Les fichiers intermédiaires (``build/``, ``*.spec``) sont déposés dans
``build/`` et ne sont jamais versionnés.

Prérequis :
    pip install pyinstaller

Usage (depuis n'importe où) :
    python scripts/build_exe.py            # un seul fichier .exe
    python scripts/build_exe.py --onedir   # dossier (démarrage rapide)
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_NAME = "PredimensionnementPlancher"
ENTRY_POINT = REPO_ROOT / "main.py"
BUILD_DIR = REPO_ROOT / "build"
DIST_DIR = REPO_ROOT / "dist"
ICON_FILE = BUILD_DIR / "app.ico"


def _generate_icon() -> Path | None:
    """Dessine l'icône de l'application dans ``build/app.ico``."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from PySide6.QtGui import QGuiApplication
        from predim_plancher.gui.icons import make_app_pixmap
    except Exception as exc:  # noqa: BLE001 - icône optionnelle
        print(f"  ! Icône indisponible ({exc})")
        return None

    if QGuiApplication.instance() is None:
        QGuiApplication(sys.argv)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    pixmap = make_app_pixmap(256)
    if not pixmap.save(str(ICON_FILE), "ICO"):
        print("  ! Échec de l'écriture de l'icône")
        return None
    print(f"  Icône générée : {ICON_FILE}")
    return ICON_FILE


def main() -> int:
    """Construit l'exécutable et renvoie le code de sortie."""
    parser = argparse.ArgumentParser(description="Construit l'exécutable Windows.")
    parser.add_argument(
        "--onedir", action="store_true",
        help="produire un dossier (démarrage rapide) au lieu d'un fichier unique",
    )
    args = parser.parse_args()

    if shutil.which("pyinstaller") is None:
        try:
            import PyInstaller  # noqa: F401
        except ImportError:
            print("PyInstaller n'est pas installé : « pip install pyinstaller »")
            return 1

    mode = "--onedir" if args.onedir else "--onefile"
    print(f"Construction de « {APP_NAME} » ({mode})…")
    icon = _generate_icon()

    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        mode, "--windowed",
        "--name", APP_NAME,
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        "--specpath", str(BUILD_DIR),
        # Données matplotlib (polices mathtext) sans embarquer tout le paquet.
        "--collect-data", "matplotlib",
    ]
    if icon is not None:
        command += ["--icon", str(icon)]
    command.append(str(ENTRY_POINT))

    result = subprocess.run(command, cwd=REPO_ROOT)
    if result.returncode != 0:
        print("Échec de la construction.")
        return result.returncode

    if args.onedir:
        executable = DIST_DIR / APP_NAME / f"{APP_NAME}.exe"
    else:
        executable = DIST_DIR / f"{APP_NAME}.exe"
    print(f"\nExécutable généré : {executable}")
    print("Les fichiers intermédiaires (build/, *.spec) ne sont pas versionnés.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())