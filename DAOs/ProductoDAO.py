from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from Modelo.Producto import Producto

class ProductoDAO:
    def __init__(self, db: Session):
        self.db = db

    def create(self, p: Producto) -> Producto:
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return p

    def get_by_id(self, producto_id: int) -> Optional[Producto]:
        return self.db.get(Producto, producto_id)

    def list_all(self) -> List[Producto]:
        stmt = select(Producto).order_by(Producto.id)
        return list(self.db.scalars(stmt))

    def update(self, p: Producto) -> Producto:
        producto_db = self.db.get(Producto, p.id)
        if not producto_db:
            raise ValueError(f"Producto con id={p.id} no encontrado")
        producto_db.nombre = p.nombre
        producto_db.descripcion = p.descripcion
        producto_db.precio = p.precio
        producto_db.cantidad = p.cantidad
        producto_db.codigo = getattr(p, "codigo", producto_db.codigo)
        producto_db.activo = getattr(p, "activo", producto_db.activo)
        self.db.commit()
        self.db.refresh(producto_db)
        return producto_db

    def delete(self, producto_id: int) -> None:
        stmt = delete(Producto).where(Producto.id == producto_id)
        self.db.execute(stmt)
        self.db.commit()

    def adjust_stock(self, producto_id: int, delta: int) -> Optional[int]:
        stmt = (
            update(Producto)
            .where(Producto.id == producto_id)
            .values(cantidad=Producto.cantidad + delta)
            .returning(Producto.cantidad)
        )
        new_qty = self.db.execute(stmt).scalar_one_or_none()
        self.db.commit()
        return new_qty

    def replace_stock(self, producto_id: int, nueva_cantidad: int) -> Optional[int]:
        stmt = (
            update(Producto)
            .where(Producto.id == producto_id)
            .values(cantidad=nueva_cantidad)
            .returning(Producto.cantidad)
        )
        new_qty = self.db.execute(stmt).scalar_one_or_none()
        self.db.commit()
        return new_qty
