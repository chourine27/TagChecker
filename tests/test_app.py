import pytest
from httpx import AsyncClient, ASGITransport
import sys
from pathlib import Path

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nfc_available_rest.app import app


@pytest.mark.asyncio
async def test_health():
    """Teste l'endpoint de santé."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}