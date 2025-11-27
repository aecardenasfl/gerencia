# DAOs/PedidoDAO.py - Versión SQLAlchemy

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, update, delete
from Modelo.Pedido import Pedido, DetallePedido # Usamos los modelos SQLAlchemy
from DAOs.DB import get_session # Solo para referencia, el DAO recibe la Session

# Nota: Ya no necesitamos _TABLAS_PEDIDO_CREADAS ni _ensure_tables.

class PedidoDAO:
    """
    Data Access Object (DAO) para Pedido y DetallePedido, usando SQLAlchemy.
    """
    def __init__(self, db: Session):
        self.db = db

    # ----------------------------
    # Crear pedido
    # ----------------------------
    def create(self, pedido: Pedido) -> Pedido:
        """
        Inserta un pedido y sus detalles en una sola transacción.
        El objeto 'pedido' debe venir con la lista 'items' cargada.
        """
        # 1. Agrega el pedido. SQLAlchemy detecta los 'items' y los inserta
        # automáticamente gracias a la relación definida con 'cascade'.
        self.db.add(pedido)
        
        # 2. Guarda en la base de datos
        self.db.commit()
        
        # 3. Refresca para obtener el ID del pedido y los IDs de los detalles
        self.db.refresh(pedido) 
        
        return pedido

    # ----------------------------
    # Obtener pedido por ID
    # ----------------------------
    def get_by_id(self, pedido_id: int) -> Optional[Pedido]:
        """
        Obtiene un pedido por ID y carga sus detalles en la misma consulta
        usando 'joinedload'.
        """
        # Usamos select para poder usar joinedload (carga ansiosa)
        stmt = (
            select(Pedido)
            .options(joinedload(Pedido.items)) # Carga los DetallePedido en 1 consulta
            .where(Pedido.id == pedido_id)
        )
        # El ORM mapea la fila principal a Pedido y las anidadas a Pedido.items
        return self.db.scalars(stmt).unique().one_or_none()


    # ----------------------------
    # Actualizar estado (sin lógica)
    # ----------------------------
    def update_estado(self, pedido_id: int, nuevo_estado: str) -> Optional[int]:
        """Actualiza solo el campo 'estado' y retorna el ID."""
        stmt = (
            update(Pedido)
            .where(Pedido.id == pedido_id)
            .values(estado=nuevo_estado)
            .returning(Pedido.id)
        )
        
        updated_id = self.db.execute(stmt).scalar_one_or_none()
        self.db.commit()
        return updated_id


    # ----------------------------
    # Consulta: pedidos por usuario
    # ----------------------------
    def get_by_usuario(self, usuario_id: int) -> List[Pedido]:
        """
        Retorna la lista de pedidos de un usuario, cargando los detalles
        de cada pedido de forma eficiente.
        """
        stmt = (
            select(Pedido)
            .options(joinedload(Pedido.items)) # ⬅️ Carga los detalles en la misma consulta
            .where(Pedido.usuario_id == usuario_id)
            .order_by(Pedido.id)
        )
        # El ORM se encarga de agrupar los resultados en objetos Pedido con sus items.
        return self.db.scalars(stmt).unique().all()

    # ----------------------------
    # Otras operaciones
    # ----------------------------

    def list_all(self) -> List[Pedido]:
        """Lista todos los pedidos (con sus detalles)."""
        stmt = select(Pedido).options(joinedload(Pedido.items)).order_by(Pedido.id)
        return self.db.scalars(stmt).all()

    def delete(self, pedido_id: int) -> bool:
        """Elimina un pedido y sus detalles asociados (gracias a ON DELETE CASCADE)."""
        stmt = delete(Pedido).where(Pedido.id == pedido_id)
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0