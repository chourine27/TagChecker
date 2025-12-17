""" Module de gestion des tag """

import logging
from .database import (
    add_tag,
    get_connection,
    init_db,
    tag_exists,
    verifier_fichier_existe
)

class TagManager:

    """
    Gère les opérations CRUD (Créer, Lire, Modifier, Supprimer)
    """  

    def __init__(self):
        if verifier_fichier_existe() is False :
            logging.info("La base de données n'existe pas, initialisation")
            init_db()

    def ajouter_tag(self, nouveau_tag: str) -> bool:
        """Ajoute un tag à la base de donnée."""
        if tag_exists(nouveau_tag) is False :
            logging.info("C'est bon le tag n'existe pas, on peut le créer")
            if add_tag(nouveau_tag) is False :
                logging.error(f"Le tag {nouveau_tag} n'a pas pu être ajouté")
                return False
            logging.info("Le tag a été ajouté")
        else :
            logging.info("Le tag existe déjà, rien à faire")
        return True
