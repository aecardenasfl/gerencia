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

import psycopg2
from psycopg2 import sql
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor


# Pool singleton y lock para seguridad en entornos con hilos
_pool: Optional[SimpleConnectionPool] = None
_lock = threading.Lock()
_schema: Optional[str] = None


def _create_pool(minconn: int = 1, maxconn: int = 5) -> SimpleConnectionPool:
    # Leer exclusivamente desde config/.env. No usar variables de entorno como fallback.
    env_path = Path(__file__).resolve().parents[1] / 'config' / '.env'
    if not env_path.exists():
        raise RuntimeError(
            f"Archivo de configuración requerido no encontrado: {env_path}. "
            "Crea `config/.env` con las credenciales de la base de datos."
        )

    cfg: dict = {}
    with env_path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k:
                cfg[k] = v

    # Si se define POSTGRES_DSN en el archivo de config, usarlo.
    dsn = cfg.get('POSTGRES_DSN')
    # establecer schema global si está presente en el archivo de config
    global _schema
    _schema = cfg.get('PGSCHEMA') or None

    if dsn:
        pool = SimpleConnectionPool(minconn, maxconn, dsn=dsn)
    else:
        # Requerir las claves necesarias en el archivo de config
        required = ('PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE')
        missing = [k for k in required if k not in cfg or not cfg[k]]
        if missing:
            raise RuntimeError(
                f"Faltan claves en {env_path}: {', '.join(missing)}. "
                "Asegúrate de que el archivo contenga PGHOST, PGPORT, PGUSER, PGPASSWORD y PGDATABASE."
            )

        params = {
            'host': cfg['PGHOST'],
            'port': int(cfg['PGPORT']),
            'user': cfg['PGUSER'],
            'password': cfg['PGPASSWORD'],
            'dbname': cfg['PGDATABASE'],
        }
        pool = SimpleConnectionPool(minconn, maxconn, **params)

    # Si se indicó un schema, crear el schema en la BD si no existe.
    if _schema:
        conn = pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {};").format(sql.Identifier(_schema)))
                conn.commit()
        except Exception:
            # Si no se puede crear el schema, devolver la conexión y re-raise
            pool.putconn(conn)
            raise
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
