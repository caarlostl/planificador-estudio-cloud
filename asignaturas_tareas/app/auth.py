
import os

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"

if not JWT_SECRET_KEY:
    raise RuntimeError("No se ha encontrado JWT_SECRET_KEY")

bearer_scheme = HTTPBearer(auto_error=False)


def obtener_estudiante_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    if credenciales is None:
        raise HTTPException(
            status_code=401,
            detail="No se ha proporcionado un token de autenticación",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        contenido = jwt.decode(
            credenciales.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        estudiante_id = int(contenido["sub"])

    except (InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Token inválido o caducado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return estudiante_id
