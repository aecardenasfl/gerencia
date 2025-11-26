#!/usr/bin/python
# -*- coding: utf-8 -*-
"""DAO para la entidad `Notificacion`.

Incluye lógica de inicialización segura para crear la tabla una sola vez.
"""
from typing import Optional, List
from psycopg2.extras import RealDictCursor
from Modelo.Notificacion import Notificacion
from DAOs.DB import get_conn

_TABLA_NOTIFICACION_CREADA = False


class NotificacionDAO:

    def __init__(self):
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self) -> None:
        """Crea la tabla 'notificaciones' si no existe. Solo se ejecuta una vez."""
        global _TABLA_NOTIFICACION_CREADA
        if _TABLA_NOTIFICACION_CREADA:
            return

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notificaciones (
                        id SERIAL PRIMARY KEY,
                        tipo TEXT NOT NULL,
                        mensaje TEXT NOT NULL,
                        producto_id INTEGER,
                        destinatario_id INTEGER,
                        leida BOOLEAN DEFAULT FALSE,
                        nivel TEXT DEFAULT 'info',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                conn.commit()
                _TABLA_NOTIFICACION_CREADA = True

    def create(self, n: Notificacion) -> Notificacion:
        """Crea una nueva notificación en la DB y devuelve el objeto con ID asignado."""
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO notificaciones (tipo, mensaje, producto_id, destinatario_id, leida, nivel)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (n.tipo, n.mensaje, n.producto_id, n.destinatario_id, n.leida, n.nivel),
                )
                new_id = cur.fetchone()[0]
                conn.commit()
                n.id = new_id
                return n

    def get_by_id(self, notificacion_id: int) -> Optional[Notificacion]:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, tipo, mensaje, producto_id, destinatario_id, leida, nivel "
                    "FROM notificaciones WHERE id = %s", 
                    (notificacion_id,)
                )
                row = cur.fetchone()
                if not row:
                    return None
                return self._row_to_notificacion(row)

    def list_all(self) -> List[Notificacion]:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, tipo, mensaje, producto_id, destinatario_id, leida, nivel "
                    "FROM notificaciones ORDER BY id"
                )
                rows = cur.fetchall()
                return [self._row_to_notificacion(r) for r in rows]

    def update(self, n: Notificacion) -> Notificacion:
        if n.id is None:
            raise ValueError("Notificacion.id es requerido para actualizar")
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE notificaciones
                    SET tipo = %s, mensaje = %s, producto_id = %s, destinatario_id = %s,
                        leida = %s, nivel = %s
                    WHERE id = %s
                    """,
                    (n.tipo, n.mensaje, n.producto_id, n.destinatario_id, n.leida, n.nivel, n.id),
                )
                conn.commit()
                return n

    def delete(self, notificacion_id: int) -> None:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM notificaciones WHERE id = %s", (notificacion_id,))
                conn.commit()

    def _row_to_notificacion(self, row: dict) -> Notificacion:
        return Notificacion(
            id=row.get('id'),
            tipo=row.get('tipo') or "",
            mensaje=row.get('mensaje') or "",
            producto_id=row.get('producto_id'),
            destinatario_id=row.get('destinatario_id'),
            leida=row.get('leida', False),
            nivel=row.get('nivel', 'info')
        )
