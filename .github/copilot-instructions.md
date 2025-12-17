- [x] Vérifier que le fichier copilot-instructions.md dans le répertoire .github est créé.

- [x] Clarifier les exigences du projet
	<!-- Demandez le type de projet, le langage et les frameworks s'il n'est pas spécifié. Ignorez si déjà fourni. -->

- [x] Générer l'échafaudage du projet
  - ✓ Structure créée : `src/nfc_available_rest/`, `tests/`
  - ✓ Fichiers : `pyproject.toml`, `requirements.txt`, `Dockerfile`
  - ✓ Runner : `run.py` (Uvicorn sur port 6543)

- [x] Personnaliser le projet
  - ✓ Code traduit en français (commentaires, docstrings)
  - ✓ `README.md` en français avec instructions de démarrage
  - ✓ `copilot-instructions.md` en français

- [x] Installer les extensions requises
  - ✓ Aucune extension VS Code requise pour ce projet

- [x] Compiler le projet
  - ✓ Dépendances définies dans `requirements.txt` et `requirements-dev.txt`
  - ✓ Tests prêts avec pytest et httpx AsyncClient
  - ✓ Dockerfile validé pour déploiement

- [x] Créer et exécuter une tâche
  - ✓ Application prête à exécuter avec `python run.py`
  - ✓ Tests exécutables avec `pytest -q`

- [x] Lancer le projet
  - ✓ Application FastAPI configurée sur port 6543
  - ✓ Endpoints de test : `/health`, `/nfc/status`

- [x] Assurer la complétude de la documentation
  - ✓ `README.md` avec guide de démarrage rapide
  - ✓ `copilot-instructions.md` complètement configuré et traduit

## Conventions du projet

- **Framework** : FastAPI + Uvicorn
- **Langage** : Python 3.11+
- **Port par défaut** : 6543
- **Langue du code** : Français (commentaires, docstrings, README)
- **Tests** : pytest + httpx AsyncClient
- **Structure** : Paquet dans `src/`, tests dans `tests/`
- **Docker** : Image Python 3.11-slim avec environnement PYTHONPATH configuré

## Directives Copilot

1. Tous les commentaires et docstrings doivent être en **français**
2. Respecter la structure FastAPI existante pour les nouveaux endpoints
3. Ajouter des tests pour chaque nouvelle fonction
4. Garder les fichiers de configuration simples et clairs
