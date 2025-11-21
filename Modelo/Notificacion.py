#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional


@dataclass
class Notificacion:
    id: Optional[int] = None
    tipo: str = ""          # ejemplo: 'inventario', 'sistema', 'pedido'
    mensaje: str = ""
    producto_id: Optional[int] = None
    destinatario_id: Optional[int] = None  # id del usuario receptor (administrador)
    leida: bool = False
    nivel: str = "info"     # 'info', 'warning', 'error'

    def __repr__(self) -> str:
        return (
            f"<Notificacion id={self.id!r} tipo={self.tipo!r} "
            f"producto_id={self.producto_id!r} leida={self.leida!r}>"
        )
