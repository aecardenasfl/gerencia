#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Servicio para orquestar la creación y consulta de pedidos.

Se encarga de validar el pedido, rellenar precios unitarios si faltan
consultando `ProductoDAO`, y delega la persistencia al `PedidoDAO`.
La lógica de stock y transacciones se deja en el DAO para garantizar
atomicidad.
"""
from typing import Optional, Union

from Modelo.Pedido import Pedido, DetallePedido
from DAOs.PedidoDAO import PedidoDAO
from DAOs.ProductoDAO import ProductoDAO


class PedidoServicio:
    def __init__(self, pedido_dao: Optional[PedidoDAO] = None, producto_dao: Optional[ProductoDAO] = None):
        self.pedido_dao = pedido_dao or PedidoDAO()
        self.producto_dao = producto_dao or ProductoDAO()

    def ensure_tables(self) -> None:
        self.pedido_dao.create_table_if_not_exists()

    def crear_pedido(self, data: Union[Pedido, dict]) -> Pedido:
        """Valida y crea un pedido.

        - Acepta un `Pedido` o un `dict` compatible.
        - Rellena `precio_unitario` en cada `DetallePedido` consultando `ProductoDAO`
          cuando falte.
        - Llama a `PedidoDAO.create()` que maneja la transacción y ajuste de stock.
        """
        pedido = data if isinstance(data, Pedido) else Pedido(**data)

        if not pedido.items:
            raise ValueError("El pedido debe contener al menos un item")

        # Poblar precios unitarios faltantes consultando ProductoDAO
        for it in pedido.items:
            if it.precio_unitario is None:
                prod = self.producto_dao.get_by_id(it.producto_id)
                if prod is None:
                    raise ValueError(f"Producto id={it.producto_id} no existe")
                it.precio_unitario = float(prod.precio)
            if it.cantidad <= 0:
                raise ValueError("Cada item debe tener cantidad positiva")

        # Delegar a DAO la creación (que es transaccional)
        creado = self.pedido_dao.create(pedido)
        return creado

    def obtener_pedido(self, pedido_id: int) -> Optional[Pedido]:
        return self.pedido_dao.get_by_id(pedido_id)


__all__ = ["PedidoServicio"]
#!/usr/bin/python
# -*- coding: utf-8 -*-

class PedidoService:
    pass