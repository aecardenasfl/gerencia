# Modelo/Notificacion.py (Versión SQLAlchemy - AJUSTADA para relación unidireccional)

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from DAOs.DB import Base

class Notificacion(Base):
    __tablename__ = "notificaciones" 

    id = Column(Integer, primary_key=True, index=True)
    
    tipo = Column(String(50), default="")  
    mensaje = Column(Text, nullable=False)
    
    # 1. Llave foránea al Producto (Opcional)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=True, index=True)
    
    # 2. Llave foránea al Usuario (Destinatario)
    destinatario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    
    leida = Column(Boolean, default=False)
    nivel = Column(String(20), default="info")

    # --- Relaciones SQLAlchemy ---
    
    # 1. Relación con Usuario (BIDIRECCIONAL) - Un Usuario tiene Muchas Notificaciones
    usuario = relationship("Usuario", back_populates="notificaciones")
    
    # 2. Relación con Producto (UNIDIRECCIONAL) - La Notificación apunta al Producto,
    #    pero el Producto no tiene un atributo 'notificaciones'.
    producto = relationship("Producto", foreign_keys=[producto_id]) 

    def __repr__(self) -> str:
        return (
            f"<Notificacion id={self.id} tipo='{self.tipo}' destinatario_id={self.destinatario_id} "
            f"leida={self.leida}>"
        )