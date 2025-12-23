#!/usr/bin/env python3
"""Script d'initialisation de la base de données."""

import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from tagChecker_rest.database import init_db

if __name__ == "__main__":
    init_db()
    logger.info("Initialisation terminée avec succès.")
