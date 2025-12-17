"""Configuration et gestion de la base de données SQLite."""

import sqlite3
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

DB_DIR = os.getenv("DB_DIR", "db")
DB_PATH = os.path.join(DB_DIR, "nfc_available.db")


def get_connection() -> sqlite3.Connection:
    """Obtient une connexion à la base de données SQLite."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def verifier_fichier_existe():
    """Vérifie si le fichier de la base de données existe."""
    if os.path.exists(DB_PATH):
        logger.info(f"✅ Le fichier '{DB_PATH}' existe.")
        return True
    else:
        logger.info(f"❌ Le fichier '{DB_PATH}' n'existe PAS.")
        return False
    
def init_db() -> None:
    """Initialise la base de données avec la table availableTag."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Créer la table availableTag
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS availableTag (
            tag TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"Base de données initialisée: {DB_PATH}")


def tag_exists(tag: str) -> bool:
    """Vérifie si un tag existe dans la base de données."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM availableTag WHERE tag = ?", (tag,))
    result = cursor.fetchone() is not None
    conn.close()
    return result


def add_tag(tag: str) -> bool:
    """Ajoute un tag à la base de données. Retourne True si succès."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO availableTag (tag) VALUES (?)", (tag,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError as e:
        logger.error(f"Erreur d'intégrité lors de l'ajout du tag '{tag}': le tag existe déjà", exc_info=True)
        return False


def remove_tag(tag: str) -> bool:
    """Supprime un tag de la base de données. Retourne True si succès."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM availableTag WHERE tag = ?", (tag,))
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    return rows_deleted > 0


def list_tags() -> list:
    """Récupère la liste de tous les tags disponibles."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT tag FROM availableTag ORDER BY created_at")
    tags = [row["tag"] for row in cursor.fetchall()]
    conn.close()
    return tags


if __name__ == "__main__":
    init_db()
