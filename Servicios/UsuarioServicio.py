#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Servicio de negocios para `Usuario`.

Valida datos del usuario y orquesta llamadas al DAO. No maneja
credenciales; el modelo de dominio se mantiene minimalista según lo
solicitado.
"""
from typing import Optional, Union

from Modelo.Usuario import Usuario
from DAOs.UsuarioDAO import UsuarioDAO


class UsuarioServicio:
    def __init__(self, dao: Optional[UsuarioDAO] = None):
        self.dao = dao or UsuarioDAO()

    def ensure_table(self) -> None:
        self.dao.create_table_if_not_exists()

    def _validate_usuario(self, u: Usuario) -> None:
        if not u.nombre or not u.nombre.strip():
            raise ValueError("'nombre' es requerido")
        if not u.email or '@' not in u.email:
            raise ValueError("'email' inválido")
        if u.rol not in ('user', 'admin'):
            raise ValueError("'rol' inválido")

    def crear_usuario(self, data: Union[Usuario, dict]) -> Usuario:
        u = data if isinstance(data, Usuario) else Usuario(**data)
        self._validate_usuario(u)

        # verificar unicidad de email
        existing = self.dao.get_by_email(u.email)
        if existing is not None:
            raise ValueError("Ya existe un usuario con ese email")

        creado = self.dao.create(u)
        return creado

    def obtener_usuario(self, usuario_id: int) -> Optional[Usuario]:
        return self.dao.get_by_id(usuario_id)

    def listar_usuarios(self):
        return self.dao.list_all()

    def actualizar_usuario(self, usuario_id: int, data: Union[Usuario, dict]) -> Usuario:
        existing = self.dao.get_by_id(usuario_id)
        if existing is None:
            raise ValueError(f"Usuario id={usuario_id} no existe")

        if isinstance(data, Usuario):
            updated = data
            updated.id = usuario_id
        else:
            updated = Usuario(
                id=usuario_id,
                nombre=data.get('nombre', existing.nombre),
                email=data.get('email', existing.email),
                rol=data.get('rol', existing.rol),
                activo=data.get('activo', existing.activo),
            )

        self._validate_usuario(updated)

        return self.dao.update(updated)

    def eliminar_usuario(self, usuario_id: int) -> None:
        self.dao.delete(usuario_id)



