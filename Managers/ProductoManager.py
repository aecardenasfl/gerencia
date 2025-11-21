#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Optional, List, Union

from Modelo.Producto import Producto
from Servicios.ProductoServicio import ProductoServicio


class ProductoManager:
    """Manager que expone operaciones para productos delegando en ProductoServicio."""

    def __init__(self, servicio: Optional[ProductoServicio] = None):
        self.servicio = servicio or ProductoServicio()

    def ensure_table(self) -> None:
        self.servicio.dao.create_table_if_not_exists()

    def create(self, data: Union[Producto, dict]) -> Producto:
        return self.servicio.create_product(data)

    def get(self, producto_id: int) -> Optional[Producto]:
        return self.servicio.get_product(producto_id)

    def list(self) -> List[Producto]:
        return self.servicio.list_products()

    def update(self, producto_id: int, data: Union[Producto, dict]) -> Producto:
        return self.servicio.update_product(producto_id, data)

    def delete(self, producto_id: int) -> None:
        self.servicio.delete_product(producto_id)

    def adjust_stock(self, producto_id: int, delta: int) -> int:
        return self.servicio.adjust_stock(producto_id, delta)