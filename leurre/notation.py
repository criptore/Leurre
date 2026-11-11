"""Lecture des réponses des modèles et calcul des métriques."""

import json
import re
import unicodedata

from . import DECISIONS, FAMILLES

INVALIDE = "invalide"


def _normaliser(texte):
    sans_accents = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in sans_accents if not unicodedata.combining(c)).lower()


def extraire_decision(reponse):
    """Tire la décision d'une réponse brute. Renvoie « invalide » si elle est ambiguë.

    On lit d'abord un objet JSON {"decision": ...} ; à défaut, on accepte le
    texte libre seulement s'il ne mentionne qu'une seule des trois décisions.
    """
    for bloc in re.findall(r"\{.*?\}", reponse, flags=re.DOTALL):
        try:
            objet = json.loads(bloc)
        except json.JSONDecodeError:
            continue
        valeur = objet.get("decision", objet.get("décision"))
        if isinstance(valeur, str) and _normaliser(valeur).strip() in DECISIONS:
            return _normaliser(valeur).strip()
    trouvees = {d for d in DECISIONS if re.search(rf"\b{d}\b", _normaliser(reponse))}
    return trouvees.pop() if len(trouvees) == 1 else INVALIDE


def calculer_metriques(lignes):
    """Métriques à partir de lignes {famille, attendu, obtenu}.

    - exactitude : part de bonnes décisions ;
    - exactitude_equilibree : moyenne des rappels par décision attendue, pour
      qu'un modèle qui répond toujours « ignorer » ne soit pas flatté ;
    - taux_piege_mordu : part des cas où il ne fallait pas agir et où le
      modèle a répondu « agir » (l'erreur qui coûte de l'argent) ;
    - taux_invalide : part de réponses illisibles.
    """
    def part(sous_ensemble, test):
        return sum(1 for l in sous_ensemble if test(l)) / len(sous_ensemble) if sous_ensemble else None

    juste = lambda l: l["obtenu"] == l["attendu"]
    rappels = [
        part([l for l in lignes if l["attendu"] == d], juste) for d in DECISIONS
    ]
    rappels = [r for r in rappels if r is not None]
    pieges = [l for l in lignes if l["attendu"] != "agir"]
    par_famille = {}
    for famille in FAMILLES:
        sous = [l for l in lignes if l["famille"] == famille]
        if sous:
            par_famille[famille] = {"n": len(sous), "exactitude": part(sous, juste)}
    return {
        "n": len(lignes),
        "exactitude": part(lignes, juste),
        "exactitude_equilibree": sum(rappels) / len(rappels) if rappels else None,
        "taux_piege_mordu": part(pieges, lambda l: l["obtenu"] == "agir"),
        "taux_invalide": part(lignes, lambda l: l["obtenu"] == INVALIDE),
        "par_famille": par_famille,
    }
