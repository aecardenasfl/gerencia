#!/usr/bin/python
# -*- coding: utf-8 -*-

from fastapi import Depends
from Managers.UsuarioManager import UsuarioManager

def obtener_servicio_usuario() -> UsuarioManager:
    # Antes devolvía UsuarioServicio(); ahora devolvemos el manager
    return UsuarioManager()

# Ejemplo de uso en un endpoint:
# @router.get("/", response_model=List[Usuario])
# def listar_usuarios(manager: UsuarioManager = Depends(obtener_servicio_usuario)):
#     return manager.list()

class UsuarioControlador:
    pass