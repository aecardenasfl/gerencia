#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Servicio de negocios para `Usuario`.

Valida datos del usuario y orquesta llamadas al DAO. No maneja
credenciales; el modelo de dominio se mantiene minimalista según lo
solicitado.
"""
import bcrypt

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

    def crear_usuario(self, data: Union[Usuario, dict], password: str = None) -> Usuario:
        u = data if isinstance(data, Usuario) else Usuario(**data)
        self._validate_usuario(u)

        # validar unicidad del email
        existing = self.dao.get_by_email(u.email)
        if existing is not None:
            raise ValueError("Ya existe un usuario con ese email")

        # Hash de la contraseña
        if not password:
            raise ValueError("Se requiere contraseña para crear usuario")

        u.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), 
            bcrypt.gensalt()
        ).decode("utf-8")

        return self.dao.create(u)

    
    def verificar_contraseña(self, email: str, password: str) -> bool:
        usuario = self.dao.get_by_email(email)
        if not usuario:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), usuario.password_hash.encode("utf-8"))

    def actualizar_contraseña(self, usuario_id: int, nueva_password: str) -> Usuario:
        """
        Actualiza la contraseña de un usuario, recalculando el hash.
        """
        usuario = self.dao.get_by_id(usuario_id)
        if not usuario:
            raise ValueError(f"Usuario id={usuario_id} no existe")

        if not nueva_password or len(nueva_password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")

        # Calcular hash y actualizar
        usuario.password_hash = bcrypt.hashpw(nueva_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
        return self.dao.update(usuario)

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


__all__ = ["UsuarioServicio"]
