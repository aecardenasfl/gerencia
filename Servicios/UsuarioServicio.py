from typing import Optional, Union
import bcrypt
from Modelo.Usuario import Usuario
from DAOs.UsuarioDAO import UsuarioDAO

class UsuarioServicio:
    def __init__(self, dao: UsuarioDAO):
        self.dao = dao

    def _validate_usuario(self, u: Usuario) -> None:
        if not u.nombre or not u.nombre.strip():
            raise ValueError("'nombre' es requerido")
        if not u.email or '@' not in u.email:
            raise ValueError("'email' inválido")
        if u.rol not in ('user', 'admin'):
            raise ValueError("'rol' inválido")

    def crear_usuario(self, data: Union[Usuario, dict], password: str) -> Usuario:
        u = data if isinstance(data, Usuario) else Usuario(**data)
        self._validate_usuario(u)

        if self.dao.get_by_email(u.email):
            raise ValueError("Ya existe un usuario con ese email")

        if not password:
            raise ValueError("Se requiere contraseña")
        u.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        return self.dao.create(u)

    def verificar_contraseña(self, email: str, password: str) -> bool:
        usuario = self.dao.get_by_email(email)
        if not usuario:
            return False
        return bcrypt.checkpw(password.encode(), usuario.password_hash.encode())

    def actualizar_contraseña(self, usuario_id: int, nueva_password: str) -> Usuario:
        usuario = self.dao.get_by_id(usuario_id)
        if not usuario:
            raise ValueError(f"Usuario id={usuario_id} no existe")
        if len(nueva_password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        usuario.password_hash = bcrypt.hashpw(nueva_password.encode(), bcrypt.gensalt()).decode()
        return self.dao.update(usuario)

    def obtener_usuario(self, usuario_id: int) -> Optional[Usuario]:
        return self.dao.get_by_id(usuario_id)

    def listar_usuarios(self):
        return self.dao.list_all()

    def actualizar_usuario(self, usuario_id: int, data: Union[Usuario, dict]) -> Usuario:
        existing = self.dao.get_by_id(usuario_id)
        if not existing:
            raise ValueError(f"Usuario id={usuario_id} no existe")
        updated = Usuario(
            id=usuario_id,
            nombre=data.get('nombre', existing.nombre),
            email=data.get('email', existing.email),
            rol=data.get('rol', existing.rol),
            activo=data.get('activo', existing.activo),
        )
        self._validate_usuario(updated)
        return self.dao.update(updated)

    def eliminar_usuario(self, usuario_id: int) -> None:
        self.dao.delete(usuario_id)
