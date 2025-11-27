# Modelo/Producto.py (Versión SQLAlchemy)

from sqlalchemy import Column, Integer, String, Numeric, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column 
from DAOs.DB import Base

# Nota: El tipo 'Numeric' se usa para 'precio' para manejar precisión decimal
# de forma segura en la base de datos (PostgreSQL).

class Producto(Base):
    # Nombre de la tabla
    __tablename__ = "productos" 

    # --- Definición de Columnas ---
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String, default='') # PostgreSQL maneja TEXT como String sin límite
    precio = Column(Numeric(10, 2), default=0.0) # Precio con 10 dígitos, 2 decimales
    cantidad = Column(Integer, default=0) # Stock actual
    codigo = Column(String(50), unique=True) # SKU o código (Opcional, pero se recomienda Unique)
    activo = Column(Boolean, default=True)

    # --- Definición de Relaciones UNO A MUCHOS ---
    
    # Un Producto puede aparecer en muchos Detalles de Pedido.
    # El modelo 'DetallePedido' contendrá la llave foránea 'producto_id'.
    detalles_pedido = relationship("DetallePedido", back_populates="producto")

    def __repr__(self) -> str:
        return (
            f"<Producto id={self.id} nombre='{self.nombre}' "
            f"stock={self.cantidad} precio={float(self.precio)}>"
        )

# NOTA: Los tipos de Python (float, int) se usarán para interactuar con este objeto,
# pero SQLAlchemy usa los tipos SQL (Numeric, Integer) para la base de datos.