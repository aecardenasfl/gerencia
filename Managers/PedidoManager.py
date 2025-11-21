#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Optional, Union

from Modelo.Pedido import Pedido
from Servicios.PedidoServicio import PedidoServicio


class PedidoManager:
    """Manager para pedidos que delega en PedidoServicio."""

    def __init__(self, servicio: Optional[PedidoServicio] = None):
        self.servicio = servicio or PedidoServicio()

    def ensure_tables(self) -> None:
        self.servicio.ensure_tables()

    def create(self, data: Union[Pedido, dict]) -> Pedido:
        return self.servicio.crear_pedido(data)

    def get(self, pedido_id: int) -> Optional[Pedido]:
        return self.servicio.obtener_pedido(pedido_id)