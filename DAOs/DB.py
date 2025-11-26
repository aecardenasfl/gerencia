#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Singleton de conexión a PostgreSQL.

Provee un pool global (creado una vez) y helpers context managers para
obtener conexiones y cursores. Lee configuración desde `POSTGRES_DSN`
o variables `PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE`.
"""
from __future__ import annotations

import os
from pathlib import Path
import threading
from contextlib import contextmanager
from typing import Optional
from config.config_loader import Config

import psycopg2
from psycopg2 import sql
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor


# Pool singleton y lock para seguridad en entornos con hilos
_pool: Optional[SimpleConnectionPool] = None
_lock = threading.Lock()
_schema: Optional[str] = None


def _create_pool(minconn: int = 1, maxconn: int = 5) -> SimpleConnectionPool:
    # Primero, intentamos DSN si está disponible
    dsn = Config.POSTGRES_DSN

    global _schema
    _schema = Config.PGSCHEMA or None

    if dsn:
        pool = SimpleConnectionPool(minconn, maxconn, dsn=dsn)
    else:
        required = (
            Config.PGHOST,
            Config.PGPORT,
            Config.PGUSER,
            Config.PGPASSWORD,
            Config.PGDATABASE,
        )

        if any(v is None for v in required):
            raise RuntimeError(
                "Faltan variables de entorno en config/.env para la conexión a PostgreSQL"
            )

        params = {
            'host': Config.PGHOST,
            'port': int(Config.PGPORT),
            'user': Config.PGUSER,
            'password': Config.PGPASSWORD,
            'dbname': Config.PGDATABASE,
        }
        pool = SimpleConnectionPool(minconn, maxconn, **params)

    # Crear schema si aplica
    if _schema:
        conn = pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL("CREATE SCHEMA IF NOT EXISTS {};")
                    .format(sql.Identifier(_schema))
                )
                conn.commit()
        finally:
            pool.putconn(conn)

    return pool


def get_pool(minconn: int = 1, maxconn: int = 5) -> SimpleConnectionPool:
    """Devuelve el pool singleton, creándolo si es necesario."""
    global _pool
    if _pool is None:
        with _lock:
            if _pool is None:
                _pool = _create_pool(minconn, maxconn)
    return _pool


def close_pool() -> None:
    """Cierra el pool y libera recursos."""
    global _pool
    with _lock:
        if _pool is not None:
            try:
                _pool.closeall()
            finally:
                _pool = None


@contextmanager
def get_conn():
    """Context manager que entrega una conexión y la devuelve al pool."""
    pool = get_pool()
    conn = pool.getconn()
    # Si se definió un schema en la configuración, ajustar el search_path
    if _schema:
        try:
            with conn.cursor() as cur:
                cur.execute(sql.SQL("SET search_path TO {}, public;").format(sql.Identifier(_schema)))
            # No es estrictamente necesario hacer commit para SET, pero no hace daño
            conn.commit()
        except Exception:
            pool.putconn(conn)
            raise
    try:
        yield conn
    finally:
        pool.putconn(conn)


@contextmanager
def get_cursor(dict_cursor: bool = False):
    """Context manager que entrega un cursor (opcionalmente dict-like).

    Uso:
        with get_cursor(True) as cur:
            cur.execute(...)  # devuelve diccionarios
    """
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor) if dict_cursor else conn.cursor()
        try:
            yield cur
        finally:
            try:
                cur.close()
            except Exception:
                pass
