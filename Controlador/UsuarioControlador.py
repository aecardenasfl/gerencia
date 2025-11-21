#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from Managers.UsuarioManager import UsuarioManager

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def obtener_servicio_usuario() -> UsuarioManager:
    # Antes devolvía UsuarioServicio(); ahora devolvemos el manager
    return UsuarioManager()


# Ejemplo de uso en un endpoint:
# @router.get("/", response_model=List[Usuario])
# def listar_usuarios(manager: UsuarioManager = Depends(obtener_servicio_usuario)):
#     return manager.list()

@router.get("/", response_model=List[Any])
def listar_usuarios(manager: UsuarioManager = Depends(obtener_servicio_usuario)):
    try:
        return manager.list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Any, status_code=status.HTTP_201_CREATED)
def crear_usuario(payload: Dict, manager: UsuarioManager = Depends(obtener_servicio_usuario)):
    try:
        return manager.create(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{usuario_id}", response_model=Any)
def obtener_usuario(usuario_id: int, manager: UsuarioManager = Depends(obtener_servicio_usuario)):
    try:
        u = manager.get(usuario_id)
        if not u:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return u
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{usuario_id}", response_model=Any)
def actualizar_usuario(usuario_id: int, payload: Dict, manager: UsuarioManager = Depends(obtener_servicio_usuario)):
    try:
        return manager.update(usuario_id, payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(usuario_id: int, manager: UsuarioManager = Depends(obtener_servicio_usuario)):
    try:
        manager.delete(usuario_id)
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class UsuarioControlador:
    pass