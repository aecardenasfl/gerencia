#!/usr/bin/python
# -*- coding: utf-8 -*-
"""DAO para la entidad `Usuario`.

Provee operaciones CRUD usando el pool definido en `DAOs.DB`.
El DTO `Modelo.Usuario.Usuario` se mantiene minimalista y no contiene
credenciales de acceso.
"""
from typing import Optional, List
from psycopg2.extras import RealDictCursor

from Modelo.Usuario import Usuario
from DAOs.DB import get_conn


class UsuarioDAO:
    def create_table_if_not_exists(self) -> None:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id SERIAL PRIMARY KEY,
                        nombre TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        rol TEXT DEFAULT 'user',
                        activo BOOLEAN DEFAULT true
                    )
                    """
                )
                conn.commit()

    def create(self, u: Usuario) -> Usuario:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO usuarios (nombre, email, rol, activo)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (u.nombre, u.email, u.rol, u.activo),
                )
                new_id = cur.fetchone()[0]
                conn.commit()
                u.id = new_id
                return u

    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id, nombre, email, rol, activo FROM usuarios WHERE id = %s", (usuario_id,))
                row = cur.fetchone()
                if not row:
                    return None
                return self._row_to_usuario(row)

    def get_by_email(self, email: str) -> Optional[Usuario]:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id, nombre, email, rol, activo FROM usuarios WHERE email = %s", (email,))
                row = cur.fetchone()
                if not row:
                    return None
                return self._row_to_usuario(row)

    def list_all(self) -> List[Usuario]:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id, nombre, email, rol, activo FROM usuarios ORDER BY id")
                rows = cur.fetchall()
                return [self._row_to_usuario(r) for r in rows]

    def update(self, u: Usuario) -> Usuario:
        if u.id is None:
            raise ValueError("Usuario.id es requerido para actualizar")
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE usuarios
                    SET nombre = %s, email = %s, rol = %s, activo = %s
                    WHERE id = %s
                    """,
                    (u.nombre, u.email, u.rol, u.activo, u.id),
                )
                conn.commit()
                return u

    def delete(self, usuario_id: int) -> None:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
                conn.commit()

    def _row_to_usuario(self, row: dict) -> Usuario:
        return Usuario(
            id=row.get('id'),
            nombre=row.get('nombre') or '',
            email=row.get('email') or '',
            rol=row.get('rol') or 'user',
            activo=row.get('activo') if 'activo' in row else True,
        )
