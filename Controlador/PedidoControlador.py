#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Controlador (Router) de FastAPI para operaciones sobre Pedido.

Implementa la creación transaccional y la consulta.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

# Importar el modelo y el servicio (Asegúrate de que estas rutas sean correctas)
from Modelo.Pedido import Pedido, DetallePedido
from Servicios.PedidoServicio import PedidoServicio


# --- Esquemas de Datos para Solicitudes Específicas ---

# 1. Esquema para la Solicitud de Cambio de Estado (PATCH de negocio)
class SolicitudCambioEstado(BaseModel):
    estado: str = Field(..., description="Nuevo estado del pedido (e.g., 'confirmado', 'enviado')")


# --- Instancia del Router y Dependencia del Servicio ---

router = APIRouter(
    prefix="/pedidos",
    tags=["pedidos"],
)

# Dependencia para obtener la instancia del servicio
def obtener_servicio_pedido() -> PedidoServicio:
    """Retorna una instancia del servicio de pedido."""
    return PedidoServicio()


# --- Endpoints ---

@router.post(
    "/",
    response_model=Pedido, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo pedido (Transaccional)",
)
def crear_pedido(
    # FastAPI mapea el JSON de entrada a Pedido (incluyendo la lista de DetallePedido)
    pedido: Pedido, 
    servicio: PedidoServicio = Depends(obtener_servicio_pedido),
):
    """
    Crea un pedido, valida stock, ajusta precios unitarios si es necesario, 
    ajusta el stock de productos y guarda el pedido, todo de forma transaccional.
    """
    try:
        # El servicio maneja toda la lógica de validación y la llamada transaccional al DAO
        pedido_creado = servicio.crear_pedido(pedido)
        return pedido_creado
    except ValueError as e:
        # Errores de stock insuficiente, producto no existe, etc.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Cualquier otro error interno (conexión DB, rollback)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error transaccional al crear pedido: {e}")


@router.get(
    "/{pedido_id}",
    response_model=Pedido,
    summary="Obtener un pedido por ID",
)
def obtener_pedido(
    pedido_id: int,
    servicio: PedidoServicio = Depends(obtener_servicio_pedido),
):
    """
    Retorna un pedido específico, incluyendo sus líneas (DetallePedido).
    """
    pedido = servicio.obtener_pedido(pedido_id)
    if pedido is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido con id={pedido_id} no encontrado",
        )
    return pedido

@router.get(
    "/usuario/{usuario_id}",
    response_model=List[Pedido],
    summary="Listar pedidos por usuario",
)
def listar_pedidos_por_usuario(
    usuario_id: int,
    servicio: PedidoServicio = Depends(obtener_servicio_pedido),
):
    """
    Devuelve la lista de pedidos (con sus líneas) del usuario indicado.

    Ejemplo de uso:
        GET /pedidos/usuario/7
    """
    try:
        pedidos = servicio.listar_pedidos_usuario(usuario_id)
        return pedidos
    except ValueError as e:
        detail = str(e)
        if "no existe" in detail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# NOTA: La listado de todos los pedidos (GET /) se omite por la complejidad de 
# traer todos los detalles de todos los pedidos.

# --- Endpoint de Negocio: Actualización de Estado (PATCH) ---

@router.patch(
    "/{pedido_id}/estado",
    response_model=Pedido,
    summary="Actualizar el estado del pedido",
)
def cambiar_estado_pedido(
    pedido_id: int,
    solicitud: SolicitudCambioEstado,
    servicio: PedidoServicio = Depends(obtener_servicio_pedido),
):
    """
    Actualiza el campo 'estado' de un pedido.
    estados_validos = ["pendiente", "confirmado", "enviado", "cancelado"]

    """
    try:
        # Se asume que el servicio implementará un método cambiar_estado
        pedido_actualizado = servicio.cambiar_estado(pedido_id, solicitud.estado)
        return pedido_actualizado
    except ValueError as e:
        detail = str(e)
        if "no existe" in detail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)