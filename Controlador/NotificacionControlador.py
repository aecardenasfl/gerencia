#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Controlador (Router) de FastAPI para operaciones sobre Notificacion."""

from typing import List, Optional, Generator
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from Modelo.Notificacion import Notificacion
from Servicios.NotificacionServicio import NotificacionServicio
from DAOs.DB import get_session  

# -------------------------------
# Esquemas Pydantic
# -------------------------------
class NotificacionRespuesta(BaseModel):
    id: int
    tipo: str
    mensaje: str
    producto_id: Optional[int]
    destinatario_id: Optional[int]
    leida: bool
    nivel: str

    model_config = {
        "from_attributes": True
    }

# -------------------------------
# Router
# -------------------------------
router = APIRouter(
    prefix="/notificaciones",
    tags=["notificaciones"],
)

# -------------------------------
# Dependencia: Servicio
# -------------------------------
def obtener_servicio_notificacion() -> Generator[NotificacionServicio, None, None]:
    """
    Adaptador: si get_session() devuelve un contextmanager (GeneratorContextManager),
    lo abrimos con __enter__() y lo cerramos con __exit__() para obtener la Session real.
    """
    cm = get_session()           # esto devuelve GeneratorContextManager
    db = cm.__enter__()          # abrimos el context manager -> Session real
    try:
        yield NotificacionServicio(db)
    finally:
        # Cerrar correctamente el context manager (evita fugas de conexión)
        cm.__exit__(None, None, None)
# -------------------------------
# Endpoints
# -------------------------------

@router.get(
    "/usuario/{usuario_id}",
    response_model=List[NotificacionRespuesta],
    summary="Listar notificaciones de un usuario",
)
def listar_notificaciones_por_usuario(
    usuario_id: int,
    solo_no_leidas: bool = False,
    servicio: NotificacionServicio = Depends(obtener_servicio_notificacion),
):
    return servicio.listar_por_usuario(usuario_id, solo_no_leidas)


@router.patch(
    "/{notificacion_id}/leer",
    status_code=status.HTTP_200_OK,
    summary="Marcar una notificación como leída",
)
def marcar_como_leida(
    notificacion_id: int,
    servicio: NotificacionServicio = Depends(obtener_servicio_notificacion),
):
    if servicio.marcar_como_leida(notificacion_id):
        return {"mensaje": f"Notificación {notificacion_id} marcada como leída."}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Notificación con id={notificacion_id} no encontrada."
    )


@router.patch(
    "/usuario/{usuario_id}/leer_todas",
    status_code=status.HTTP_200_OK,
    summary="Marcar todas las notificaciones de un usuario como leídas",
)
def marcar_todas_como_leidas(
    usuario_id: int,
    servicio: NotificacionServicio = Depends(obtener_servicio_notificacion),
):
    cantidad = servicio.marcar_todas_como_leidas(usuario_id)
    return {"mensaje": f"{cantidad} notificaciones marcadas como leídas."}


@router.delete(
    "/usuario/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar todas las notificaciones de un usuario",
)
def eliminar_notificaciones_por_usuario(
    usuario_id: int,
    servicio: NotificacionServicio = Depends(obtener_servicio_notificacion),
):
    servicio.eliminar_por_usuario(usuario_id)
    return


@router.delete(
    "/{notificacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una notificación por ID",
)
def eliminar_notificacion(
    notificacion_id: int,
    servicio: NotificacionServicio = Depends(obtener_servicio_notificacion),
):
    if not servicio.eliminar_por_id(notificacion_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notificación con id={notificacion_id} no encontrada."
        )
    return
