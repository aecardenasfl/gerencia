#!/usr/bin/python
# -*- coding: utf-8 -*-
"""DAO para `Pedido` y `detalle_pedidos`.

Incluye lógica de inicialización segura para crear las tablas una sola vez.
"""
from typing import Optional, List
from decimal import Decimal

from psycopg2.extras import RealDictCursor

from Modelo.Pedido import Pedido, DetallePedido
from Modelo.Producto import Producto
from DAOs.DB import get_conn


# Bandera de control global para asegurar que las tablas solo se creen una vez
_TABLAS_PEDIDO_CREADAS = False 


class PedidoDAO:
    
    # Nuevo constructor para activar la inicialización
    def __init__(self):
        # Llama a la inicialización de las tablas al instanciarse
        self.create_table_if_not_exists() 

    def create_table_if_not_exists(self) -> None:
        """Crea las tablas 'pedidos' y 'detalle_pedidos' si no existen. Solo se ejecuta una vez."""
        global _TABLAS_PEDIDO_CREADAS
        
        # Si ya se ejecutó la creación exitosamente, salimos inmediatamente.
        if _TABLAS_PEDIDO_CREADAS:
            return
            
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla PEDIDOS
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS pedidos (
                        id SERIAL PRIMARY KEY,
                        usuario_id INTEGER,
                        estado TEXT NOT NULL,
                        total NUMERIC DEFAULT 0
                    )
                    """
                )
                # Crear tabla DETALLE_PEDIDOS
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS detalle_pedidos (
                        id SERIAL PRIMARY KEY,
                        pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
                        producto_id INTEGER NOT NULL,
                        cantidad INTEGER NOT NULL,
                        precio_unitario NUMERIC NOT NULL,
                        subtotal NUMERIC NOT NULL
                    )
                    """
                )
                conn.commit()
                # Marcar la bandera como True solo si la operación fue exitosa.
                _TABLAS_PEDIDO_CREADAS = True
                
    def create(self, pedido: Pedido) -> Pedido:
        """Crea un pedido con sus líneas de forma transaccional."""
        # ... (código existente de create) ...
        if not pedido.items:
            raise ValueError("El pedido debe contener al menos un item")

        with get_conn() as conn:
            cur = conn.cursor()
            try:
                total = Decimal('0')
                # Primero, validar existencias y poblar precios
                for it in pedido.items:
                    cur.execute("SELECT cantidad, precio FROM productos WHERE id = %s FOR UPDATE", (it.producto_id,))
                    row = cur.fetchone()
                    if not row:
                        raise ValueError(f"Producto id={it.producto_id} no existe")
                    available = int(row[0])
                    current_price = Decimal(row[1] or 0)
                    if it.cantidad <= 0:
                        raise ValueError("La cantidad debe ser positiva para cada item")
                    if available < it.cantidad:
                        raise ValueError(f"Stock insuficiente para producto id={it.producto_id}")
                    if it.precio_unitario is None:
                        it.precio_unitario = float(current_price)
                    subtotal = Decimal(str(it.precio_unitario)) * Decimal(it.cantidad)
                    total += subtotal

                # Insertar pedido
                cur.execute(
                    "INSERT INTO pedidos (usuario_id, estado, total) VALUES (%s, %s, %s) RETURNING id",
                    (pedido.usuario_id, pedido.estado, total),
                )
                pedido_id = cur.fetchone()[0]
                pedido.id = pedido_id

                # Insertar detalle_pedidos y ajustar stock
                for it in pedido.items:
                    subtotal = Decimal(str(it.precio_unitario)) * Decimal(it.cantidad)
                    cur.execute(
                        "INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                        (pedido_id, it.producto_id, it.cantidad, Decimal(str(it.precio_unitario)), subtotal),
                    )
                    # opcional: obtener id_detalle = cur.fetchone()[0]
                    # actualizar stock
                    cur.execute(
                        "UPDATE productos SET cantidad = cantidad - %s WHERE id = %s",
                        (it.cantidad, it.producto_id),
                    )
                    it.pedido_id = pedido_id

                # Actualizar total en pedidos (por si hubo redondeos)
                cur.execute("UPDATE pedidos SET total = %s WHERE id = %s", (total, pedido_id))
                conn.commit()
                pedido.total = float(total)
                return pedido
            except Exception:
                conn.rollback()
                raise

    def get_by_id(self, pedido_id: int) -> Optional[Pedido]:
        # ... (código existente) ...
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM pedidos WHERE id = %s", (pedido_id,))
                p_row = cur.fetchone()
                if not p_row:
                    return None
                cur.execute("SELECT * FROM detalle_pedidos WHERE pedido_id = %s ORDER BY id", (pedido_id,))
                lines = cur.fetchall()
                items: List[DetallePedido] = []
                for r in lines:
                    items.append(
                        DetallePedido(
                            producto_id=r.get('producto_id'),
                            cantidad=r.get('cantidad'),
                            precio_unitario=float(r.get('precio_unitario') or 0),
                            pedido_id=r.get('pedido_id'),
                        )
                    )
                pedido = Pedido(
                    id=p_row.get('id'),
                    usuario_id=p_row.get('usuario_id'),
                    estado=p_row.get('estado'),
                    items=items,
                    total=float(p_row.get('total') or 0),
                )
                return pedido
            
    def update_estado(self, pedido_id: int, nuevo_estado: str) -> Optional[Pedido]:
        # ... (código existente) ...
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE pedidos SET estado = %s WHERE id = %s RETURNING id",
                    (nuevo_estado, pedido_id)
                )
                row = cur.fetchone()
                conn.commit()
                if not row:
                    return None
            
            # Reutiliza el método get_by_id para obtener el objeto completo
            return self.get_by_id(pedido_id)