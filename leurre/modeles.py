"""Modèles notables : références triviales et API compatible OpenAI."""

import json
import os
import urllib.request

from . import DECISIONS

CONSIGNE = """Tu es le filtre d'entrée d'un système de trading automatique.
On te donne un message (actualité, post de réseau social...) et son contexte.
Choisis exactement une décision :
- "agir" : l'information est fiable, nouvelle et concerne bien l'actif suivi ; le système peut trader dessus.
- "ignorer" : l'information ne doit pas déclencher de trade.
- "verifier" : l'information pourrait compter mais doit être recoupée avant toute action.
Réponds uniquement par un objet JSON : {"decision": "agir" | "ignorer" | "verifier", "raison": "une phrase"}"""


def formuler(cas):
    return f"Message :\n{cas['texte']}\n\nContexte :\n{cas['contexte']}"


def reference(nom):
    """Référence triviale « toujours-<décision> », utile pour situer les scores."""
    decision = nom.removeprefix("toujours-")
    if decision not in DECISIONS:
        raise ValueError(f"référence inconnue « {nom} » (attendu : toujours-agir, toujours-ignorer, toujours-verifier)")
    return lambda cas: json.dumps({"decision": decision})


def api_openai(modele, base_url, cle=None, delai=120):
    """Client minimal pour /chat/completions (Ollama, llama.cpp, vLLM, OpenAI...)."""
    url = base_url.rstrip("/") + "/chat/completions"
    entetes = {"Content-Type": "application/json"}
    if cle:
        entetes["Authorization"] = f"Bearer {cle}"

    def repondre(cas):
        corps = {
            "model": modele,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": CONSIGNE},
                {"role": "user", "content": formuler(cas)},
            ],
        }
        requete = urllib.request.Request(url, json.dumps(corps).encode(), entetes)
        with urllib.request.urlopen(requete, timeout=delai) as r:
            return json.load(r)["choices"][0]["message"]["content"] or ""

    return repondre


def construire(modele, base_url):
    if modele.startswith("toujours-"):
        return reference(modele)
    return api_openai(modele, base_url, os.environ.get("LEURRE_API_KEY"))
