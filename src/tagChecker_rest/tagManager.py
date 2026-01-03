""" Module de gestion des tags """

import logging
from .database import (
    add_tag,
    remove_tag,
    init_db,
    tag_exists,
    verifier_fichier_existe
)


class TagManager:

    """
    Gère les opérations CRUD (Créer, Lire, Modifier, Supprimer)
    """

    def __init__(self):
        if verifier_fichier_existe() is False:
            logging.info("La base de données n'existe pas, initialisation")
            init_db()

    def ajouter_tag(self, nouveau_tag: str) -> bool:
        """Ajoute un tag à la base de donnée."""
        if tag_exists(nouveau_tag) is False:
            logging.info("C'est bon le tag n'existe pas, on peut le créer")
            if add_tag(nouveau_tag) is False:
                logging.error(f"Le tag {nouveau_tag} n'a pas pu être ajouté")
                return False
            logging.info("Le tag a été ajouté")
        else:
            logging.info("Le tag existe déjà, rien à faire")
        return True

    def supprimer_tag(self, tag_a_supprimer: str) -> bool:
        """Supprime un tag de la base de donnée."""
        if tag_exists(tag_a_supprimer) is True:
            logging.info("Le tag existe, on peut le supprimer")
            if remove_tag(tag_a_supprimer) is False:
                logging.error(f"Le tag {tag_a_supprimer} n'a pas pu être supprimé")
                return False
            logging.info("Le tag a été supprimé")
        else:
            logging.info("Le tag n'existe pas, rien à faire")
        return True

    def existance_tag(self, tag_a_verifier: str) -> bool:
        """Vérifie l'existence d'un tag dans la base de donnée."""
        return tag_exists(tag_a_verifier)
