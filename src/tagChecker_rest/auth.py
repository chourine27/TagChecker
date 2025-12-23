"""Module d'authentification avec JWT."""

import jwt as pyjwt
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Configuration JWT
SECRET_KEY = "votre-clé-secrète-à-changer-en-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Utilisateurs de test (en prod, utiliser une base de données)
FAKE_USERS_DB = {
    "Matthieu": "MdP",
    "Karine": "MdP"
}

security = HTTPBearer()
logger = logging.getLogger(__name__)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


def créer_token(données: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un JWT token."""
    données_à_encoder = données.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    données_à_encoder.update({"exp": expire})
    token_encodé = pyjwt.encode(données_à_encoder, SECRET_KEY, algorithm=ALGORITHM)
    # pyjwt.encode() retourne un str en PyJWT >= 2.0
    if isinstance(token_encodé, bytes):
        token_encodé = token_encodé.decode('utf-8')
    return token_encodé


def vérifier_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Vérifie et décode un JWT token."""
    token = credentials.credentials
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        return username
    except pyjwt.ExpiredSignatureError as e:
        logger.error("Token expiré lors de la vérification du token", exc_info=True)
        raise HTTPException(status_code=401, detail="Token expiré")
    except pyjwt.InvalidTokenError as e:
        logger.error("Token invalide ou décodage échoué lors de la vérification du token", exc_info=True)
        raise HTTPException(status_code=401, detail="Token invalide")


def valider_identifiants(username: str, password: str) -> bool:
    """Valide les identifiants de l'utilisateur."""
    if username in FAKE_USERS_DB:
        return FAKE_USERS_DB[username] == password
    return False
