#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Optional, Union, Any, List, Dict

from Modelo.Pedido import Pedido
from Servicios.PedidoServicio import PedidoServicio
from Managers.ProductoManager import ProductoManager


def _call_any(obj: Any, names: List[str], *args, **kwargs):
    for n in names:
        fn = getattr(obj, n, None)
        if callable(fn):
            return fn(*args, **kwargs)
    raise RuntimeError(f"Ningún método válido encontrado en {obj} de: {', '.join(names)}")


class PedidoManager:
    """Manager para pedidos: crea/obtiene/lista/actualiza/elimina y orquesta ajuste de stock."""

    def __init__(self, servicio: Optional[PedidoServicio] = None):
        self.servicio = servicio or PedidoServicio()
        self.producto_manager = ProductoManager()

    def ensure_tables(self) -> None:
        return _call_any(self.servicio, ["ensure_tables", "ensure_table", "crear_tablas", "create_tables"])

    def create(self, data: Union[Pedido, Dict]) -> Any:
        """
        data: dict con la estructura del pedido, idealmente incluye 'items': [{'producto_id': int, 'cantidad': int}, ...]
        El manager crea el pedido mediante el servicio y luego intenta ajustar stock para cada item.
        """
        payload = data if isinstance(data, dict) else data.__dict__
        # Crear pedido a través del servicio (nombre flexible)
        order = _call_any(self.servicio, ["crear_pedido", "create_order", "create"], payload)

        # Ajustar stock por cada item; si no hay items, se ignora
        items = payload.get("items") or []
        for it in items:
            try:
                pid = it.get("producto_id") or it.get("producto") or it.get("id")
                qty = it.get("cantidad") or it.get("qty") or it.get("cantidad_producto") or 0
                if pid is None:
                    continue
                # reducir stock en cantidad vendida (por eso -int(qty))
                self.producto_manager.adjust_stock(int(pid), -int(qty))
            except Exception as e:
                # no detener la creación por error de ajuste; loguear/propagar según prefieras
                print(f"Advertencia al ajustar stock para producto {it}: {e}")

        return order

    def get(self, pedido_id: int) -> Optional[Pedido]:
        return _call_any(self.servicio, ["obtener_pedido", "get_order", "get"], pedido_id)

    def list(self) -> List[Any]:
        return _call_any(self.servicio, ["listar_pedidos", "list_orders", "list"])

    def update(self, pedido_id: int, data: Union[Pedido, Dict]) -> Any:
        return _call_any(self.servicio, ["actualizar_pedido", "update_order", "update"], pedido_id, data)

    def delete(self, pedido_id: int) -> None:
        return _call_any(self.servicio, ["eliminar_pedido", "delete_order", "delete"], pedido_id)
