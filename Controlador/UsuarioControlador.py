#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Controlador (Router) de FastAPI para operaciones sobre Usuario.

Implementa el CRUD completo, incluyendo el método PATCH para actualizaciones parciales.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr

# Importar el modelo y el servicio (Asegúrate de que estas rutas sean correctas)
from Modelo.Usuario import Usuario
from Servicios.UsuarioServicio import UsuarioServicio


# --- Esquemas de Datos para Solicitudes Específicas ---

# Esquema para Actualizaciones Parciales (PATCH)
# Define todos los campos como opcionales para permitir actualizaciones parciales.
class UsuarioActualizarParcial(BaseModel):
    # El ID no se incluye porque se toma de la URL
    nombre: str | None = Field(default=None, description="Nuevo nombre del usuario")
    email: str | None = Field(default=None, description="Nuevo email del usuario (debe ser único)")
    rol: str | None = Field(default=None, description="Nuevo rol del usuario ('user' o 'admin')")
    activo: bool | None = Field(default=None, description="Estado de actividad del usuario")

class UsuarioCambiarPassword(BaseModel):
    nueva_password: str = Field(..., min_length=6, description="Nueva contraseña del usuario")

class UsuarioCrear(BaseModel):
    nombre: str
    email: str
    rol: str
    activo: bool = True
    password: str
class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    activo: bool

    class Config:
        orm_mode = True

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

# --- Instancia del Router y Dependencia del Servicio ---

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"],
)


# Dependencia para obtener la instancia del servicio
def obtener_servicio_usuario() -> UsuarioServicio:
    """Retorna una instancia del servicio de usuario."""
    return UsuarioServicio()


# --- Endpoints CRUD ---

@router.post("/", response_model=UsuarioRespuesta)
def crear_usuario(
    usuario: UsuarioCrear,
    servicio: UsuarioServicio = Depends(obtener_servicio_usuario),
):
    try:
        # convertir datos excepto el password
        datos = usuario.dict()
        password = datos.pop("password")

        usuario_creado = servicio.crear_usuario(datos, password)
        return usuario_creado

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear usuario: {e}"
        )


@router.get(
    "/",
    response_model=List[Usuario], 
    summary="Listar todos los usuarios",
)
def listar_usuarios(
    servicio: UsuarioServicio = Depends(obtener_servicio_usuario),
):
    """
    Retorna la lista de todos los usuarios.
    """
    return servicio.listar_usuarios()

@router.post(
    "/login",
    summary="Autenticar usuario",
    status_code=status.HTTP_200_OK
)
def login(
    credenciales: UsuarioLogin,
    servicio: UsuarioServicio = Depends(obtener_servicio_usuario),
):
    """
    Verifica email y contraseña.
    """
    if not servicio.verificar_contraseña(credenciales.email, credenciales.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Obtener usuario para retornar información útil
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

@router.get(
    "/{usuario_id}",
    response_model=Usuario,
    summary="Obtener un usuario por ID",
)
def obtener_usuario(
    usuario_id: int,
    servicio: UsuarioServicio = Depends(obtener_servicio_usuario),
):
    """
    Retorna los detalles de un usuario específico por su ID.
    """
    usuario = servicio.obtener_usuario(usuario_id)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id={usuario_id} no encontrado",
        )
    return usuario


@router.put(
    "/{usuario_id}",
    response_model=Usuario,
    summary="Actualizar completamente un usuario (Reemplazo total)",
)
def actualizar_usuario(
    usuario_id: int,
    datos_usuario: Usuario, # El cuerpo DEBE contener todos los campos
    servicio: UsuarioServicio = Depends(obtener_servicio_usuario),
):
    """
    Actualiza **todos** los campos de un usuario existente.
    """
    try:
        # El servicio ya maneja la validación y el error 404
        return servicio.actualizar_usuario(usuario_id, datos_usuario)
    except ValueError as e:
        detail = str(e)
        if f"id={usuario_id} no existe" in detail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        # Errores de validación como email duplicado o rol inválido
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


@router.patch(
    "/{usuario_id}",
    response_model=Usuario,
    summary="Actualizar parcialmente un usuario",
)
def actualizar_parcialmente_usuario(
    usuario_id: int,
    datos_parciales: UsuarioActualizarParcial, # Usa el esquema opcional
    servicio: UsuarioServicio = Depends(obtener_servicio_usuario),
):
    """
    Actualiza **parcialmente** (sólo los campos provistos) un usuario existente.
    """
    # Convierte Pydantic a diccionario, omitiendo los campos que NO fueron enviados.
    data_dict = datos_parciales.model_dump(exclude_unset=True) 

    if not data_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se debe proporcionar al menos un campo para actualizar",
        )

    try:
        # El servicio (actualizar_usuario) usa el diccionario para hacer el merge.
        return servicio.actualizar_usuario(usuario_id, data_dict)
    except ValueError as e:
        detail = str(e)
        if f"id={usuario_id} no existe" in detail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        # Errores de validación (ej. email duplicado)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

@router.patch(
    "/{usuario_id}/password",
    summary="Actualizar contraseña de un usuario",
    status_code=status.HTTP_200_OK,
)
def cambiar_password(
    usuario_id: int,
    datos: UsuarioCambiarPassword,
    servicio: UsuarioServicio = Depends(obtener_servicio_usuario),
):
    """
    Actualiza la contraseña de un usuario específico.
    """
    try:
        usuario_actualizado = servicio.actualizar_contraseña(usuario_id, datos.nueva_password)
        return {"mensaje": f"Contraseña de usuario {usuario_id} actualizada correctamente"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar contraseña: {e}")
        
@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un usuario",
)
def eliminar_usuario(
    usuario_id: int,
    servicio: UsuarioServicio = Depends(obtener_servicio_usuario),
):
    """
    Elimina un usuario por su ID.
    """
    # En un sistema real, primero verificarías si el usuario existe para devolver 404, 
    # pero el DAO simplemente ejecuta DELETE. Lo dejamos así por simplicidad.
    servicio.eliminar_usuario(usuario_id)
    return
