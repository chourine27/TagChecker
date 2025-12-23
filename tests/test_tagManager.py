import pytest
import sys
import importlib
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import logging

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.mark.parametrize("tag_value", ["tag1", "4e5656545654", "test_tag_123"])
def test_ajouter_tag_nouveau(tmp_path, monkeypatch, tag_value):
    """Teste l'ajout d'un nouveau tag qui n'existe pas encore."""
    # Configurer un dossier de base de données temporaire
    db_dir = tmp_path / "db"
    monkeypatch.setenv("DB_DIR", str(db_dir))

    # Importer (ou recharger) les modules après avoir défini DB_DIR
    db_mod = importlib.import_module("tagChecker_rest.database")
    importlib.reload(db_mod)

    tag_manager_mod = importlib.import_module("tagChecker_rest.tagManager")
    importlib.reload(tag_manager_mod)

    # Créer une instance de TagManager (initialise la DB si nécessaire)
    tag_manager = tag_manager_mod.TagManager()

    # Ajouter un nouveau tag
    result = tag_manager.ajouter_tag(tag_value)

    # Vérifications
    assert result is True
    assert db_mod.tag_exists(tag_value) is True


@pytest.mark.parametrize("tag_value", ["duplicate_tag", "another_duplicate"])
def test_ajouter_tag_existant(tmp_path, monkeypatch, tag_value):
    """Teste l'ajout d'un tag qui existe déjà (doit retourner True sans erreur)."""
    # Configurer un dossier de base de données temporaire
    db_dir = tmp_path / "db"
    monkeypatch.setenv("DB_DIR", str(db_dir))

    # Importer (ou recharger) les modules après avoir défini DB_DIR
    db_mod = importlib.import_module("tagChecker_rest.database")
    importlib.reload(db_mod)

    tag_manager_mod = importlib.import_module("tagChecker_rest.tagManager")
    importlib.reload(tag_manager_mod)

    # Créer une instance de TagManager
    tag_manager = tag_manager_mod.TagManager()

    # Ajouter le tag une première fois
    first_result = tag_manager.ajouter_tag(tag_value)
    assert first_result is True

    # Ajouter le même tag une deuxième fois
    second_result = tag_manager.ajouter_tag(tag_value)

    # Vérifications: doit retourner True (le tag existe déjà, rien à faire)
    assert second_result is True
    assert db_mod.tag_exists(tag_value) is True


def test_ajouter_tag_echec_insertion(tmp_path, monkeypatch):
    """Teste le comportement quand add_tag échoue."""
    # Configurer un dossier de base de données temporaire
    db_dir = tmp_path / "db"
    monkeypatch.setenv("DB_DIR", str(db_dir))

    # Importer (ou recharger) les modules après avoir défini DB_DIR
    db_mod = importlib.import_module("tagChecker_rest.database")
    importlib.reload(db_mod)

    tag_manager_mod = importlib.import_module("tagChecker_rest.tagManager")
    importlib.reload(tag_manager_mod)

    # Créer une instance de TagManager
    tag_manager = tag_manager_mod.TagManager()

    # Simuler un échec de add_tag
    with patch("tagChecker_rest.tagManager.add_tag", return_value=False):
        with patch("tagChecker_rest.tagManager.tag_exists", return_value=False):
            result = tag_manager.ajouter_tag("failing_tag")

            # Vérifications: doit retourner False en cas d'échec
            assert result is False


def test_init_tagmanager_db_inexistante(tmp_path, monkeypatch):
    """Teste l'initialisation de TagManager quand la base de données n'existe pas."""
    # Configurer un dossier de base de données temporaire
    db_dir = tmp_path / "db"
    monkeypatch.setenv("DB_DIR", str(db_dir))

    # Importer (ou recharger) les modules après avoir défini DB_DIR
    db_mod = importlib.import_module("tagChecker_rest.database")
    importlib.reload(db_mod)

    tag_manager_mod = importlib.import_module("tagChecker_rest.tagManager")
    importlib.reload(tag_manager_mod)

    # Vérifier que la DB n'existe pas encore
    assert db_mod.verifier_fichier_existe() is False

    # Créer une instance de TagManager (doit initialiser la DB)
    tag_manager = tag_manager_mod.TagManager()

    # Vérifier que la DB existe maintenant
    assert db_mod.verifier_fichier_existe() is True


def test_init_tagmanager_db_existante(tmp_path, monkeypatch):
    """Teste l'initialisation de TagManager quand la base de données existe déjà."""
    # Configurer un dossier de base de données temporaire
    db_dir = tmp_path / "db"
    monkeypatch.setenv("DB_DIR", str(db_dir))

    # Importer (ou recharger) les modules après avoir défini DB_DIR
    db_mod = importlib.import_module("tagChecker_rest.database")
    importlib.reload(db_mod)

    tag_manager_mod = importlib.import_module("tagChecker_rest.tagManager")
    importlib.reload(tag_manager_mod)

    # Initialiser la DB manuellement
    db_mod.init_db()
    assert db_mod.verifier_fichier_existe() is True

    # Créer une instance de TagManager (ne doit pas réinitialiser)
    tag_manager = tag_manager_mod.TagManager()

    # Vérifier que la DB existe toujours
    assert db_mod.verifier_fichier_existe() is True


def test_ajouter_plusieurs_tags(tmp_path, monkeypatch):
    """Teste l'ajout de plusieurs tags différents."""
    # Configurer un dossier de base de données temporaire
    db_dir = tmp_path / "db"
    monkeypatch.setenv("DB_DIR", str(db_dir))

    # Importer (ou recharger) les modules après avoir défini DB_DIR
    db_mod = importlib.import_module("tagChecker_rest.database")
    importlib.reload(db_mod)

    tag_manager_mod = importlib.import_module("tagChecker_rest.tagManager")
    importlib.reload(tag_manager_mod)

    # Créer une instance de TagManager
    tag_manager = tag_manager_mod.TagManager()

    # Liste de tags à ajouter
    tags = ["tag1", "tag2", "tag3", "123456789"]

    # Ajouter tous les tags
    for tag in tags:
        result = tag_manager.ajouter_tag(tag)
        assert result is True

    # Vérifier que tous les tags existent
    for tag in tags:
        assert db_mod.tag_exists(tag) is True

    # Vérifier la liste complète des tags
    all_tags = db_mod.list_tags()
    for tag in tags:
        assert tag in all_tags


def test_ajouter_tag_vide(tmp_path, monkeypatch):
    """Teste l'ajout d'un tag vide."""
    # Configurer un dossier de base de données temporaire
    db_dir = tmp_path / "db"
    monkeypatch.setenv("DB_DIR", str(db_dir))

    # Importer (ou recharger) les modules après avoir défini DB_DIR
    db_mod = importlib.import_module("tagChecker_rest.database")
    importlib.reload(db_mod)

    tag_manager_mod = importlib.import_module("tagChecker_rest.tagManager")
    importlib.reload(tag_manager_mod)

    # Créer une instance de TagManager
    tag_manager = tag_manager_mod.TagManager()

    # Essayer d'ajouter un tag vide (devrait fonctionner techniquement)
    result = tag_manager.ajouter_tag("")
    assert result is True
    assert db_mod.tag_exists("") is True


def test_ajouter_tag_avec_caracteres_speciaux(tmp_path, monkeypatch):
    """Teste l'ajout de tags avec des caractères spéciaux."""
    # Configurer un dossier de base de données temporaire
    db_dir = tmp_path / "db"
    monkeypatch.setenv("DB_DIR", str(db_dir))

    # Importer (ou recharger) les modules après avoir défini DB_DIR
    db_mod = importlib.import_module("tagChecker_rest.database")
    importlib.reload(db_mod)

    tag_manager_mod = importlib.import_module("tagChecker_rest.tagManager")
    importlib.reload(tag_manager_mod)

    # Créer une instance de TagManager
    tag_manager = tag_manager_mod.TagManager()

    # Tags avec caractères spéciaux
    special_tags = [
        "tag-with-dash",
        "tag_with_underscore",
        "tag.with.dots",
        "tag:with:colons",
        "tag@with@at"
    ]

    for tag in special_tags:
        result = tag_manager.ajouter_tag(tag)
        assert result is True
        assert db_mod.tag_exists(tag) is True


def test_logging_ajouter_tag_nouveau(tmp_path, monkeypatch, caplog):
    """Teste que les logs appropriés sont générés lors de l'ajout d'un nouveau tag."""
    # Configurer un dossier de base de données temporaire
    db_dir = tmp_path / "db"
    monkeypatch.setenv("DB_DIR", str(db_dir))

    # Importer (ou recharger) les modules après avoir défini DB_DIR
    db_mod = importlib.import_module("tagChecker_rest.database")
    importlib.reload(db_mod)

    tag_manager_mod = importlib.import_module("tagChecker_rest.tagManager")
    importlib.reload(tag_manager_mod)

    # Créer une instance de TagManager
    tag_manager = tag_manager_mod.TagManager()

    # Activer la capture des logs
    with caplog.at_level(logging.INFO):
        result = tag_manager.ajouter_tag("test_log_tag")

    # Vérifier les logs
    assert "C'est bon le tag n'existe pas, on peut le créer" in caplog.text
    assert "Le tag a été ajouté" in caplog.text


def test_logging_ajouter_tag_existant(tmp_path, monkeypatch, caplog):
    """Teste que les logs appropriés sont générés lors de l'ajout d'un tag existant."""
    # Configurer un dossier de base de données temporaire
    db_dir = tmp_path / "db"
    monkeypatch.setenv("DB_DIR", str(db_dir))

    # Importer (ou recharger) les modules après avoir défini DB_DIR
    db_mod = importlib.import_module("tagChecker_rest.database")
    importlib.reload(db_mod)

    tag_manager_mod = importlib.import_module("tagChecker_rest.tagManager")
    importlib.reload(tag_manager_mod)

    # Créer une instance de TagManager
    tag_manager = tag_manager_mod.TagManager()

    # Ajouter le tag une première fois
    tag_manager.ajouter_tag("duplicate_log_tag")

    # Activer la capture des logs pour le deuxième ajout
    with caplog.at_level(logging.INFO):
        caplog.clear()
        result = tag_manager.ajouter_tag("duplicate_log_tag")

    # Vérifier les logs
    assert "Le tag existe déjà, rien à faire" in caplog.text
