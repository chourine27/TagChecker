# nfcAvailable_Rest

Projet FastAPI minimal pour une API REST de disponibilité NFC.

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
docker build -t nfcavailable-rest .
```

Exécutez le conteneur Docker :

```bash
docker run -p 6543:6543 nfcavailable-rest
```

## Versioning API

L'API est structurée avec un système de versioning. Pour l'instant, seule la version `v1` est disponible.

Tous les endpoints sont préfixés par `/v1` :

- `GET /v1/health`
- `POST /v1/login`
- `GET /v1/checkTag`

## Structure du projet

- `src/nfc_available_rest` - paquet d'application
- `run.py` - lanceur de développement (exécute uvicorn)
- `tests` - tests pytest
- `Dockerfile` - construction de l'image conteneur

## Authentification

Le projet inclut un endpoint d'authentification JWT :

- `POST /login` : accepte `{ "username": "...", "password": "..." }` et retourne un jeton JWT en cas d'authentification réussie.

Utilisateurs de test (déclarés dans `src/nfc_available_rest/auth.py`) :

- `Matthieu` / `MdP`
- `Karine` / `MdP`

Exemple :

```bash
curl -X POST http://localhost:6543/login -H "Content-Type: application/json" \
	-d '{"username":"Matthieu","password":"MdP"}'
```

La réponse contient `access_token` et `token_type`.

Note : la clé secrète JWT est définie dans `src/nfc_available_rest/auth.py`; changez-la en production.

## Débogage VS Code

Un fichier de configuration de débogage est disponible : `.vscode/launch.json`.

 - Configuration **FastAPI Debug** : lance `uvicorn` en mode reload sur le port `6543`.
 - Configuration **Pytest Debug** : lance `pytest` en mode debug.

Lancez-le depuis VS Code (F5) et choisissez la configuration souhaitée.

## Logs

Le projet configure un logging rotatif au démarrage via `src/nfc_available_rest/logging_config.py`.

- Dossier par défaut : `logs/`
- Fichier par défaut : `logs/nfc_available_rest.log`
- Rotation : 5 fichiers de backup, ~5 MB par fichier (configurable dans `logging_config.configure_logging`).

Personnalisation rapide :

```bash
# Changer le dossier de logs
export LOG_DIR=/var/log/nfc_available_rest

# Démarrer l'application
python run.py

# Consulter les logs en temps réel
tail -f logs/nfc_available_rest.log
```

Pour modifier le niveau ou la rotation, éditez `src/nfc_available_rest/logging_config.py` ou fournissez des variables d'environnement avant le démarrage.

## Base de données

Le projet utilise SQLite pour la gestion des tags disponibles.

- Dossier par défaut : `db/`
- Fichier par défaut : `db/nfc_available.db`
- Table principale : `availableTag` (colonne `tag` en clé primaire)

### Initialisation

Initialiser la base de données avant le premier lancement :

```bash
python init_db.py
```

Fonctions disponibles dans `src/nfc_available_rest/database.py` :

- `tag_exists(tag: str) -> bool` : vérifie si un tag existe
- `add_tag(tag: str) -> bool` : ajoute un tag
- `remove_tag(tag: str) -> bool` : supprime un tag
- `list_tags() -> list` : récupère tous les tags

### Exemple d'utilisation de `add_tag` (Python)

Vous pouvez utiliser les fonctions de `database.py` directement depuis un script Python :

```python
from nfc_available_rest import database as db

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
export DB_DIR=/var/lib/nfc_available
python init_db.py
python run.py
```

## Vérification d'un tag NFC

Le projet inclut un endpoint de vérification NFC :

- `GET /v1/checkTag` : endpoint pour vérifier un tag NFC. L'accès est protégé et nécessite un jeton JWT valide.

Test inclus : `tests/test_checkNFC.py` vérifie que l'accès sans jeton retourne une erreur 401 avec le message `"Accès refusé"`.

Exemples :

Accès sans jeton (réponse attendue : 401) :

```bash
curl -v -X GET http://localhost:6543/v1/checkTag -H "Content-Type: application/json" -d '{"tag":"4e5656545654"}'
# -> réponse: HTTP/1.1 401 { "detail": "Accès refusé" }
```

Accès avec jeton valide :

```bash
# Obtenir un token
TOKEN=$(curl -s -X POST http://localhost:6543/v1/login -H "Content-Type: application/json" -d '{"username":"Matthieu","password":"MdP"}' | jq -r '.access_token')

# Appeler checkTag avec le token
curl -X GET http://localhost:6543/v1/checkTag -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"tag":"4e5656545654"}'
# -> réponse: { "result": "OK" }
```


## Prochaines étapes

- Implémentez l'intégration réelle du lecteur NFC dans `src/nfc_available_rest/app.py`.
- Configurez CI pour exécuter les tests et construire l'image.
