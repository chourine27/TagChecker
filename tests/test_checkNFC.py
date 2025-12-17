import pytest
from httpx import AsyncClient, ASGITransport
import sys
from pathlib import Path

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nfc_available_rest.app import app


@pytest.mark.asyncio
async def test_checkNFC():
    """Teste l'endpoint de vérification de tag NFC sans jeton."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/checkNFC",
            json={"tag": ""}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Accès refusé"