import pytest
from httpx import AsyncClient, ASGITransport
import sys
from pathlib import Path
import importlib

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tagChecker_rest.app import app


@pytest.mark.asyncio
async def test_health():
    """Teste l'endpoint de santé."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/v1/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_add_tag_sans_authentification():
    """Teste l'endpoint d'ajout de tag sans token JWT."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/v1/tag", json={"tag": "test_tag"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_add_tag_avec_authentification(tmp_path, monkeypatch):
    """Teste l'endpoint d'ajout de tag avec authentification valide."""
    # Configurer un dossier de base de données temporaire
    db_dir = tmp_path / "db"
    monkeypatch.setenv("DB_DIR", str(db_dir))

    # Recharger les modules pour prendre en compte la nouvelle DB
    db_mod = importlib.import_module("tagChecker_rest.database")
    importlib.reload(db_mod)

    tag_manager_mod = importlib.import_module("tagChecker_rest.tagManager")
    importlib.reload(tag_manager_mod)

    app_mod = importlib.import_module("tagChecker_rest.app")
    importlib.reload(app_mod)

    async with AsyncClient(transport=ASGITransport(app=app_mod.app), base_url="http://test") as ac:
        # Se connecter pour obtenir un token
        login_response = await ac.post(
            "/v1/login",
            json={"username": "Matthieu", "password": "MdP"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Ajouter un nouveau tag
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.post(
            "/v1/tag",
            json={"tag": "nouveau_tag_123"},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json() == {"result": "OK"}

        # Vérifier que le tag a bien été ajouté
        assert db_mod.tag_exists("nouveau_tag_123") is True


@pytest.mark.asyncio
async def test_add_tag_avec_majuscule_Tag(tmp_path, monkeypatch):
    """Teste l'endpoint avec la clé 'Tag' en majuscule."""
    # Configurer un dossier de base de données temporaire
    db_dir = tmp_path / "db"
    monkeypatch.setenv("DB_DIR", str(db_dir))

    # Recharger les modules
    db_mod = importlib.import_module("tagChecker_rest.database")
    importlib.reload(db_mod)

    tag_manager_mod = importlib.import_module("tagChecker_rest.tagManager")
    importlib.reload(tag_manager_mod)

    app_mod = importlib.import_module("tagChecker_rest.app")
    importlib.reload(app_mod)

    async with AsyncClient(transport=ASGITransport(app=app_mod.app), base_url="http://test") as ac:
        # Se connecter
        login_response = await ac.post(
            "/v1/login",
            json={"username": "Matthieu", "password": "MdP"}
        )
        token = login_response.json()["access_token"]

        # Ajouter un tag avec la clé "Tag" en majuscule
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.post(
            "/v1/tag",
            json={"Tag": "tag_majuscule_456"},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json() == {"result": "OK"}

        # Vérifier que le tag a bien été ajouté
        assert db_mod.tag_exists("tag_majuscule_456") is True


@pytest.mark.asyncio
async def test_add_tag_deja_existant(tmp_path, monkeypatch):
    """Teste l'ajout d'un tag qui existe déjà (doit retourner OK)."""
    # Configurer un dossier de base de données temporaire
    db_dir = tmp_path / "db"
    monkeypatch.setenv("DB_DIR", str(db_dir))

    # Recharger les modules
    db_mod = importlib.import_module("tagChecker_rest.database")
    importlib.reload(db_mod)

    tag_manager_mod = importlib.import_module("tagChecker_rest.tagManager")
    importlib.reload(tag_manager_mod)

    app_mod = importlib.import_module("tagChecker_rest.app")
    importlib.reload(app_mod)

    async with AsyncClient(transport=ASGITransport(app=app_mod.app), base_url="http://test") as ac:
        # Se connecter
        login_response = await ac.post(
            "/v1/login",
            json={"username": "Matthieu", "password": "MdP"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Ajouter le tag une première fois
        response1 = await ac.post(
            "/v1/tag",
            json={"tag": "duplicate_tag"},
            headers=headers
        )
        assert response1.status_code == 200

        # Ajouter le même tag une deuxième fois
        response2 = await ac.post(
            "/v1/tag",
            json={"tag": "duplicate_tag"},
            headers=headers
        )
        assert response2.status_code == 200
        assert response2.json() == {"result": "OK"}