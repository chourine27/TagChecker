import sys
import importlib
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest


def load_ewelink_manager():
    """Import the module with a stubbed pysonofflan dependency."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    fake_pysonofflan = ModuleType("pysonofflan")
    fake_pysonofflan.SonoffSwitch = MagicMock(name="SonoffSwitch")
    sys.modules["pysonofflan"] = fake_pysonofflan

    mod = importlib.import_module("tagChecker_rest.ewelinkManager")
    importlib.reload(mod)
    return mod


@pytest.mark.asyncio
async def test_connecter_appelle_client():
    mod = load_ewelink_manager()

    switch_instance = MagicMock()
    client_mock = MagicMock(return_value=switch_instance)
    mod.SonoffSwitch = client_mock

    manager = mod.EwelinkManager()
    result = await manager.connecter()

    assert result is True
    client_mock.assert_any_call("192.168.45.59")
    client_mock.assert_any_call("192.168.45.60")
    assert client_mock.call_count == 2


@pytest.mark.asyncio
async def test_lister_les_appareils_retourne_liste():
    mod = load_ewelink_manager()

    manager = mod.EwelinkManager()
    result = await manager.lister_les_appareils()

    assert result == ["Appareil1", "Appareil2", "Appareil3"]


@pytest.mark.asyncio
async def test_activer_appareil_retourne_true():
    mod = load_ewelink_manager()

    manager = mod.EwelinkManager()
    result = await manager.activer_appareil("device-1")

    assert result is True


@pytest.mark.asyncio
async def test_desactiver_appareil_retourne_true():
    mod = load_ewelink_manager()

    manager = mod.EwelinkManager()
    result = await manager.desactiver_appareil("device-2")

    assert result is True


@pytest.mark.asyncio
async def test_retourner_etat_appareil_retourne_on():
    mod = load_ewelink_manager()

    manager = mod.EwelinkManager()
    result = await manager.retourner_etat_appareil("device-3")

    assert result == "ON"
