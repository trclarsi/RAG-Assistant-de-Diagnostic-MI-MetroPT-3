# Note de Cadrage — Assistant de Diagnostic Hybride Vector + Graph RAG pour la Maintenance Industrielle (MetroPT-3)

**Auteur :** Clarsi Trésor Iloki
**Statut :** Projet portfolio — validation des compétences RAG (livre *RAG with Python Cookbook*)
**Domaine :** Maintenance prédictive ferroviaire — Unité de Production d'Air (APU), Métro de Porto
**Date :** Août 2026

---

## 1. Contexte

Dans l'industrie (manufacturing, énergie, transport), la documentation technique nécessaire au diagnostic et à la résolution de pannes est structurellement fragmentée : manuels constructeurs, fiches AMDEC/FMECA internes, rapports d'incidents historiques — autant de sources hétérogènes, rarement centralisées, et pratiquement jamais interrogeables de façon unifiée. Ce constat est documenté dans la littérature PHM (Prognostics and Health Management) : le temps de diagnostic (composante du MTTR) est fortement pénalisé par la dispersion de la connaissance technique, plus que par un manque de données capteurs.

Ce projet s'inscrit dans la continuité directe de mon expérience professionnelle : PFE chez VINCI Énergies/OMEXOM (plateforme EDM avec pipeline RAG en production), stage SONASID (AMDEC sur Shearline 500), et mon axe de recherche doctoral (RUL/PHM, PIML, fusion multi-capteurs).

### Pourquoi le domaine ferroviaire (APU du Métro de Porto) plutôt qu'un autre

Plusieurs domaines ont été évalués (éolien, industrie manufacturière générique) avant de retenir celui-ci, pour une raison méthodologique précise : c'est le seul corpus identifié qui offre **simultanément** un signal capteur réel, un historique de pannes réelles horodatées, ET les dates d'intervention de maintenance associées — le tout pour **le même appareil, le même opérateur**. Cette cohérence bout-en-bout (signal → panne → action) était une contrainte explicite du projet, pour éviter de bâtir un RAG sur des données incohérentes ou de prétendre avoir un historique de résolution qui n'existe pas.

## 2. Problématique

> **Comment transformer une dérive de capteurs observée sur une unité critique (compresseur d'air) en diagnostic causal exploitable — cause probable et action recommandée — en s'appuyant automatiquement sur la littérature technique documentée et sur l'historique réel de pannes de l'appareil, plutôt que sur la mémoire individuelle d'un technicien ?**

Sous-problèmes techniques associés :
- Hétérogénéité des sources (manuel technique généraliste en texte libre vs. relations structurées cause→effet→action)
- Absence de comptes-rendus d'intervention narratifs complets dans la plupart des corpus publics — nécessité de s'appuyer sur ce qui existe réellement (rapports de panne horodatés + dates de maintenance) sans fabriquer de contenu
- Besoin de traçabilité : toute réponse générée doit être vérifiable (source citée, chemin de raisonnement explicite)
- Risque d'hallucination inacceptable dans un contexte où une mauvaise recommandation a un coût sécurité/financier réel (l'APU est un composant sans redondance : sa panne immobilise le train)

## 3. Objectifs

### Objectif général
Concevoir et implémenter un assistant de diagnostic combinant recherche vectorielle et graphe de connaissances (Vector + Graph RAG hybride), capable de relier une observation capteur réelle à un diagnostic causal documenté et une action recommandée, avec citation systématique des sources.

### Objectifs spécifiques
1. Ingérer et structurer un corpus multi-format (manuel technique en texte libre, papier scientifique, séries temporelles capteurs, rapports de panne)
2. Construire un graphe de connaissances (composant → mode de défaillance → cause → action) à partir de la littérature technique et de la logique AMDEC/FMECA documentée
3. Combiner recherche sémantique (contexte riche, nuances) et traversée de graphe (raisonnement structuré fiable) pour répondre à des requêtes de diagnostic
4. Évaluer quantitativement la pertinence des réponses sur la base des pannes réelles documentées du dataset (vérité terrain)

## 4. Solution proposée

### 4.1 Vue d'ensemble de l'architecture

```
Question utilisateur en langage naturel
        │
        ▼
[Query Router] ── décompose et route la requête (ch. 7.4, 7.8)
        │
        ├──────────────────────────┐
        ▼                          ▼
[Recherche vectorielle]     [Traversée du graphe]
  Documents non structurés    Relations structurées
  (Atlas Copco Manual,          (Composant → Mode de
   papier scientifique           défaillance → Cause →
   MetroPT — texte libre)        Action recommandée)
  → pgvector / FAISS             → Neo4j (ch. 9.1-9.3)
        │                          │
        └────────────┬─────────────┘
                      ▼
        [Fusion des contextes récupérés]
                      │
                      ▼
        [Génération de la réponse + citations]
                      │
                      ▼
        Réponse sourcée : diagnostic probable +
        action recommandée + passage source cité
                      │
                      ▼
        [Évaluation] ── confrontation aux rapports
                         de panne réels du dataset
```

### 4.2 Correspondance avec le livre (chapitres mobilisés)

| Chapitre | Application au projet |
|---|---|
| Ch. 3 — Loading Data | Chargement du manuel PDF (3.2), du papier scientifique (3.2), des données tabulaires capteurs/rapports de panne (3.3) |
| Ch. 4 — Data Preparation | Métadonnées composant/type de panne (4.1), normalisation du vocabulaire technique (4.2), chunking document-aware (4.6) |
| Ch. 5 — Embeddings | Choix du modèle d'embedding (5.4) |
| Ch. 6 — Vector DB | PostgreSQL + pgvector ou FAISS (6.2-6.4) |
| Ch. 7 — Retrieval | Filtrage par métadonnées (7.1), query routing (7.4), décomposition de requêtes complexes (7.8) |
| Ch. 9 — Graph RAG | Construction du graphe de connaissances (9.1-9.2), requêtes Cypher (9.3), recherche sémantique sur le graphe — jonction Vector/Graph (9.4) |
| Ch. 10 — Évaluation | Context precision@k (10.4), faithfulness LLM-as-judge (10.5), validation contre les pannes réelles documentées |
| Ch. 11 — RAG Web Apps | Interface Streamlit de démonstration (11.1-11.2) |

## 5. Sources de données par couche

### Couche 0 — Connaissances générales (fonctionnement systèmes pneumatiques/air comprimé)

| Source | Contenu | Accès |
|---|---|---|
| **Atlas Copco Compressed Air Manual (9ᵉ édition)** | Référence du secteur : physique de la compression, composants, maintenance, dépannage | Gratuit, officiel — `atlascopco.com/content/dam/atlas-copco/compressor-technique/compressor-technique-service/documents/Compressed-Air-Manual-9th-edition.pdf` |
| **Papier scientifique MetroPT-3** (Veloso et al., 2022, *Scientific Data*, Nature) | Architecture de l'APU, description de chaque capteur, contexte opérationnel ferroviaire | Accès libre — `nature.com/articles/s41597-022-01877-3` (miroir PMC : `ncbi.nlm.nih.gov/pmc/articles/PMC9747912`) |

**Rôle :** vocabulaire technique de base, architecture générale du système, structure type d'un manuel de maintenance.

### Couche 1 — Sous-système (compresseur / unité de production d'air, diagnostics)

| Source | Contenu | Accès |
|---|---|---|
| **Atlas Copco Compressed Air Manual** (sections "Problem Solving" et "Maintenance") | Diagnostics de pannes courantes : fuites d'air, fuites d'huile, surchauffe | Même document que Couche 0 |
| **Papier MetroPT-3 — section FMEA/FMECA** | Confirme explicitement que le choix des capteurs a été basé sur une AMDEC/FMECA réalisée par les équipes de maintenance du Métro de Porto — connaissance procédurale "cause → capteur associé" | Même papier Nature |
| **A Benchmark Dataset for Predictive Maintenance** (Veloso et al., arXiv) | Méthodologie d'évaluation, types de panne détaillés, schéma explicite des fuites | Accès libre — `arxiv.org/pdf/2207.05466` |

**Rôle :** fournir la connaissance procédurale et diagnostique nécessaire pour interpréter les observations capteurs et construire le graphe de connaissances.

### Couche 2 — Données opérationnelles et pannes réelles (même appareil : APU du Métro de Porto)

| Source | Contenu | Accès |
|---|---|---|
| **MetroPT-3 Dataset** (UCI Machine Learning Repository) | Séries temporelles réelles à 1 Hz : 8 capteurs analogiques (pression, température huile, courant moteur, débit) + 8 signaux digitaux, février–août 2020 | Gratuit — `archive.ics.uci.edu/dataset/791/metropt+3+dataset` |
| **Table des rapports de panne** (incluse dans le dataset/papier) | Dates de début/fin de chaque panne réelle, sévérité, **date de l'intervention de maintenance associée** | Incluse dans le papier Nature + page UCI |
| **Miroir Kaggle** | Même données, format prêt à l'emploi pour prototypage rapide | `kaggle.com/datasets/pattinson9999/uci-metropt-3-dataset` |

**Détail des pannes réelles documentées (extrait vérifié) :**

| # | Début | Fin | Type | Sévérité | Action de maintenance |
|---|---|---|---|---|---|
| 1 | 18/04/2020 | 18/04/2020 | Fuite d'air | Stress élevé | — |
| 2 | 29/05/2020 | 30/05/2020 | Fuite d'air | Stress élevé | Maintenance le 30/04 à 12h00 |
| 3 | 05/06/2020 | 07/06/2020 | Fuite d'air | Stress élevé | Maintenance le 08/06 à 16h00 |
| 4 | 15/07/2020 | 15/07/2020 | Fuite d'air | Stress élevé | Maintenance le 16/07 à 00h00 |

*Note : une version ultérieure du dataset (MetroPT2, 2022) documente également une panne de type "Oil Leak", permettant d'enrichir la diversité des modes de défaillance si besoin.*

## 6. Pourquoi cette architecture Vector + Graph plutôt qu'un RAG classique

| | Vector RAG seul | Graph RAG seul | **Hybride (retenu)** |
|---|---|---|---|
| Force | Bon pour retrouver un passage pertinent dans un texte long | Bon pour le raisonnement structuré multi-sauts | Combine recherche floue en langage naturel **et** raisonnement structuré fiable |
| Faiblesse | Ne "raisonne" pas — similarité sémantique uniquement | Rigide si la question ne correspond à aucune relation prédéfinie | — |

C'est une architecture rarement démontrée dans les portfolios juniors, ce qui en fait un projet différenciant tout en restant ancré sur un vrai problème documenté.

## 7. Enjeux

### 7.1 Enjeux techniques
- **Fiabilité / anti-hallucination** : un diagnostic erroné sur un composant critique sans redondance a un impact opérationnel réel (immobilisation du train) — nécessite citation obligatoire et évaluation faithfulness systématique
- **Construction du graphe de connaissances** : extraire des relations structurées fiables à partir de texte non structuré (manuel, papier scientifique) sans introduire d'erreurs d'interprétation
- **Cohérence des données** : garantir que toutes les couches (connaissance générale, procédurale, opérationnelle) restent traçables au même système physique

### 7.2 Enjeux métier / organisationnels
- Réduction du temps de diagnostic (MTTR) pour un composant critique et non redondant
- Démonstration d'un raisonnement de type expert (signal → cause probable → action) sans dépendre d'un historique d'intervention narratif qui n'existe pas publiquement

### 7.3 Enjeux pour le portfolio
- Architecture Vector + Graph RAG : différenciante et rarement démontrée par des candidats juniors
- Ancrage sur un vrai problème documenté et vérifiable (papier scientifique publié, dataset académique reconnu)
- Cohérent avec mon axe de recherche doctoral (PHM/RUL) et mon expérience professionnelle (AMDEC SONASID) — bon point de continuité narrative pour LinkedIn/entretiens

## 8. Livrables attendus

1. Code source documenté (GitHub, README avec diagramme d'architecture hybride Vector+Graph)
2. Graphe de connaissances Neo4j (composant → mode de défaillance → cause → action), construit à partir des sources Couche 0/1
3. Rapport d'évaluation quantitatif (RAGAS : faithfulness, context precision) confronté aux pannes réelles du dataset
4. Démonstration vidéo courte pour LinkedIn (requête → diagnostic sourcé, validé sur un cas de panne réel du dataset)
5. Article technique (Dev.to, republication Medium) détaillant l'architecture hybride et les choix méthodologiques

## 9. Critères de succès

| Critère | Cible |
|---|---|
| Faithfulness (RAGAS) | > 0.85 |
| Context precision@k | > 0.75 |
| Citation systématique des sources | 100% des réponses |
| Validation sur cas réel | Le système retrouve le bon mode de défaillance documenté pour au moins 3 des 4 pannes réelles du dataset, à partir du seul signal capteur |
| Gestion des cas hors-périmètre | Refus explicite si l'information n'est pas dans le corpus (pas d'hallucination) |

## 10. Risques et limites

- **Corpus de pannes limité en volume** (4 événements documentés dans MetroPT-3) : suffisant pour une démonstration et une validation qualitative, mais pas pour une évaluation statistique robuste — à documenter explicitement comme limite, sans présenter de métrique non vérifiable
- **Absence de comptes-rendus d'intervention narratifs complets** : le dataset fournit panne horodatée + date de maintenance, mais pas le détail texte libre de l'intervention technique (pièce remplacée, geste précis) — le système comble ce vide par le raisonnement documenté (Couche 1), pas par une donnée fabriquée
- **Construction du graphe** : la qualité du graphe de connaissances dépend de la justesse de l'extraction des relations depuis les manuels — nécessite une validation manuelle des relations extraites avant mise en production du graphe

## 11. Prochaines étapes

1. Télécharger et inspecter les fichiers MetroPT-3 (UCI) : structure exacte des séries temporelles et de la table de pannes
2. Récupérer les PDF Couche 0/1 (Atlas Copco Manual, papier Nature MetroPT-3, papier arXiv complémentaire)
3. Démarrer le pipeline d'ingestion (ch. 3) : PDF texte pour Couches 0/1, tabulaire/CSV pour Couche 2
4. Construire manuellement puis semi-automatiquement le graphe de connaissances (composant → mode de défaillance → cause → action) à partir de la logique FMEA documentée
5. Implémenter le pipeline Vector RAG (ch. 4-5-6) et Graph RAG (ch. 9) séparément, puis la fusion (ch. 9.4)
6. Développer le query router (ch. 7.4)
7. Évaluer sur les 4 cas de panne réels documentés
8. Développer l'interface Streamlit de démonstration (ch. 11)
9. Documenter et publier (GitHub, Dev.to, LinkedIn)
