"""Assemble les fichiers de résultats en un tableau comparatif Markdown.

Exemple :
    python -m leurre.tableau resultats/*.json
"""

import argparse
import json

from . import FAMILLES


def _pct(x):
    return "—" if x is None else f"{100 * x:.0f} %"


def rendre_tableau(resultats):
    entetes = ["Modèle", "Exactitude", "Équilibrée", "Pièges mordus", "Invalides", *FAMILLES]
    rangs = [entetes, ["---"] * len(entetes)]
    for r in sorted(resultats, key=lambda r: -(r["metriques"]["exactitude_equilibree"] or 0)):
        m = r["metriques"]
        rangs.append([
            r["modele"],
            _pct(m["exactitude"]),
            _pct(m["exactitude_equilibree"]),
            _pct(m["taux_piege_mordu"]),
            _pct(m["taux_invalide"]),
            *[_pct(m["par_famille"].get(f, {}).get("exactitude")) for f in FAMILLES],
        ])
    return "\n".join("| " + " | ".join(r) + " |" for r in rangs)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("fichiers", nargs="+", help="fichiers JSON produits par leurre.evaluer")
    a = p.parse_args(argv)
    resultats = []
    for chemin in a.fichiers:
        with open(chemin, encoding="utf-8") as f:
            resultats.append(json.load(f))
    print(rendre_tableau(resultats))


if __name__ == "__main__":
    main()
