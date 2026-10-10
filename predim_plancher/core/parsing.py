"""Analyse de la saisie utilisateur (dimensions)."""


def parse_dimensions(texte: str) -> tuple[list[tuple[float, float]], list[str]]:
    """Convertit un texte multiligne en liste de paires ``(lx, ly)``.

    Une ligne valide contient deux nombres positifs séparés par une virgule,
    un point-virgule ou un espace (point ou virgule décimale acceptés).

    Renvoie ``(dimensions, erreurs)`` où ``erreurs`` décrit les lignes invalides.
    """
    dimensions: list[tuple[float, float]] = []
    erreurs: list[str] = []

    for i, ligne in enumerate(texte.splitlines(), start=1):
        ligne = ligne.strip()
        if not ligne:
            continue
        ligne_norm = ligne.replace(";", ",").replace(" ", ",")
        parts = [p for p in ligne_norm.split(",") if p != ""]
        if len(parts) != 2:
            erreurs.append(
                f"Ligne {i} invalide : « {ligne} » (attendu : lx, ly)"
            )
            continue
        try:
            a = float(parts[0].replace(",", "."))
            b = float(parts[1].replace(",", "."))
        except ValueError:
            erreurs.append(f"Ligne {i} : valeurs non numériques « {ligne} »")
            continue
        if a <= 0 or b <= 0:
            erreurs.append(f"Ligne {i} : dimensions non positives")
            continue
        dimensions.append((a, b))

    return dimensions, erreurs
