#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
DAO para la entidad `Usuario`.

Incluye lógica de inicialización segura para crear la tabla una sola vez.
"""

from typing import Optional, List
from psycopg2.extras import RealDictCursor
from Modelo.Usuario import Usuario
from DAOs.DB import get_conn

# Bandera de control global para asegurar que la tabla solo se cree una vez
_TABLA_USUARIO_CREADA = False


class UsuarioDAO:

    # Constructor que activa la inicialización
    def __init__(self):
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self) -> None:
        """Crea la tabla 'usuarios' si no existe. Solo se ejecuta una vez."""
        global _TABLA_USUARIO_CREADA

        if _TABLA_USUARIO_CREADA:
            return

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id SERIAL PRIMARY KEY,
                        nombre TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        rol TEXT DEFAULT 'user',
                        activo BOOLEAN DEFAULT true,
                        password_hash TEXT NOT NULL
                    )
                    """
                )
                conn.commit()
                _TABLA_USUARIO_CREADA = True

    def create(self, u: Usuario) -> Usuario:
        """Inserta un usuario. El password_hash debe venir creado desde el Servicio."""
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO usuarios (nombre, email, rol, activo, password_hash)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (u.nombre, u.email, u.rol, u.activo, u.password_hash),
                )
                new_id = cur.fetchone()[0]
                conn.commit()
                u.id = new_id
                return u

    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, nombre, email, rol, activo, password_hash
                    FROM usuarios WHERE id = %s
                    """,
                    (usuario_id,)
                )
                row = cur.fetchone()
                if not row:
                    return None
                return self._row_to_usuario(row)

    def get_by_email(self, email: str) -> Optional[Usuario]:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, nombre, email, rol, activo, password_hash
                    FROM usuarios WHERE email = %s
                    """,
                    (email,)
                )
                row = cur.fetchone()
                if not row:
                    return None
                return self._row_to_usuario(row)

    def list_all(self) -> List[Usuario]:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, nombre, email, rol, activo, password_hash
                    FROM usuarios ORDER BY id
                    """
                )
                rows = cur.fetchall()
                return [self._row_to_usuario(r) for r in rows]

    def update(self, u: Usuario) -> Usuario:
        if u.id is None:
            raise ValueError("Usuario.id es requerido para actualizar")

        campos = ["nombre = %s", "email = %s", "rol = %s", "activo = %s"]
        valores = [u.nombre, u.email, u.rol, u.activo]

        # Solo actualiza la contraseña si viene incluida
        if hasattr(u, "password_hash") and u.password_hash:
            campos.append("password_hash = %s")
            valores.append(u.password_hash)

        valores.append(u.id)

        query = f"""
            UPDATE usuarios
            SET {', '.join(campos)}
            WHERE id = %s
        """

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, valores)
                conn.commit()

        return u

    def delete(self, usuario_id: int) -> None:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
                conn.commit()

    def get_usuarios_por_rol(self, rol: str) -> List[Usuario]:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, nombre, email, rol, activo, password_hash
                    FROM usuarios WHERE rol = %s ORDER BY id
                    """,
                    (rol,)
                )
                rows = cur.fetchall()
                return [self._row_to_usuario(r) for r in rows]

    def list_activos(self) -> List[Usuario]:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, nombre, email, rol, activo, password_hash
                    FROM usuarios WHERE activo = TRUE ORDER BY id
                    """
                )
                rows = cur.fetchall()
                return [self._row_to_usuario(r) for r in rows]

    def _row_to_usuario(self, row: dict) -> Usuario:
        """Mapea un diccionario de postgres al modelo Usuario."""
        return Usuario(
            id=row.get("id"),
            nombre=row.get("nombre") or "",
            email=row.get("email") or "",
            rol=row.get("rol") or "user",
            activo=row.get("activo", True),
            password_hash=row.get("password_hash") or ""
        )
