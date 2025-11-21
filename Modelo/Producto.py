#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional


@dataclass
class Producto:
    id: Optional[int] = None
    nombre: str = ""
    descripcion: str = ""
    precio: float = 0.0
    cantidad: int = 0
    codigo: Optional[str] = None  # SKU o código identificador
    activo: bool = True

    def __repr__(self) -> str:
        return (
            f"<Producto id={self.id!r} nombre={self.nombre!r} "
            f"cantidad={self.cantidad!r} precio={self.precio!r}>"
        )
