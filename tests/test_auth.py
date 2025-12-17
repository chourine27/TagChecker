"""Tests d'authentification JWT."""

import pytest
from httpx import AsyncClient, ASGITransport
import sys
from pathlib import Path

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nfc_available_rest.app import app


@pytest.mark.asyncio
async def test_login_succès():
    """Teste une authentification réussie avec identifiants valides."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/login",
            json={"username": "Matthieu", "password": "MdP"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_mot_de_passe_incorrect():
    """Teste une authentification échouée avec mot de passe incorrect."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/login",
            json={"username": "Matthieu", "password": "mauvais_mot_de_passe"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Identifiants invalides"


@pytest.mark.asyncio
async def test_login_utilisateur_inexistant():
    """Teste une authentification échouée avec utilisateur inexistant."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/login",
            json={"username": "utilisateur_inexistant", "password": "password123"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Identifiants invalides"


@pytest.mark.asyncio
async def test_login_avec_user_valide():
    """Teste une authentification réussie avec l'utilisateur 'user'."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/login",
            json={"username": "Karine", "password": "MdP"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
