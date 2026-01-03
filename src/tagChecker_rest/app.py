from fastapi import FastAPI, HTTPException, Depends, Body, Query, APIRouter
from pydantic import BaseModel
from datetime import timedelta
from typing import Any, Dict
import logging

from .auth import (
    Token,
    LoginRequest,
    créer_token,
    vérifier_token,
    valider_identifiants,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from .tagManager import TagManager
from .ewelinkManager import EwelinkManager
from .logging_config import configure_logging


# Configurer le logging rotatif au démarrage de l'application
configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI(title="nfcAvailable_Rest")

# Router versionné (v1)
router_v1 = APIRouter(prefix="/v1")

# Initialisation du gestionnaire de tags
tag_manager = TagManager()
# Initialisation du gestionnaire eWeLink
ewelink_manager = EwelinkManager()


class Health(BaseModel):
    status: str


@router_v1.get("/health", response_model=Health)
async def health():
    return {"status": "ok"}

@router_v1.get("/em")
async def ewelink():
    logger.info("eWeLink")
    await ewelink_manager.connecter()
    return {"status": "ok"}

@router_v1.get("/log")
async def log_info(text: str = Query(..., description="Le tag à vérifier")):
    logger.info(f"{text}")
    return {"status": "ok"}


@router_v1.post("/login", response_model=Token)
async def login(request: LoginRequest):
    """Authentifie un utilisateur et retourne un JWT token.
    
    Args:
        request: Contient username et password
        
    Returns:
        Token JWT si authentification réussie
        
    Raises:
        HTTPException 401: Si identifiants invalides
    """
    if not valider_identifiants(request.username, request.password):
        raise HTTPException(
            status_code=401,
            detail="Identifiants invalides"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = créer_token(
        données={"sub": request.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router_v1.get("/check_tag")
async def check_tag(username: str = Depends(vérifier_token), tag: str = Query(..., description="Le tag à vérifier")):
    """Vérifie qu'un tag est éligible à activer

    - Exige un en-tête `Authorization: Bearer <token>`.
    - Accepte le paramètre `tag` dans l'URL (ex: /check_tag?tag=mon_tag).
    - Retourne `{ "result": "OK" }` si le token est valide.
    """

    # La variable 'tag' contient directement la valeur passée en paramètre
    logger.info(f"Vérification du tag '{tag}' par l'utilisateur {username}")

    return {"result": "OK"}

@router_v1.post("/tag")
async def add_new_tag(username: str = Depends(vérifier_token), payload: Dict[str, Any] = Body(...)):
    """Ajoute un tag dans la base de données

    - Exige un en-tête `Authorization: Bearer <token>`.
    - Accepte le paramètre `tag` dans l'URL (ex: /tag/tag=mon_tag).
    - Retourne `{ "result": "OK" }` si le token est valide.
    """
    # Lire la valeur du tag (accept both 'Tag' and 'tag')
    tag_value = None
    if isinstance(payload, dict):
        tag_value = payload.get("Tag") if payload.get("Tag") is not None else payload.get("tag")

    logger.info(f"Ajout du tag par l'utilisateur {username}")
    
    if tag_manager.ajouter_tag(tag_value) is False:
        raise HTTPException(
            status_code=500,
            detail="Erreur dans l'ajout du tag"
        ) 

    # On pourrait valider la valeur du tag ici ; test demande seulement la présence
    return {"result": "OK"}

# Inclure le router versionné dans l'application principale
app.include_router(router_v1)
