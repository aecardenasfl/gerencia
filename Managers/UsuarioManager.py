#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Optional, List, Union, Any

from Modelo.Usuario import Usuario
from Servicios.UsuarioServicio import UsuarioServicio


def _call_any(obj: Any, names: list, *args, **kwargs):
    for n in names:
        fn = getattr(obj, n, None)
        if callable(fn):
            return fn(*args, **kwargs)
    raise RuntimeError(f"Ningún método válido encontrado en {obj} de: {', '.join(names)}")


class UsuarioManager:
    """Manager para usuarios: CRUD y creación de tablas (delegando en UsuarioServicio)."""

    def __init__(self, servicio: Optional[UsuarioServicio] = None):
        self.servicio = servicio or UsuarioServicio()

    def ensure_table(self) -> None:
        return _call_any(self.servicio, ["ensure_table", "crear_tabla", "create_table", "ensure_tables"])

    def create(self, data: Union[Usuario, dict]) -> Any:
        return _call_any(self.servicio, ["crear_usuario", "create_user", "create"], data)

    def get(self, usuario_id: int) -> Optional[Usuario]:
        return _call_any(self.servicio, ["obtener_usuario", "get_user", "get"], usuario_id)

    def list(self) -> List[Usuario]:
        return _call_any(self.servicio, ["listar_usuarios", "list_users", "list"])

    def update(self, usuario_id: int, data: Union[Usuario, dict]) -> Any:
        return _call_any(self.servicio, ["actualizar_usuario", "update_user", "update"], usuario_id, data)

    def delete(self, usuario_id: int) -> None:
        return _call_any(self.servicio, ["eliminar_usuario", "delete_user", "delete"], usuario_id)

