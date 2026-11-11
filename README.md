# Leurre

Banc d'essai qui mesure si un LLM sait repérer les **faux signaux** dans l'actualité financière et les réseaux sociaux : ironie, homonymes, comptes piratés, vieilles news repostées, pumps organisés.

Les benchmarks de finance mesurent surtout le sentiment (positif ou négatif). Leurre mesure autre chose : face à un message, le modèle doit décider s'il faut **agir**, **ignorer** ou **vérifier**.

> État : v0. 36 cas inventés, pas encore de jeu de test caché. Les chiffres ne valent que comme démonstration du protocole.

## Les cas

`data/cases.jsonl`, un cas par ligne :

| Champ | Rôle |
| --- | --- |
| `id` | identifiant unique |
| `famille` | `vraie_news`, `ironie`, `homonyme`, `compte_pirate`, `vieille_news` ou `pump` |
| `texte` | le message vu par le modèle |
| `contexte` | source, date, liste de suivi : vu par le modèle aussi |
| `decision` | la bonne réponse : `agir`, `ignorer` ou `verifier` |
| `explication` | pourquoi (jamais montrée au modèle) |

Tous les cas sont inventés et les sociétés sont fictives, pour éviter les questions de droits sur des posts réels et pour que les modèles ne puissent pas réciter une actualité apprise. Seuls les cas d'homonymie citent de vrais noms (Apple, Amazon, Doge...), dans leur sens non financier.

La famille `vraie_news` sert de témoin : un modèle qui ignore tout par prudence doit y perdre des points.

## Utilisation

Python 3.9+, aucune dépendance.

Noter un modèle servi par une API compatible OpenAI (Ollama par défaut) :

```bash
python -m leurre.evaluer --modele llama3.2
```

Autre serveur ou API distante (clé lue dans `LEURRE_API_KEY`) :

```bash
python -m leurre.evaluer --modele mon-modele --base-url https://exemple.com/v1
```

Comparer plusieurs modèles :

```bash
python -m leurre.tableau resultats/*.json
```

Lancer les tests :

```bash
python -m unittest
```

## Métriques

- **Exactitude** : part de bonnes décisions.
- **Équilibrée** : moyenne des rappels sur les trois décisions. C'est le classement de référence, car 72 % des cas attendent `ignorer`.
- **Pièges mordus** : part des cas où il ne fallait pas agir et où le modèle a répondu `agir`. C'est l'erreur qui coûte de l'argent.
- **Invalides** : réponses dont on ne peut pas tirer une décision unique (comptées fausses).
- Puis l'exactitude par famille, pour voir où chaque modèle se fait avoir.

Références triviales (`--modele toujours-agir`, etc.), à battre par tout modèle sérieux :

| Modèle | Exactitude | Équilibrée | Pièges mordus | Invalides | vraie_news | ironie | homonyme | compte_pirate | vieille_news | pump |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| toujours-agir | 14 % | 33 % | 100 % | 0 % | 83 % | 0 % | 0 % | 0 % | 0 % | 0 % |
| toujours-ignorer | 72 % | 33 % | 0 % | 0 % | 0 % | 100 % | 100 % | 50 % | 83 % | 100 % |
| toujours-verifier | 14 % | 33 % | 0 % | 0 % | 17 % | 0 % | 0 % | 50 % | 17 % | 0 % |

## Suite prévue

- Intégrer les cas pièges de Sentinel et monter à environ 200 cas, avec plus de cas `agir` et `verifier`.
- Séparer un jeu de développement public et un jeu de test jamais vu, protocole figé (méthode Krinos-Bench).
- Faire relire les étiquettes par une deuxième personne et mesurer l'accord.
- Passer plusieurs modèles locaux et publier le tableau.
- Recherche bibliographique pour vérifier que l'angle « résistance aux pièges » est bien peu couvert.
