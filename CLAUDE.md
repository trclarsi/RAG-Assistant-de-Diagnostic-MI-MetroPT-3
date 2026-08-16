# CLAUDE.md — Règles standard pour projets RAG

Ce fichier définit les règles que Claude Code doit respecter dans tout projet RAG basé sur ce template. Il est générique : dupliquer/adapter le contenu spécifique projet (sources, schéma de graphe, critères de succès métier) dans un fichier séparé (ex: `docs/project-brief.md`) plutôt que de le mélanger ici.

## Structure du projet

```
src/rag_app/
  ingestion/     # chargement + parsing des documents (PDF, CSV, HTML, ...)
  retrieval/     # vector store, graph store, query routing
  generation/    # prompts, appels LLM, assemblage de la réponse
  evaluation/    # RAGAS, jeux de test, scripts d'évaluation
  app/           # interface (Streamlit/API)
  config.py      # config centralisée via pydantic-settings
tests/
  unit/          # tests rapides, sans dépendance réseau/DB
  integration/   # tests contre Postgres/Neo4j réels (via docker compose)
data/
  raw/           # documents sources bruts — jamais modifiés en place
  processed/     # sorties de pipeline (chunks, embeddings intermédiaires)
  vector_store/  # index locaux (FAISS) si utilisé
```

## Environnement & dépendances

- Gestionnaire de paquets : `uv`. Ne jamais utiliser `pip install` directement dans l'environnement du projet — passer par `uv add <package>` pour que `pyproject.toml` et le lockfile restent la source de vérité.
- Ne jamais committer `.env`. Toute nouvelle variable d'environnement doit être ajoutée à `.env.example` avec une valeur factice.
- Les services (Postgres/pgvector, Neo4j) tournent via `docker compose up -d`. Ne pas supposer une instance installée globalement sur la machine.
- `make setup` doit rester la commande unique pour initialiser l'environnement de zéro. Si tu ajoutes une étape d'installation manuelle, l'intégrer dans `Makefile`, pas dans une note à part.

## Secrets et données sensibles

- Aucune clé API, mot de passe, ou identifiant réel en dur dans le code, les notebooks, ou les messages de commit.
- Avant tout `git add`, vérifier qu'aucun fichier sous `data/raw/` contenant des données propriétaires/sensibles n'est inclus si le dépôt est public.
- Ne jamais logger le contenu complet d'un prompt contenant des données utilisateur sensibles en clair en production — logger un identifiant ou un hash.

## Pipeline RAG — règles de conception

- **Anti-hallucination par défaut** : toute réponse générée doit citer la ou les sources (document + section/chunk) ayant permis la réponse. Si le contexte récupéré ne permet pas de répondre, le système doit le dire explicitement plutôt que d'inventer.
- **Chunking** : ne jamais chunker un document sans stratégie explicite justifiée (taille, overlap, découpage document-aware). Documenter le choix dans le docstring de la fonction d'ingestion concernée.
- **Traçabilité** : chaque chunk indexé doit conserver ses métadonnées de provenance (fichier source, page/section, date d'ingestion). Ne jamais indexer un chunk "nu" sans métadonnées.
- **Séparation retrieval / generation** : le code de récupération de contexte ne doit jamais appeler le LLM de génération, et inversement. Ça garde le pipeline testable étape par étape.
- **Config centralisée** : tout paramètre ajustable (top_k, chunk_size, modèle, seuils) passe par `config.py` / variables d'environnement — jamais en dur dans le code métier.

## Tests et évaluation

- Toute nouvelle fonction d'ingestion, de retrieval ou de génération a un test unitaire correspondant dans `tests/unit/`. Les tests unitaires ne doivent pas appeler de vraie API LLM ni de vraie base — mocker.
- Les tests d'intégration (`tests/integration/`) peuvent appeler les services Docker locaux mais jamais d'API LLM payante en CI sans garde explicite (marquer avec un skip par défaut si pas de clé API).
- Toute modification du pipeline de retrieval ou de génération doit être validée par une exécution de l'évaluation (`make eval`, RAGAS ou équivalent) avant d'être considérée terminée — ne pas se fier uniquement à "ça compile".
- Ne pas présenter une métrique d'évaluation comme robuste si le jeu de test est trop petit pour être statistiquement significatif — le dire explicitement.

## Style de code

- Python typé (type hints partout dans `src/`), vérifié par `mypy` (`make lint`).
- Formatage/lint via `ruff` (`make format`, `make lint`) — pas de config de style concurrente (black, flake8, isort séparés).
- Pas de notebook Jupyter dans `src/` : les notebooks sont pour l'exploration (`notebooks/`), le code de production vit dans `src/rag_app/`. Si une expérimentation en notebook devient utile durablement, la porter en module testé.
- Docstrings sur les fonctions publiques de `ingestion/`, `retrieval/`, `generation/` — expliquer le rôle dans le pipeline, pas relire le code.

## Git & commits

- Un commit = un changement logique cohérent (ingestion, retrieval, eval, etc. séparés si possible).
- Ne jamais forcer un push, amender un commit déjà partagé, ou utiliser `--no-verify` sans demande explicite de l'utilisateur.

## Flux de travail Git (branche + PR)

- Aucun changement ne se fait directement sur `main`. Créer une branche dédiée (`feat/...`, `fix/...`, `chore/...`) pour tout travail, même petit.
- Ouvrir une Pull Request vers `main` une fois le travail prêt. Le merge n'a lieu qu'après que la CI (lint, mypy, tests) est passée au vert.
- Les commandes lourdes en dépendances (`uv sync`, `docker compose up`, exécution de tests avec dépendances installées) doivent être lancées depuis un terminal WSL natif par l'utilisateur, pas via un accès réseau `\\wsl.localhost\...` — cet accès croisé Windows→WSL est nettement plus lent (copie fichier par fichier au lieu de hardlink) et peut bloquer une installation pendant de longues minutes.

## Workflow d'autorisation avec Claude

- **Avant toute modification de fichier** (création, édition, suppression), Claude doit d'abord expliquer : quel fichier, quelle modification exacte, pourquoi, et quelle(s) technologie(s)/dépendance(s), fonctionnalités sont concernées — puis attendre l'autorisation explicite de l'utilisateur avant d'agir. Aucune modification silencieuse ou groupée sans validation préalable, même pour des changements jugés mineurs ou évidents.
- Claude ne doit jamais se présenter ou s'attribuer comme auteur/éditeur du code dans les commits : pas de mention "Co-Authored-By: Claude" ni de signature équivalente identifiant Claude comme auteur des changements dans les messages de commit.
- Cette règle s'applique à toute action modifiant l'état du dépôt (fichiers, config, commits) — pas seulement au code applicatif.

## Ce que Claude ne doit jamais faire seul

- Supprimer ou écraser des données sous `data/raw/`.
- Changer le schéma du graphe de connaissances ou la stratégie de chunking en place sans le signaler explicitement (impact sur tout l'index existant — nécessite souvent une ré-ingestion complète).
- Désactiver un garde-fou anti-hallucination (ex: retirer l'obligation de citation) pour "faire passer" une démo, sans le signaler comme compromis temporaire.
- Committer `.env`, des clés API, ou des exports de base contenant des données réelles sensibles.
- Modifier un fichier sans avoir d'abord expliqué la modification et obtenu l'autorisation explicite de l'utilisateur (voir section "Workflow d'autorisation avec Claude").
- S'attribuer comme auteur/éditeur du code dans un commit.
