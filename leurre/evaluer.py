"""Fait passer un modèle sur les cas et enregistre ses résultats.

Exemples :
    python -m leurre.evaluer --modele toujours-ignorer
    python -m leurre.evaluer --modele llama3.2 --base-url http://localhost:11434/v1
"""

import argparse
import json
import re
import sys
from pathlib import Path

from .donnees import CHEMIN_PAR_DEFAUT, charger_cas
from .modeles import construire
from .notation import calculer_metriques, extraire_decision
from .tableau import rendre_tableau


def evaluer(cas, repondre, journal=None):
    lignes = []
    for i, c in enumerate(cas, 1):
        brut = repondre(c)
        lignes.append({
            "id": c["id"],
            "famille": c["famille"],
            "attendu": c["decision"],
            "obtenu": extraire_decision(brut),
            "reponse_brute": brut,
        })
        if journal:
            print(f"[{i}/{len(cas)}] {c['id']} : {lignes[-1]['obtenu']} (attendu {c['decision']})", file=journal)
    return lignes


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--modele", required=True, help="nom du modèle, ou toujours-agir / toujours-ignorer / toujours-verifier")
    p.add_argument("--base-url", default="http://localhost:11434/v1", help="API compatible OpenAI (défaut : Ollama local). Clé éventuelle dans LEURRE_API_KEY.")
    p.add_argument("--cas", default=CHEMIN_PAR_DEFAUT, help="fichier JSONL de cas")
    p.add_argument("--sortie", default="resultats", help="dossier des résultats")
    a = p.parse_args(argv)

    cas = charger_cas(a.cas)
    lignes = evaluer(cas, construire(a.modele, a.base_url), journal=sys.stderr)
    resultat = {"modele": a.modele, "metriques": calculer_metriques(lignes), "lignes": lignes}

    dossier = Path(a.sortie)
    dossier.mkdir(parents=True, exist_ok=True)
    fichier = dossier / (re.sub(r"[^\w.-]+", "_", a.modele) + ".json")
    fichier.write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding="utf-8")
    print(rendre_tableau([resultat]))
    print(f"\nRésultats enregistrés dans {fichier}", file=sys.stderr)


if __name__ == "__main__":
    main()
