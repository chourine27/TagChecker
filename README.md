# TagChecker_Rest

Projet FastAPI minimal pour une API REST de vérification de tags.

## Table des matières

1. [Démarrage rapide](#démarrage-rapide-linux--zsh)
2. [Versioning API](#versioning-api)
3. [Structure du projet](#structure-du-projet)
4. [Authentification](#authentification)
   - [Configuration de la clé secrète JWT](#configuration-de-la-clé-secrète-jwt)
   - [Obtenir un token d'API](#obtenir-un-token-dapi)
   - [Utiliser le token](#utiliser-le-token-pour-accéder-aux-endpoints-protégés)
5. [Débogage VS Code](#débogage-vs-code)
6. [Logs](#logs)
7. [Base de données](#base-de-données)
8. [Gestion des tags](#gestion-des-tags)
   - [Vérification d'un tag](#vérification-dun-tag)
   - [Ajout d'un tag](#ajout-dun-tag)
9. [Référence rapide de l'API](#référence-rapide-de-lapi)
10. [Prochaines étapes](#prochaines-étapes)

## Démarrage rapide (Linux / zsh)

Créez un environnement virtuel et installez les dépendances de développement :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Exécutez l'application localement :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# Initialiser la base de données (première utilisation)
python init_db.py

# Lancer l'application
python run.py
```

Exécutez les tests :

```bash
pytest -q
```

### Tests spécifiques

Pour exécuter uniquement les tests d'authentification :

```bash
pytest -q tests/test_auth.py
```

Construisez l'image Docker :

```bash
docker build -t tagchecker-rest .
```

Exécutez le conteneur Docker :

```bash
docker run -p 6543:6543 tagchecker-rest
```

## Versioning API

L'API est structurée avec un système de versioning. Pour l'instant, seule la version `v1` est disponible.

Tous les endpoints sont préfixés par `/v1` :

- `GET /v1/health` - Vérification de l'état de l'API (public)
- `GET /v1/log` - Enregistrement de logs (public)
- `POST /v1/login` - Authentification et obtention du token JWT (public)
- `GET /v1/check_tag` - Vérification d'un tag (protégé par JWT)
- `POST /v1/tag` - Ajout d'un nouveau tag dans la base de données (protégé par JWT)

## Structure du projet

- `src/tagChecker_rest` - paquet d'application
- `run.py` - lanceur de développement (exécute uvicorn)
- `tests` - tests pytest
- `Dockerfile` - construction de l'image conteneur

## Authentification

Le projet utilise l'authentification JWT (JSON Web Token) pour sécuriser les endpoints de l'API.

### Configuration de la clé secrète JWT

La clé secrète JWT est définie dans `src/tagChecker_rest/auth.py` :

- **SECRET_KEY** : `"votre-clé-secrète-à-changer-en-prod"` (ligne 12)
- **ALGORITHM** : `HS256`
- **EXPIRATION** : 30 minutes par défaut

**Important** : Changez la clé secrète en production ! Utilisez une clé aléatoire sécurisée :

```bash
# Générer une clé secrète sécurisée
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Pour utiliser une variable d'environnement (recommandé en production) :

```bash
export JWT_SECRET_KEY="votre-clé-secrète-générée"
```

Et modifiez `auth.py` pour lire la variable d'environnement :

```python
import os
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "votre-clé-secrète-à-changer-en-prod")
```

### Obtenir un token d'API

Endpoint : `POST /v1/login`

Utilisateurs de test (déclarés dans `src/tagChecker_rest/auth.py`) :

- `Matthieu` / `MdP`
- `Karine` / `MdP`

**Exemple de requête** :

```bash
curl -X POST http://localhost:6543/v1/login -H "Content-Type: application/json" \
	-d '{"username":"Matthieu","password":"MdP"}'
```

**Réponse** :

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Utiliser le token pour accéder aux endpoints protégés

Incluez le token dans l'en-tête `Authorization` avec le préfixe `Bearer` :

```bash
# Stocker le token dans une variable
TOKEN=$(curl -s -X POST http://localhost:6543/v1/login -H "Content-Type: application/json" \
	-d '{"username":"Matthieu","password":"MdP"}' | jq -r '.access_token')

# Utiliser le token pour accéder à un endpoint protégé
curl -X GET "http://localhost:6543/v1/checkTag?tag=4e5656545654" \
	-H "Authorization: Bearer $TOKEN"
```

**Sans token valide** : l'API retourne une erreur 401 avec le message `"Accès refusé"`.

## Débogage VS Code

Un fichier de configuration de débogage est disponible : `.vscode/launch.json`.

 - Configuration **FastAPI Debug** : lance `uvicorn` en mode reload sur le port `6543`.
 - Configuration **Pytest Debug** : lance `pytest` en mode debug.

Lancez-le depuis VS Code (F5) et choisissez la configuration souhaitée.

## Logs

Le projet configure un logging rotatif au démarrage via `src/tagChecker_rest/logging_config.py`.

- Dossier par défaut : `logs/`
- Fichier par défaut : `logs/tagChecker_rest.log`
- Rotation : 5 fichiers de backup, ~5 MB par fichier (configurable dans `logging_config.configure_logging`).

Personnalisation rapide :

```bash
# Changer le dossier de logs
export LOG_DIR=/var/log/tagChecker_rest

# Démarrer l'application
python run.py

# Consulter les logs en temps réel
tail -f logs/tagChecker_rest.log
```

Pour modifier le niveau ou la rotation, éditez `src/tagChecker_rest/logging_config.py` ou fournissez des variables d'environnement avant le démarrage.

## Base de données

Le projet utilise SQLite pour la gestion des tags disponibles.

- Dossier par défaut : `db/`
- Fichier par défaut : `db/tagChecker.db`
- Table principale : `availableTag` (colonne `tag` en clé primaire)

### Initialisation

Initialiser la base de données avant le premier lancement :

```bash
python init_db.py
```

Fonctions disponibles dans `src/tagChecker_rest/database.py` :

- `tag_exists(tag: str) -> bool` : vérifie si un tag existe
- `add_tag(tag: str) -> bool` : ajoute un tag
- `remove_tag(tag: str) -> bool` : supprime un tag
- `list_tags() -> list` : récupère tous les tags

### Exemple d'utilisation de `add_tag` (Python)

Vous pouvez utiliser les fonctions de `database.py` directement depuis un script Python :

```python
from tagChecker_rest import database as db

# Initialiser la base (faites ceci une seule fois)
db.init_db()

tag = "4e5656545654"
success = db.add_tag(tag)
print("Ajout réussi:", success)  # True si ajouté, False si tag déjà présent
print("Existe:", db.tag_exists(tag))

# Tentative d'ajout en doublon
print("Ajout en doublon:", db.add_tag(tag))  # False si doublon (erreur d'intégrité gérée)

# Lister et supprimer
print("Tous les tags:", db.list_tags())
db.remove_tag(tag)
```

Comportement :
- `add_tag` retourne `True` si le tag a été inséré avec succès.
- `add_tag` retourne `False` si le tag existe déjà (gestion d'`sqlite3.IntegrityError`).


Changer le dossier de la base de données :

```bash
export DB_DIR=/var/lib/tagChecker
python init_db.py
python run.py
```

## Gestion des tags

### Vérification d'un tag

Endpoint : `GET /v1/check_tag`

Vérifie qu'un tag est éligible. L'accès est protégé et nécessite un jeton JWT valide.

**Paramètres** :
- `tag` (query string) : Le tag à vérifier

**Exemples** :

Accès sans jeton (réponse attendue : 401) :

```bash
curl -v -X GET "http://localhost:6543/v1/check_tag?tag=4e5656545654"
# -> réponse: HTTP/1.1 401 { "detail": "Not authenticated" }
```

Accès avec jeton valide :

```bash
# Obtenir un token
TOKEN=$(curl -s -X POST http://localhost:6543/v1/login -H "Content-Type: application/json" \
	-d '{"username":"Matthieu","password":"MdP"}' | jq -r '.access_token')

# Appeler check_tag avec le token
curl -X GET "http://localhost:6543/v1/check_tag?tag=4e5656545654" \
	-H "Authorization: Bearer $TOKEN"
# -> réponse: { "result": "OK" }
```

### Ajout d'un tag

Endpoint : `POST /v1/tag`

Ajoute un nouveau tag dans la base de données. L'accès est protégé et nécessite un jeton JWT valide.

**Body JSON** :
```json
{
  "tag": "4e5656545654"
}
```

ou

```json
{
  "Tag": "4e5656545654"
}
```

**Exemple** :

```bash
# Obtenir un token
TOKEN=$(curl -s -X POST http://localhost:6543/v1/login -H "Content-Type: application/json" \
	-d '{"username":"Matthieu","password":"MdP"}' | jq -r '.access_token')

# Ajouter un nouveau tag
curl -X POST http://localhost:6543/v1/tag \
	-H "Authorization: Bearer $TOKEN" \
	-H "Content-Type: application/json" \
	-d '{"tag":"4e5656545654"}'
# -> réponse: { "result": "OK" }
```

**Réponses** :
- `200 OK` : `{ "result": "OK" }` - Tag ajouté avec succès
- `401 Unauthorized` : Token manquant ou invalide
- `500 Internal Server Error` : Erreur lors de l'ajout du tag (ex: tag déjà existant)


## Référence rapide de l'API

### Endpoints publics

| Méthode | Endpoint | Description | Paramètres |
|---------|----------|-------------|------------|
| GET | `/v1/health` | Vérification de l'état de l'API | Aucun |
| GET | `/v1/log` | Enregistrement de logs | `text` (query string) |
| POST | `/v1/login` | Authentification et obtention du token JWT | `username`, `password` (JSON body) |

### Endpoints protégés (JWT requis)

| Méthode | Endpoint | Description | Paramètres |
|---------|----------|-------------|------------|
| GET | `/v1/check_tag` | Vérification d'un tag | `tag` (query string) |
| POST | `/v1/tag` | Ajout d'un nouveau tag | `tag` ou `Tag` (JSON body) |

### Configuration rapide pour développement

```bash
# 1. Installer les dépendances
python3 -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows
pip install -r requirements-dev.txt

# 2. Initialiser la base de données
python init_db.py

# 3. Lancer l'application
python run.py

# 4. Accéder à l'API
# Documentation interactive: http://localhost:6543/docs
# API: http://localhost:6543/v1/
```

### Workflow complet d'authentification

```bash
# 1. Obtenir un token
TOKEN=$(curl -s -X POST http://localhost:6543/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Matthieu","password":"MdP"}' | jq -r '.access_token')

# 2. Utiliser le token
curl -X GET "http://localhost:6543/v1/check_tag?tag=ABC123" \
  -H "Authorization: Bearer $TOKEN"

# 3. Ajouter un tag
curl -X POST http://localhost:6543/v1/tag \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tag":"ABC123"}'
```

## Prochaines étapes

- Implémentez l'intégration réelle du lecteur NFC dans `src/tagChecker_rest/app.py`.
- Configurez CI pour exécuter les tests et construire l'image.
- Remplacez `FAKE_USERS_DB` par une vraie base de données utilisateurs.
- Ajoutez la gestion des variables d'environnement pour `SECRET_KEY`.
