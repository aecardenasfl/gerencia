#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Capa de Servicio para la entidad Notificacion.

Maneja la lógica de negocio y utiliza NotificacionDAO para interactuar con la DB.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from Modelo.Notificacion import Notificacion
from DAOs.NotificacionDAO import NotificacionDAO

# Importar la función get_db de donde la tengas definida
# from DAOs.DB_SQLAlchemy import SessionLocal 

class NotificacionServicio:
    """
    Gestiona las operaciones de negocio relacionadas con las notificaciones.
    """
    def __init__(self, db: Session):
        # Inyectamos la sesión de DB y creamos el DAO
        self.db = db
        self.dao = NotificacionDAO(db)

    # --- Métodos requeridos por el Controlador ---

    def listar_por_usuario(self, usuario_id: int, solo_no_leidas: bool) -> List[Notificacion]:
        """
        Obtiene la lista de notificaciones para un usuario específico.
        """
        # La lógica de filtrado se pasa al DAO.
        return self.dao.list_by_user(usuario_id, solo_no_leidas)

    def marcar_como_leida(self, notificacion_id: int) -> bool:
        """
        Marca una notificación específica como leída.
        """
        # La lógica atómica de actualización se ejecuta en el DAO.
        # Si el DAO no encuentra el ID, retorna False, que el controlador interpreta como 404.
        return self.dao.mark_as_read(notificacion_id)

    def eliminar_por_usuario(self, usuario_id: int) -> None:
        """
        Elimina todas las notificaciones de un usuario.
        """
        # Implementaremos un método específico en el DAO para una eliminación masiva eficiente.
        # Nota: Asumimos que NotificacionDAO tiene o tendrá este método.
        try:
            self.dao.delete_by_user(usuario_id)
        except Exception as e:
            # En un entorno real, manejar aquí logs o excepciones específicas
            print(f"Error al eliminar notificaciones del usuario {usuario_id}: {e}")
            pass # No lanzamos error si no se encuentra, ya que DELETE es idempotente.

    def eliminar_por_id(self, notificacion_id: int) -> bool:
        """
        Elimina una notificación individual por ID.
        """
        return self.dao.delete(notificacion_id)

    # --- Métodos adicionales (para la creación de notificaciones por lógica de negocio) ---

    def crear_notificacion(self, tipo: str, mensaje: str, destinatario_id: int, 
                           producto_id: Optional[int] = None, nivel: str = "info") -> Notificacion:
        """
        Crea una nueva instancia de Notificacion y la guarda en la base de datos.
        """
        n = Notificacion(
            tipo=tipo,
            mensaje=mensaje,
            producto_id=producto_id,
            destinatario_id=destinatario_id,
            leida=False,
            nivel=nivel
        )
        return self.dao.create(n)
    
    def marcar_todas_como_leidas(self, usuario_id: int) -> int:
        """Marca todas las notificaciones de un usuario como leídas."""
        return self.dao.mark_all_as_read_by_user(usuario_id)
