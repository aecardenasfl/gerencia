# Modelo/Usuario.py

from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column # <-- Importación clave para relaciones
from DAOs.DB import Base
from Modelo.Notificacion import Notificacion

# NOTA: Debes asegurarte de que la clase Notificacion se defina
# e importe en algún lugar para que Base.metadata la descubra.

class Usuario(Base):
    # Nombre de la tabla en la base de datos
    __tablename__ = "usuarios" 

    # --- Definición de Columnas (Misma que antes) ---
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True) 
    rol = Column(String(50), default='user')
    activo = Column(Boolean, default=True)
    password_hash = Column(Text, nullable=False)

    # --- Definición de Relaciones UNO A MUCHOS ---
    
    # 1. Relación con Pedidos (Un Usuario puede tener muchos Pedidos)
    pedidos = relationship("Pedido", back_populates="usuario")
    
    # 2. Relación con Notificaciones (Un Usuario puede tener muchas Notificaciones)
    # 'back_populates="usuario"' define el atributo inverso en el modelo Notificacion.
    notificaciones = relationship("Notificacion", back_populates="usuario") 

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} nombre='{self.nombre}' email='{self.email}'>"