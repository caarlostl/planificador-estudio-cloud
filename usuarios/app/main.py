
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from pwdlib import PasswordHash
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from . import models
from .database import get_db

app = FastAPI(
    title="Microservicio de usuarios",
    description="Gestión de cuentas de estudiantes",
    version="1.0.0"
)

password_hash = PasswordHash.recommended()

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("No se ha encontrado JWT_SECRET_KEY")

JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30


class UsuarioRegistro(BaseModel):
    nombre: str
    email: EmailStr
    password: str

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

def crear_token_acceso(estudiante_id: int):
    ahora = datetime.now(timezone.utc)

    datos_token = {
        "sub": str(estudiante_id),
        "iat": ahora,
        "exp": ahora + timedelta(
            minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    }

    return jwt.encode(
        datos_token,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

@app.get("/")
def comprobar_servicio():
    return {"mensaje": "Microservicio de usuarios funcionando"}


@app.post("/usuarios/registro")
def registrar_usuario(
    usuario: UsuarioRegistro,
    db: Session = Depends(get_db)
):
    usuario_existente = db.query(models.Usuario).filter(
        models.Usuario.email == usuario.email
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="El correo electrónico ya está registrado"
        )

    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        password_hash=password_hash.hash(usuario.password)
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "mensaje": "Usuario registrado correctamente",
        "usuario": {
            "id": nuevo_usuario.id,
            "nombre": nuevo_usuario.nombre,
            "email": nuevo_usuario.email
        }
    }

@app.post("/usuarios/login")
def iniciar_sesion(
    usuario: UsuarioLogin,
    db: Session = Depends(get_db)
):
    usuario_db = db.query(models.Usuario).filter(
        models.Usuario.email == usuario.email
    ).first()

    if not usuario_db or not password_hash.verify(
        usuario.password,
        usuario_db.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Correo electrónico o contraseña incorrectos"
        )

    token = crear_token_acceso(usuario_db.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }