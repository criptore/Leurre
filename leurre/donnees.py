"""Chargement et validation du jeu de cas."""

import json
from pathlib import Path

from . import DECISIONS, FAMILLES

CHEMIN_PAR_DEFAUT = Path(__file__).resolve().parent.parent / "data" / "cases.jsonl"
CHAMPS = ("id", "famille", "texte", "contexte", "decision", "explication")


def charger_cas(chemin=CHEMIN_PAR_DEFAUT):
    """Lit un fichier JSONL de cas et lève ValueError au premier cas invalide."""
    cas, vus = [], set()
    with open(chemin, encoding="utf-8") as f:
        for no, ligne in enumerate(f, 1):
            if not ligne.strip():
                continue
            try:
                c = json.loads(ligne)
            except json.JSONDecodeError as e:
                raise ValueError(f"{chemin}:{no} : JSON invalide ({e})") from e
            for champ in CHAMPS:
                if not isinstance(c.get(champ), str) or not c[champ].strip():
                    raise ValueError(f"{chemin}:{no} : champ « {champ} » manquant ou vide")
            if c["famille"] not in FAMILLES:
                raise ValueError(f"{chemin}:{no} : famille inconnue « {c['famille']} »")
            if c["decision"] not in DECISIONS:
                raise ValueError(f"{chemin}:{no} : décision inconnue « {c['decision']} »")
            if c["id"] in vus:
                raise ValueError(f"{chemin}:{no} : identifiant en double « {c['id']} »")
            vus.add(c["id"])
            cas.append(c)
    return cas
