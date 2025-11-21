#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import List, Optional, Union

from Modelo.Producto import Producto
from DAOs.ProductoDAO import ProductoDAO


class ProductoServicio:
    """Servicio de negocio para operaciones sobre `Producto`.

    Mantiene validaciones simples y orquesta llamadas al DAO.
    """

    def __init__(self, dao: Optional[ProductoDAO] = None):
        self.dao = dao or ProductoDAO()

    def _validate_producto(self, p: Producto) -> None:
        if not p.nombre or not p.nombre.strip():
            raise ValueError("'nombre' es requerido y no puede estar vacío")
        try:
            precio = float(p.precio)
        except Exception:
            raise ValueError("'precio' debe ser numérico")
        if precio < 0:
            raise ValueError("'precio' no puede ser negativo")
        try:
            cantidad = int(p.cantidad)
        except Exception:
            raise ValueError("'cantidad' debe ser un entero")
        if cantidad < 0:
            raise ValueError("'cantidad' no puede ser negativa")

    def create_product(self, data: Union[Producto, dict]) -> Producto:
        p = data if isinstance(data, Producto) else Producto(**data)
        self._validate_producto(p)
        return self.dao.create(p)

    def get_product(self, producto_id: int) -> Optional[Producto]:
        return self.dao.get_by_id(producto_id)

    def list_products(self) -> List[Producto]:
        return self.dao.list_all()

    def update_product(self, producto_id: int, data: Union[Producto, dict]) -> Producto:
        existing = self.dao.get_by_id(producto_id)
        if existing is None:
            raise ValueError(f"Producto con id={producto_id} no existe")
        # Prepare updated object
        if isinstance(data, Producto):
            updated = data
            updated.id = producto_id
        else:
            # merge fields with existing
            attrs = {
                'id': producto_id,
                'nombre': data.get('nombre', existing.nombre),
                'descripcion': data.get('descripcion', existing.descripcion),
                'precio': data.get('precio', existing.precio),
                'cantidad': data.get('cantidad', existing.cantidad),
                'codigo': data.get('codigo', existing.codigo),
                'activo': data.get('activo', existing.activo),
            }
            updated = Producto(**attrs)
        self._validate_producto(updated)
        return self.dao.update(updated)

    def delete_product(self, producto_id: int) -> None:
        # Let DAO handle deletion; optionally you can check existence first
        self.dao.delete(producto_id)

    def adjust_stock(self, producto_id: int, delta: int) -> int:
        """Ajusta el stock y devuelve el nuevo valor.

        Lanza ValueError si el producto no existe o si la operación dejaría stock negativo.
        """
        if not isinstance(delta, int):
            raise ValueError("'delta' debe ser un entero")
        # If delta is negative, ensure enough stock
        if delta < 0:
            prod = self.dao.get_by_id(producto_id)
            if prod is None:
                raise ValueError(f"Producto con id={producto_id} no existe")
            if prod.cantidad + delta < 0:
                raise ValueError("Stock insuficiente para la operación solicitada")
        new_qty = self.dao.adjust_stock(producto_id, delta)
        if new_qty is None:
            raise ValueError(f"Producto con id={producto_id} no existe")
        return new_qty


__all__ = ["ProductoService"]