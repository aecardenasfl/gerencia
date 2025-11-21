#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from Managers.PedidoManager import PedidoManager

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


def obtener_servicio_pedido() -> PedidoManager:
    return PedidoManager()


@router.get("/", response_model=List[Any])
def listar_pedidos(manager: PedidoManager = Depends(obtener_servicio_pedido)):
    try:
        return manager.list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Any, status_code=status.HTTP_201_CREATED)
def crear_pedido(payload: Dict, manager: PedidoManager = Depends(obtener_servicio_pedido)):
    try:
        return manager.create(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pedido_id}", response_model=Any)
def obtener_pedido(pedido_id: int, manager: PedidoManager = Depends(obtener_servicio_pedido)):
    try:
        p = manager.get(pedido_id)
        if not p:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return p
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{pedido_id}", response_model=Any)
def actualizar_pedido(pedido_id: int, payload: Dict, manager: PedidoManager = Depends(obtener_servicio_pedido)):
    try:
        return manager.update(pedido_id, payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pedido(pedido_id: int, manager: PedidoManager = Depends(obtener_servicio_pedido)):
    try:
        manager.delete(pedido_id)
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))