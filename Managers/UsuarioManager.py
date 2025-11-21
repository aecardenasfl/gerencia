#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Optional, List, Union

from Modelo.Usuario import Usuario
from Servicios.UsuarioServicio import UsuarioServicio


class UsuarioManager:
    """Manager ligero que delega en Servicios.UsuarioServicio."""

    def __init__(self, servicio: Optional[UsuarioServicio] = None):
        self.servicio = servicio or UsuarioServicio()

    def ensure_table(self) -> None:
        self.servicio.ensure_table()

    def create(self, data: Union[Usuario, dict]) -> Usuario:
        return self.servicio.crear_usuario(data)

    def get(self, usuario_id: int) -> Optional[Usuario]:
        return self.servicio.obtener_usuario(usuario_id)

    def list(self) -> List[Usuario]:
        return self.servicio.listar_usuarios()

    def update(self, usuario_id: int, data: Union[Usuario, dict]) -> Usuario:
        return self.servicio.actualizar_usuario(usuario_id, data)

    def delete(self, usuario_id: int) -> None:
        self.servicio.eliminar_usuario(usuario_id)