from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI(
    title="Microservicio de usuarios",
    description="Gestión de cuentas de estudiantes",
    version="1.0.0"
)

#Modelo de datos para registrar un estudiante
class UsuarioRegistro(BaseModel):
    nombre: str
    email: EmailStr
    password: str

usuarios = []

@app.get("/")
def comprobar_servicio():
    return {"mensaje": "Microservicio de usuarios funcionando"}

@app.post("/usuarios/registro")
def registrar_usuario(usuario: UsuarioRegistro):
    if any(u["email"] == usuario.email for u in usuarios):
        raise HTTPException(
            status_code=400,
            detail="El correo electrónico ya está registrado"
        )

    nuevo_usuario = {
        "id": len(usuarios) + 1,
        "nombre": usuario.nombre,
        "email": usuario.email
    }

    usuarios.append(nuevo_usuario)

    return {
        "mensaje": "Usuario registrado correctamente",
        "usuario": nuevo_usuario
    }