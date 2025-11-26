#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import List, Optional, Union

from Modelo.Producto import Producto
from DAOs.ProductoDAO import ProductoDAO


class ProductoServicio:
    """Servicio de negocio para operaciones sobre `Producto`.

    Contiene validaciones y orquesta las llamadas al DAO.
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

    # -----------------------------------------------------
    # Crear
    # -----------------------------------------------------
    def crear_producto(self, data: Union[Producto, dict]) -> Producto:
        p = data if isinstance(data, Producto) else Producto(**data)
        self._validate_producto(p)
        return self.dao.create(p)

    # -----------------------------------------------------
    # Consultar
    # -----------------------------------------------------
    def obtener_producto(self, producto_id: int) -> Optional[Producto]:
        return self.dao.get_by_id(producto_id)

    def listar_productos(self) -> List[Producto]:
        return self.dao.list_all()

    # -----------------------------------------------------
    # Actualizar
    # -----------------------------------------------------
    def actualizar_producto(self, producto_id: int, data: Union[Producto, dict]) -> Producto:
        existing = self.dao.get_by_id(producto_id)
        if existing is None:
            raise ValueError(f"Producto con id={producto_id} no existe")

        if isinstance(data, Producto):
            updated = data
            updated.id = producto_id
        else:
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

    # -----------------------------------------------------
    # Eliminar
    # -----------------------------------------------------
    def eliminar_producto(self, producto_id: int) -> None:
        self.dao.delete(producto_id)

    # -----------------------------------------------------
    # Stock
    # -----------------------------------------------------
    def ajustar_stock(self, producto_id: int, delta: int) -> int:
        if not isinstance(delta, int):
            raise ValueError("'delta' debe ser un entero")

        if delta < 0:
            prod = self.dao.get_by_id(producto_id)
            if prod is None:
                raise ValueError(f"Producto con id={producto_id} no existe")
            if prod.cantidad + delta < 0:
                raise ValueError("Stock insuficiente")

        new_qty = self.dao.adjust_stock(producto_id, delta)
        if new_qty is None:
            raise ValueError(f"Producto con id={producto_id} no existe")

        return new_qty
