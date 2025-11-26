#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Optional, Union, List

from Modelo.Pedido import Pedido, DetallePedido
from DAOs.PedidoDAO import PedidoDAO
from DAOs.ProductoDAO import ProductoDAO
from DAOs.UsuarioDAO import UsuarioDAO


class PedidoServicio:
    """
    Servicio de negocio para gestionar pedidos.
    Realiza:
      - Validación de usuario
      - Validación de items y cantidades
      - Verificación de stock
      - Obtención de precio unitario si falta
      - Cálculo de total del pedido
      - Delegación de persistencia al PedidoDAO
    """

    def __init__(self,
                 pedido_dao: Optional[PedidoDAO] = None,
                 producto_dao: Optional[ProductoDAO] = None,
                 usuario_dao: Optional[UsuarioDAO] = None):

        self.pedido_dao = pedido_dao or PedidoDAO()
        self.producto_dao = producto_dao or ProductoDAO()
        self.usuario_dao = usuario_dao or UsuarioDAO()

    # ------------------------------------------------------------
    # VALIDACIONES INTERNAS DEL SERVICIO
    # ------------------------------------------------------------

    def _validar_usuario(self, usuario_id: int):
        usuario = self.usuario_dao.get_by_id(usuario_id)
        if usuario is None:
            raise ValueError(f"Usuario con id={usuario_id} no existe")
        return usuario

    def _validar_items_y_enriquecer(self, pedido: Pedido):
        """
        - Verifica que haya items
        - Verifica cantidades > 0
        - Verifica existencia del producto
        - Completa precio_unitario si está vacío
        - Verifica stock disponible
        """
        if not pedido.items or len(pedido.items) == 0:
            raise ValueError("El pedido debe contener al menos un item")

        for it in pedido.items:

            # Cantidad válida
            if it.cantidad <= 0:
                raise ValueError(f"La cantidad del producto {it.producto_id} debe ser positiva")

            # Obtener producto real
            prod = self.producto_dao.get_by_id(it.producto_id)
            if prod is None:
                raise ValueError(f"Producto con id={it.producto_id} no existe")

            # Validar stock
            if prod.cantidad < it.cantidad:
                raise ValueError(
                    f"Stock insuficiente para producto id={it.producto_id}. "
                    f"Disponible={prod.cantidad}, solicitado={it.cantidad}"
                )

            # Completar precio unitario si falta
            if it.precio_unitario is None:
                it.precio_unitario = float(prod.precio)

        # Finalmente recalcular total
        pedido.total = pedido.calcular_total()

    # ------------------------------------------------------------
    # MÉTODOS PÚBLICOS DEL SERVICIO
    # ------------------------------------------------------------

    def crear_pedido(self, data: Union[Pedido, dict]) -> Pedido:
        """
        Crea un pedido aplicando todas las reglas de negocio.
        """

        pedido = data if isinstance(data, Pedido) else Pedido(**data)

        # Validar usuario
        if pedido.usuario_id is None:
            raise ValueError("El pedido debe incluir usuario_id")

        self._validar_usuario(pedido.usuario_id)

        # Validar items + completar info + verificar stock
        self._validar_items_y_enriquecer(pedido)

        # Delegar creación al DAO (que hace transacción + afecta stock)
        creado = self.pedido_dao.create(pedido)
        return creado

    def obtener_pedido(self, pedido_id: int) -> Optional[Pedido]:
        return self.pedido_dao.get_by_id(pedido_id)

    def listar_pedidos_usuario(self, usuario_id: int) -> List[Pedido]:
        """
        Nueva funcionalidad: listar los pedidos de un usuario.
        """
        self._validar_usuario(usuario_id)
        return self.pedido_dao.get_by_usuario(usuario_id)

    def cambiar_estado(self, pedido_id: int, nuevo_estado: str) -> Pedido:
        estados_validos = ["pendiente", "confirmado", "enviado", "cancelado"]

        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado '{nuevo_estado}' no es válido")

        actualizado = self.pedido_dao.update_estado(pedido_id, nuevo_estado)

        if actualizado is None:
            raise ValueError(f"Pedido con id={pedido_id} no existe")

        return actualizado
