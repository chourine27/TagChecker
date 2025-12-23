import pytest
import sys
import importlib
from pathlib import Path

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os


@pytest.mark.parametrize("tag_value", ["tag1", "4e5656545654"])
def test_add_and_remove_tag(tmp_path, monkeypatch, tag_value):
    """Teste l'ajout d'un nouveau tag, l'échec sur doublon, la liste et la suppression."""
    # Configurer un dossier de base de données temporaire
    db_dir = tmp_path / "db"
    monkeypatch.setenv("DB_DIR", str(db_dir))

    # Importer (ou recharger) le module database après avoir défini DB_DIR
    db_mod = importlib.import_module("tagChecker_rest.database")
    importlib.reload(db_mod)

    # Initialiser la base et vérifier l'ajout
    db_mod.init_db()

    # Ajout initial -> doit réussir
    assert db_mod.add_tag(tag_value) is True
    assert db_mod.tag_exists(tag_value) is True

    # Ajout du même tag -> doit échouer (integrity error)
    assert db_mod.add_tag(tag_value) is False

    # Vérifier la liste des tags
    tags = db_mod.list_tags()
    assert tag_value in tags

    # Supprimer le tag -> doit réussir
    assert db_mod.remove_tag(tag_value) is True
    assert db_mod.tag_exists(tag_value) is False
