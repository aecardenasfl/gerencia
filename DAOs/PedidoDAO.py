#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
DAO para `Pedido` y `detalle_pedidos`.

Refactorado para eliminar lógica de negocio: este DAO ahora contiene SOLO operaciones
CRUD y consultas directas a la base de datos.
Toda lógica de negocio (validación de stock, cálculo de totales, etc.) debe
vivir en PedidoManager.
"""
from typing import Optional, List
from decimal import Decimal
from psycopg2.extras import RealDictCursor

from Modelo.Pedido import Pedido, DetallePedido
from DAOs.DB import get_conn

# Bandera para inicialización de tablas
_TABLAS_PEDIDO_CREADAS = False


class PedidoDAO:
    def __init__(self):
        self._ensure_tables()

    # ----------------------------
    # Inicialización de tablas
    # ----------------------------
    def _ensure_tables(self) -> None:
        global _TABLAS_PEDIDO_CREADAS
        if _TABLAS_PEDIDO_CREADAS:
            return

        with get_conn() as conn:
            with conn.cursor() as cur:
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
                _TABLAS_PEDIDO_CREADAS = True

    # ----------------------------
    # Crear pedido (SQL puro)
    # ----------------------------
    def create(self, pedido: Pedido) -> Pedido:
        """Inserta un pedido y sus detalles.
        Asume que `pedido` ya está validado y que los totales ya están calculados
        por PedidoManager.
        """
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Insertar pedido
                cur.execute(
                    "INSERT INTO pedidos (usuario_id, estado, total) VALUES (%s, %s, %s) RETURNING id",
                    (pedido.usuario_id, pedido.estado, Decimal(str(pedido.total)))
                )
                pedido_id = cur.fetchone()[0]
                pedido.id = pedido_id

                # Insertar items
                for it in pedido.items:
                    cur.execute(
                        """
                        INSERT INTO detalle_pedidos
                        (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                        VALUES (%s, %s, %s, %s, %s) RETURNING id
                        """,
                        (
                            pedido_id,
                            it.producto_id,
                            it.cantidad,
                            Decimal(str(it.precio_unitario)),
                            Decimal(str(it.subtotal))
                        )
                    )
                    it.pedido_id = pedido_id

                conn.commit()
                return pedido

    # ----------------------------
    # Obtener pedido por ID
    # ----------------------------
    def get_by_id(self, pedido_id: int) -> Optional[Pedido]:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM pedidos WHERE id = %s", (pedido_id,))
                p_row = cur.fetchone()
                if not p_row:
                    return None

                cur.execute(
                    "SELECT * FROM detalle_pedidos WHERE pedido_id = %s ORDER BY id",
                    (pedido_id,)
                )
                rows = cur.fetchall()

                items: List[DetallePedido] = []
                for r in rows:
                    items.append(
                        DetallePedido(
                            producto_id=r['producto_id'],
                            cantidad=r['cantidad'],
                            precio_unitario=float(r['precio_unitario']),
                            subtotal=float(r['subtotal']),
                            pedido_id=r['pedido_id'],
                        )
                    )

                return Pedido(
                    id=p_row['id'],
                    usuario_id=p_row['usuario_id'],
                    estado=p_row['estado'],
                    total=float(p_row['total']),
                    items=items
                )

    # ----------------------------
    # Actualizar estado (sin lógica)
    # ----------------------------
    def update_estado(self, pedido_id: int, nuevo_estado: str) -> Optional[int]:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE pedidos SET estado = %s WHERE id = %s RETURNING id",
                    (nuevo_estado, pedido_id)
                )
                row = cur.fetchone()
                conn.commit()
                return row[0] if row else None

    # ----------------------------
    # Consulta: pedidos por usuario
    # ----------------------------
    def get_by_usuario(self, usuario_id: int) -> List[Pedido]:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM pedidos WHERE usuario_id = %s ORDER BY id",
                    (usuario_id,)
                )
                pedidos_raw = cur.fetchall()

                pedidos: List[Pedido] = []

                for p in pedidos_raw:
                    pedido_id = p['id']

                    cur.execute(
                        "SELECT * FROM detalle_pedidos WHERE pedido_id = %s ORDER BY id",
                        (pedido_id,)
                    )
                    detalles_raw = cur.fetchall()

                    items = [
                        DetallePedido(
                            producto_id=d['producto_id'],
                            cantidad=d['cantidad'],
                            precio_unitario=float(d['precio_unitario']),
                            subtotal=float(d['subtotal']),
                            pedido_id=d['pedido_id'],
                        ) for d in detalles_raw
                    ]

                    pedidos.append(
                        Pedido(
                            id=pedido_id,
                            usuario_id=p['usuario_id'],
                            estado=p['estado'],
                            total=float(p['total']),
                            items=items
                        )
                    )

                return pedidos