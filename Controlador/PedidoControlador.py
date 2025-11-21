#!/usr/bin/python
# -*- coding: utf-8 -*-

from fastapi import Depends
from Managers.PedidoManager import PedidoManager

class PedidoControlador:
    pass

def obtener_servicio_pedido() -> PedidoManager:
    # Antes devolvía PedidoServicio(); ahora devolvemos el manager
    return PedidoManager()

# Ejemplo de uso en un endpoint:
# @router.post("/", response_model=Pedido)
# def crear_pedido(payload: PedidoCreate, manager: PedidoManager = Depends(obtener_servicio_pedido)):
#     return manager.create(payload)