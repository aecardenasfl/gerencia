from typing import List, Optional, Union
from Modelo.Producto import Producto
from Modelo.Notificacion import Notificacion
from DAOs.ProductoDAO import ProductoDAO
from DAOs.UsuarioDAO import UsuarioDAO
from DAOs.NotificacionDAO import NotificacionDAO
from DAOs.DB import get_session

class ProductoServicio:
    """
    Servicio de negocio para Producto. Maneja CRUD, ajuste de stock y procesamiento de lecturas de sensores
    generando notificaciones para administradores si el stock es bajo o agotado.
    """

    # ------------------------------------------------------------
    # VALIDACIÓN DE PRODUCTO
    # ------------------------------------------------------------
    @staticmethod
    def _validate_producto(p: Producto) -> None:
        if not p.nombre.strip():
            raise ValueError("'nombre' es requerido")
        if float(p.precio) < 0:
            raise ValueError("'precio' no puede ser negativo")
        if int(p.cantidad) < 0:
            raise ValueError("'cantidad' no puede ser negativa")

    # ------------------------------------------------------------
    # OPERACIONES CRUD
    # ------------------------------------------------------------
    def crear_producto(self, data: Union[Producto, dict]) -> Producto:
        p = data if isinstance(data, Producto) else Producto(**data)
        self._validate_producto(p)
        with get_session() as db:
            dao = ProductoDAO(db)
            return dao.create(p)

    def obtener_producto(self, producto_id: int) -> Optional[Producto]:
        with get_session() as db:
            dao = ProductoDAO(db)
            return dao.get_by_id(producto_id)

    def listar_productos(self) -> List[Producto]:
        with get_session() as db:
            dao = ProductoDAO(db)
            return dao.list_all()

    def actualizar_producto(self, producto_id: int, data: Union[Producto, dict]) -> Producto:
        with get_session() as db:
            dao = ProductoDAO(db)
            existing = dao.get_by_id(producto_id)
            if not existing:
                raise ValueError(f"Producto con id={producto_id} no existe")
            updated = Producto(**{**data, "id": producto_id}) if isinstance(data, dict) else data
            self._validate_producto(updated)
            return dao.update(updated)

    def eliminar_producto(self, producto_id: int) -> None:
        with get_session() as db:
            dao = ProductoDAO(db)
            dao.delete(producto_id)

    # ------------------------------------------------------------
    # AJUSTE DE STOCK
    # ------------------------------------------------------------
    def ajustar_stock(self, producto_id: int, delta: int) -> int:
        with get_session() as db:
            dao = ProductoDAO(db)
            new_qty = dao.adjust_stock(producto_id, delta)
            if new_qty is None:
                raise ValueError(f"Producto con id={producto_id} no existe")
            if new_qty < 0:
                raise ValueError("Stock insuficiente")
            return new_qty

    # ------------------------------------------------------------
    # PROCESAR LECTURAS DE SENSORES
    # ------------------------------------------------------------
    def procesar_lecturas_sensor(self, lecturas: List[dict]):
        with get_session() as db:
            producto_dao = ProductoDAO(db)
            notificacion_dao = NotificacionDAO(db)
            usuario_dao = UsuarioDAO(db)

            admins = usuario_dao.get_usuarios_por_rol("admin")

            for lectura in lecturas:
                producto_id = lectura["producto_id"]
                cantidad = lectura["cantidad"]

                producto_dao.replace_stock(producto_id, cantidad)
                producto = producto_dao.get_by_id(producto_id)

                if producto is None:
                    print(f"[WARNING] Producto con id={producto_id} no existe. Lectura ignorada.")
                    continue  # <-- Ignora esta lectura y pasa a la siguiente

                mensaje = None
                nivel = "info"

                if producto.cantidad == 0:
                    mensaje = f"Stock agotado: Producto {producto_id} está sin stock"
                    nivel = "error"
                elif producto.cantidad <= 10:
                    mensaje = f"Stock bajo: Producto {producto_id} tiene {producto.cantidad} unidades"
                    nivel = "warning"

                if mensaje:
                    for admin in admins:
                        notificacion = Notificacion(
                            tipo="inventario",
                            mensaje=mensaje,
                            producto_id=producto_id,
                            destinatario_id=admin.id,
                            leida=False,
                            nivel=nivel
                        )
                        notificacion_dao.create(notificacion)
