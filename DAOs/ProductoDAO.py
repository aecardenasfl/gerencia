#!/usr/bin/python
# -*- coding: utf-8 -*-
# DAOs/ProductoDAO.py

from typing import Optional, List
from decimal import Decimal

from psycopg2.extras import RealDictCursor

from Modelo.Producto import Producto
from DAOs.DB import get_conn 

# Control para evitar crear la tabla más de una vez
_TABLA_PRODUCTO_CREADA = False


class ProductoDAO:

    def __init__(self):
        self.create_table_if_not_exists()

    # ---------------------------------------------------------
    # Crear tabla si no existe (solo una vez)
    # ---------------------------------------------------------
    def create_table_if_not_exists(self) -> None:
        global _TABLA_PRODUCTO_CREADA
        
        if _TABLA_PRODUCTO_CREADA:
            return
            
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS productos (
                        id SERIAL PRIMARY KEY,
                        nombre TEXT NOT NULL,
                        descripcion TEXT DEFAULT '',
                        precio NUMERIC DEFAULT 0,
                        cantidad INTEGER DEFAULT 0,
                        codigo TEXT,
                        activo BOOLEAN DEFAULT true
                    )
                    """
                )
                conn.commit()
                _TABLA_PRODUCTO_CREADA = True

    # ---------------------------------------------------------
    # CRUD
    # ---------------------------------------------------------
    def create(self, p: Producto) -> Producto:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO productos (nombre, descripcion, precio, cantidad, codigo, activo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (p.nombre, p.descripcion, Decimal(p.precio), p.cantidad, p.codigo, p.activo),
                )
                new_id = cur.fetchone()[0]
                conn.commit()
                p.id = new_id
                return p

    def get_by_id(self, producto_id: int) -> Optional[Producto]:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM productos WHERE id = %s", (producto_id,))
                row = cur.fetchone()
                if not row:
                    return None
                return self._row_to_producto(row)

    def list_all(self) -> List[Producto]:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM productos ORDER BY id")
                rows = cur.fetchall()
                return [self._row_to_producto(r) for r in rows]

    def update(self, p: Producto) -> Producto:
        if p.id is None:
            raise ValueError("Producto.id es requerido para actualizar")
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE productos
                    SET nombre = %s, descripcion = %s, precio = %s, cantidad = %s, codigo = %s, activo = %s
                    WHERE id = %s
                    """,
                    (p.nombre, p.descripcion, Decimal(p.precio), p.cantidad,
                     p.codigo, p.activo, p.id),
                )
                conn.commit()
                return p

    def delete(self, producto_id: int) -> None:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
                conn.commit()

    # ---------------------------------------------------------
    # Utilidades para PedidoServicio
    # ---------------------------------------------------------
    def exists(self, producto_id: int) -> bool:
        """Retorna True si el producto existe."""
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM productos WHERE id = %s", (producto_id,))
                return cur.fetchone() is not None

    def get_stock(self, producto_id: int) -> Optional[int]:
        """Retorna el stock actual, o None si el producto no existe."""
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT cantidad FROM productos WHERE id = %s", (producto_id,))
                row = cur.fetchone()
                return row[0] if row else None

    def adjust_stock(self, producto_id: int, delta: int) -> Optional[int]:
        """Modifica el stock sumando delta (positivo o negativo) y retorna el nuevo stock."""
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE productos
                    SET cantidad = cantidad + %s
                    WHERE id = %s
                    RETURNING cantidad
                    """,
                    (delta, producto_id)
                )
                row = cur.fetchone()
                conn.commit()
                return row[0] if row else None

    # ---------------------------------------------------------
    # Conversión
    # ---------------------------------------------------------
    def _row_to_producto(self, row: dict) -> Producto:
        precio = float(row.get('precio') or 0.0)
        return Producto(
            id=row.get('id'),
            nombre=row.get('nombre') or '',
            descripcion=row.get('descripcion') or '',
            precio=precio,
            cantidad=row.get('cantidad') or 0,
            codigo=row.get('codigo'),
            activo=row.get('activo') if 'activo' in row else True,
        )
