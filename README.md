# Template — Environnement de dev standard pour projets RAG

Squelette réutilisable pour démarrer un projet RAG (vector, graph, ou hybride).

## Démarrage rapide

```bash
cp .env.example .env        # puis remplir les clés/API
make setup                  # crée le venv (uv) et installe les deps
make up                      # lance Postgres/pgvector (et Neo4j si décommenté)
make run                     # lance l'app Streamlit de démo
```

## Commandes utiles

| Commande | Rôle |
|---|---|
| `make lint` | ruff + mypy |
| `make format` | formatage auto |
| `make test` | tests unitaires (rapides, sans DB/API) |
| `make test-cov` | tests + couverture |
| `make eval` | évaluation RAG (RAGAS) |
| `make down` | arrête les services Docker |
| `make clean` | nettoie les caches |

## Structure

Voir [CLAUDE.md](./CLAUDE.md) pour la structure détaillée et les règles de développement du projet.

## Adapter ce template à un projet spécifique

1. Renommer `rag_app` en `src/<nom_du_projet>/` si besoin (mettre à jour `pyproject.toml`).
2. Ajouter un `docs/project-brief.md` avec le contexte métier/sources/critères de succès propres au projet — ne pas alourdir `CLAUDE.md` avec ça.
3. Décommenter le service `neo4j` dans `docker-compose.yml` si l'architecture inclut un Graph RAG.
4. Choisir le backend vector store réel (`pgvector`, `faiss`, `chroma`) dans `.env` / `config.py`.
