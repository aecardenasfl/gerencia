#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Data Access Object (DAO) para el modelo Notificacion, utilizando SQLAlchemy."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from Modelo.Notificacion import Notificacion

class NotificacionDAO:
    """
    Data Access Object (DAO) para el modelo Notificacion, utilizando SQLAlchemy.
    """
    def __init__(self, db: Session):
        self.db = db

    # ----------------------------
    # CRUD
    # ----------------------------
    def create(self, n: Notificacion) -> Notificacion:
        """Crea una nueva notificación."""
        self.db.add(n)
        self.db.commit()
        self.db.refresh(n)
        return n

    def get_by_id(self, notificacion_id: int) -> Optional[Notificacion]:
        """Obtiene una notificación por ID."""
        return self.db.get(Notificacion, notificacion_id)

    def list_all(self) -> List[Notificacion]:
        """Lista todas las notificaciones ordenadas por ID."""
        stmt = select(Notificacion).order_by(Notificacion.id)
        return self.db.scalars(stmt).all()
        
    def list_by_user(self, usuario_id: int, solo_no_leidas: bool = False) -> List[Notificacion]:
        """Lista las notificaciones para un usuario específico, con filtro opcional."""
        stmt = (
            select(Notificacion)
            .where(Notificacion.destinatario_id == usuario_id)
            .order_by(Notificacion.id.desc()) # Mostrar las más recientes primero
        )
        
        if solo_no_leidas:
            stmt = stmt.where(Notificacion.leida == False)
        
        return self.db.scalars(stmt).all()

    def update(self, n: Notificacion) -> Notificacion:
        """Actualiza una notificación existente."""
        if n.id is None:
            raise ValueError("Notificacion.id es requerido para actualizar")
        
        # 1. Obtenemos la instancia para que SQLAlchemy pueda rastrear los cambios
        notificacion_db = self.db.get(Notificacion, n.id)
        
        if not notificacion_db:
            raise ValueError(f"Notificacion con id={n.id} no encontrada para actualizar")

        # 2. Copiamos/actualizamos los atributos del objeto pasado
        # Usamos el objeto de la base de datos para actualizar
        notificacion_db.tipo = n.tipo
        notificacion_db.mensaje = n.mensaje
        notificacion_db.producto_id = n.producto_id
        notificacion_db.destinatario_id = n.destinatario_id
        notificacion_db.leida = n.leida
        notificacion_db.nivel = n.nivel
            
        self.db.commit()
        self.db.refresh(notificacion_db)
        return notificacion_db
    
    def mark_as_read(self, notificacion_id: int) -> bool:
        """
        Marca una notificación específica como leída.
        Retorna True si se actualizó al menos una fila, False si no existía.
        """
        stmt = update(Notificacion).where(Notificacion.id == notificacion_id).values(leida=True)
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0


    def mark_all_as_read_by_user(self, usuario_id: int) -> int:
        stmt = update(Notificacion).where(Notificacion.destinatario_id == usuario_id).values(leida=True)
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount


    def delete(self, notificacion_id: int) -> bool:
        """Elimina una notificación por ID."""
        stmt = delete(Notificacion).where(Notificacion.id == notificacion_id)
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0

    def delete_by_user(self, usuario_id: int) -> None:
        """
        Elimina todas las notificaciones de un usuario de forma masiva y eficiente.
        """
        stmt = delete(Notificacion).where(Notificacion.destinatario_id == usuario_id)
        self.db.execute(stmt)
        self.db.commit()
        # No necesitamos retornar nada, el proceso es la eliminación.