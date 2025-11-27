from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from Modelo.Usuario import Usuario

class UsuarioDAO:
    """
    DAO para operaciones CRUD sobre el modelo Usuario.
    Se asume que la sesión (Session) es inyectada desde FastAPI o desde el servicio.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, u: Usuario) -> Usuario:
        """Inserta un usuario y retorna el objeto con ID generado."""
        self.db.add(u)
        self.db.commit()
        self.db.refresh(u)
        return u

    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID."""
        return self.db.get(Usuario, usuario_id)

    def get_by_email(self, email: str) -> Optional[Usuario]:
        """Obtiene un usuario por email."""
        stmt = select(Usuario).where(Usuario.email == email)
        return self.db.scalar(stmt)

    def list_all(self) -> List[Usuario]:
        """Lista todos los usuarios ordenados por ID."""
        stmt = select(Usuario).order_by(Usuario.id)
        return list(self.db.scalars(stmt))

    def update(self, u: Usuario) -> Usuario:
        """Actualiza un usuario existente."""
        usuario_db = self.db.get(Usuario, u.id)
        if not usuario_db:
            raise ValueError(f"Usuario con id={u.id} no encontrado")

        usuario_db.nombre = u.nombre
        usuario_db.email = u.email
        usuario_db.rol = u.rol
        usuario_db.activo = u.activo
        if hasattr(u, 'password_hash') and u.password_hash:
            usuario_db.password_hash = u.password_hash

        self.db.commit()
        self.db.refresh(usuario_db)
        return usuario_db

    def delete(self, usuario_id: int) -> None:
        """Elimina un usuario por ID."""
        stmt = delete(Usuario).where(Usuario.id == usuario_id)
        self.db.execute(stmt)
        self.db.commit()

    # Métodos auxiliares opcionales
    def get_usuarios_por_rol(self, rol: str) -> List[Usuario]:
        stmt = select(Usuario).where(Usuario.rol == rol).order_by(Usuario.id)
        return list(self.db.scalars(stmt))

    def list_activos(self) -> List[Usuario]:
        stmt = select(Usuario).where(Usuario.activo == True).order_by(Usuario.id)
        return list(self.db.scalars(stmt))
