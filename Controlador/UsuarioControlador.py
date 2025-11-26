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
    password: str = Field(..., description="Contraseña en texto plano")

class UsuarioCambiarPassword(BaseModel):
    nueva_password: str = Field(..., min_length=6, description="Nueva contraseña del usuario")

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

@router.post(
    "/",
    response_model=Usuario, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo usuario",
)
def crear_usuario(
    usuario: Usuario, # Usa tu dataclass para la entrada
    servicio: UsuarioServicio = Depends(obtener_servicio_usuario),
):
    """
    Crea un nuevo usuario en la base de datos.
    """
    try:
        usuario_creado = servicio.crear_usuario(usuario)
        return usuario_creado
    except ValueError as e:
        # Errores de validación (email ya existe, rol inválido, etc.)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear usuario: {e}")


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