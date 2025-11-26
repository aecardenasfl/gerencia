from dataclasses import dataclass
from typing import Optional

@dataclass
class Usuario:
    id: Optional[int] = None
    nombre: str = ""
    email: str = ""
    rol: str = "user"
    activo: bool = True
    password_hash: str = ""  # Almacenar el hash, nunca el password en texto plano

    def __repr__(self) -> str:
        return (
            f"<Usuario id={self.id!r} email={self.email!r} "
            f"nombre={self.nombre!r} rol={self.rol!r}>"
        )
