#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
`PedidoItem` representa una línea de pedido (producto + cantidad + precio unitario).
`Pedido` contiene una lista de `PedidoItem` y metadatos básicos.
Las clases son contenedores de datos únicamente; la lógica de negocio
quedará en los managers/servicios.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DetallePedido:
    producto_id: int
    cantidad: int = 1
    precio_unitario: Optional[float] = None  # precio al momento del pedido
    pedido_id: Optional[int] = None
    
    def __repr__(self) -> str:
        return (
            f"<PedidoItem producto_id={self.producto_id!r} "
            f"cantidad={self.cantidad!r} precio_unitario={self.precio_unitario!r}>"
        )


@dataclass
class Pedido:
    id: Optional[int] = None
    usuario_id: Optional[int] = None
    estado: str = "pendiente"  # e.g., pendiente, confirmado, enviado, cancelado
    items: List[DetallePedido] = field(default_factory=list)
    total: float = 0.0

    def calcular_total(self) -> float:
        s = 0.0
        for it in self.items:
            pu = float(it.precio_unitario) if it.precio_unitario is not None else 0.0
            s += pu * int(it.cantidad)
        return float(s)

    def __repr__(self) -> str:
        return (
            f"<Pedido id={self.id!r} usuario_id={self.usuario_id!r} "
            f"estado={self.estado!r} items={len(self.items)!r} total={self.total!r}>"
        )
