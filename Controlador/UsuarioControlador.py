#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Controlador (Router) de FastAPI para operaciones sobre Usuario.
Implementa el CRUD completo, incluyendo el método PATCH para actualizaciones parciales.
"""
from typing import List, Optional, Generator
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from Modelo.Usuario import Usuario
from DAOs.DB import get_session
from Servicios.UsuarioServicio import UsuarioServicio
from DAOs.UsuarioDAO import UsuarioDAO
from sqlalchemy.orm import Session

class UsuarioActualizarParcial(BaseModel):
    nombre: Optional[str] = Field(default=None, description="Nuevo nombre del usuario")
    email: Optional[EmailStr] = Field(default=None, description="Nuevo email del usuario (debe ser único)")
    rol: Optional[str] = Field(default=None, description="Nuevo rol del usuario ('user' o 'admin')")
    activo: Optional[bool] = Field(default=None, description="Estado de actividad del usuario")

class UsuarioCambiarPassword(BaseModel):
    nueva_password: str = Field(..., min_length=6, description="Nueva contraseña del usuario")

class UsuarioCrear(BaseModel):
    nombre: str
    email: EmailStr
    rol: str
    activo: bool = True
    password: str

class UsuarioActualizarCompleto(BaseModel):
    nombre: str
    email: EmailStr
    rol: str
    activo: bool

class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str
    activo: bool

    model_config = {"from_attributes": True}

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

# --- Router ---
router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"],
)

# --- Dependencias ---

def get_db() -> Generator[Session, None, None]:
    """Dependencia de sesión de DB, manejada por FastAPI."""
    with get_session() as db:
        yield db

def get_usuario_servicio(db: Session = Depends(get_db)) -> UsuarioServicio:
    """Crea UsuarioServicio con el DAO inyectado automáticamente."""
    dao = UsuarioDAO(db)
    return UsuarioServicio(dao)

# --- Endpoints CRUD y login ---

@router.post("/", response_model=UsuarioRespuesta)
def crear_usuario(
    usuario: UsuarioCrear,
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    datos = usuario.model_dump()
    password = datos.pop("password")
    try:
        return servicio.crear_usuario(datos, password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {e}")

@router.get("/", response_model=List[UsuarioRespuesta])
def listar_usuarios(servicio: UsuarioServicio = Depends(get_usuario_servicio)):
    return servicio.listar_usuarios()

@router.post("/login", status_code=status.HTTP_200_OK)
def login(credenciales: UsuarioLogin, servicio: UsuarioServicio = Depends(get_usuario_servicio)):
    if not servicio.verificar_contraseña(credenciales.email, credenciales.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    usuario = servicio.dao.get_by_email(credenciales.email)
    return {
        "mensaje": "Login exitoso",
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "rol": usuario.rol
        }
    }

@router.get("/{usuario_id}", response_model=UsuarioRespuesta)
def obtener_usuario(usuario_id: int, servicio: UsuarioServicio = Depends(get_usuario_servicio)):
    usuario = servicio.obtener_usuario(usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail=f"Usuario con id={usuario_id} no encontrado")
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioRespuesta)
def actualizar_usuario(
    usuario_id: int,
    datos_usuario: UsuarioActualizarCompleto,
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    try:
        return servicio.actualizar_usuario(usuario_id, datos_usuario.model_dump())
    except ValueError as e:
        detail = str(e)
        if f"id={usuario_id} no existe" in detail:
            raise HTTPException(status_code=404, detail=detail)
        raise HTTPException(status_code=400, detail=detail)

@router.patch("/{usuario_id}", response_model=UsuarioRespuesta)
def actualizar_parcialmente_usuario(
    usuario_id: int,
    datos_parciales: UsuarioActualizarParcial,
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    data_dict = datos_parciales.model_dump(exclude_unset=True)
    if not data_dict:
        raise HTTPException(status_code=400, detail="Se debe proporcionar al menos un campo")
    try:
        return servicio.actualizar_usuario(usuario_id, data_dict)
    except ValueError as e:
        detail = str(e)
        if f"id={usuario_id} no existe" in detail:
            raise HTTPException(status_code=404, detail=detail)
        raise HTTPException(status_code=400, detail=detail)

@router.patch("/{usuario_id}/password", status_code=status.HTTP_200_OK)
def cambiar_password(
    usuario_id: int,
    datos: UsuarioCambiarPassword,
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    try:
        servicio.actualizar_contraseña(usuario_id, datos.nueva_password)
        return {"mensaje": f"Contraseña de usuario {usuario_id} actualizada correctamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar contraseña: {e}")

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(usuario_id: int, servicio: UsuarioServicio = Depends(get_usuario_servicio)):
    servicio.eliminar_usuario(usuario_id)
