from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column 
from typing import List
from DAOs.DB import Base
# Importamos el modelo Usuario para referenciarlo
from Modelo.Usuario import Usuario

# Usamos la clase Pedido para representar la cabecera del pedido
class Pedido(Base):
    __tablename__ = "pedidos" 

    id = Column(Integer, primary_key=True, index=True)
    
    # LLAVE FORÁNEA CLAVE 
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    
    estado = Column(String(50), default="pendiente")
    total = Column(Numeric(10, 2), default=0.0) # Usamos Numeric para precisión

    # --- Relaciones SQLAlchemy ---
    
    # Relación M:1 (Muchos Pedidos a Un Usuario)
    usuario = relationship("Usuario", back_populates="pedidos")
    
    # Relación 1:M (Un Pedido a Muchos Detalles)
    items: Mapped[List["DetallePedido"]] = relationship(
        "DetallePedido", 
        back_populates="pedido", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Pedido id={self.id} usuario_id={self.usuario_id} "
            f"estado='{self.estado}' total={float(self.total)}>"
        )
    
    def calcular_total(self) -> float:
        s = 0.0
        for it in self.items:
            pu = float(it.precio_unitario) if it.precio_unitario is not None else 0.0
            s += pu * int(it.cantidad)
        return float(s)
# El resto del archivo DetallePedido no requiere cambios.
# Modelo/DetallePedido.py (Versión SQLAlchemy)

# Nota: El archivo DetallePedido se mantiene tal cual porque no tiene un problema
# evidente en las relaciones (la relación 'pedido' es 1:1, aunque Mapped[] es 
# siempre recomendable, el error estaba específicamente en la relación List)

class DetallePedido(Base):
    __tablename__ = "detalle_pedidos" 
    
    # Clave primaria compuesta o serial simple
    id = Column(Integer, primary_key=True, index=True) 

    #  LLAVE FORÁNEA 1 (Hacia Pedido) 
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False, index=True)
    
    #  LLAVE FORÁNEA 2 (Hacia Producto) 
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)

    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Numeric(10, 2)) # Precio al momento de la compra

    # --- Relaciones SQLAlchemy ---
    
    # Relación N:1 (Muchos Detalles a Un Pedido)
    # Nota: Mapped[] también sería ideal aquí (ej: pedido: Mapped["Pedido"] = relationship(...))
    # pero el error específico del traceback se enfoca en la lista (Many-to-One).
    pedido = relationship("Pedido", back_populates="items")
    
    # Relación N:1 (Muchos Detalles a Un Producto)
    producto = relationship("Producto", back_populates="detalles_pedido")

    def __repr__(self) -> str:
        return (
            f"<DetallePedido pedido_id={self.pedido_id} producto_id={self.producto_id} "
            f"cant={self.cantidad} precio={float(self.precio_unitario)}>"
        )