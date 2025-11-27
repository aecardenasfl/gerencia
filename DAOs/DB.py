
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from config.config_loader import Config
import logging

log = logging.getLogger(__name__)

# --- 1. Configuración de la Conexión (URL) ---
def get_db_url() -> str:
    """Construye la URL de conexión a PostgreSQL."""
    if Config.POSTGRES_DSN:
        return Config.POSTGRES_DSN
    
    # Asume que si no hay DSN, todas las variables están presentes
    return (
        f"postgresql+psycopg2://{Config.PGUSER}:{Config.PGPASSWORD}@{Config.PGHOST}:"
        f"{Config.PGPORT}/{Config.PGDATABASE}"
    )

# --- 2. Base Declarativa y Engine (Singleton) ---

# Base para todos los modelos de SQLAlchemy
Base = declarative_base()

# El Engine gestiona el pool de conexiones
# Usamos QueuePool por defecto para entornos web.
_engine = None

def get_engine():
    """Retorna el Engine singleton, creándolo si es necesario."""
    global _engine
    if _engine is None:
        log.info("Creando SQLAlchemy Engine y Pool...")
        url = get_db_url()
        # El pool es gestionado internamente por el engine
        _engine = create_engine(
            url, 
            poolclass=QueuePool, 
            pool_size=5, 
            max_overflow=10, 
            echo=False # Cambiar a True para ver SQL de debug
        )

        # Configuración del search_path si se usa SCHEMA
        if Config.PGSCHEMA:
            _engine.execution_options = {
                "schema_translate_map": {
                    None: Config.PGSCHEMA, # Mapea el esquema por defecto al configurado
                }
            }
        
    return _engine

# --- 3. Fábrica de Sesiones ---

# Crea la fábrica de sesiones (lazily loaded)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

# --- 4. Context Manager para Sesiones ---

@contextmanager
def get_session():
    """Provee una sesión de base de datos con manejo automático de cierre."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# --- 5. Helper para Crear Tablas (solo para desarrollo inicial) ---

def create_all_tables():
    """Crea todas las tablas definidas en Base si no existen."""
    Base.metadata.create_all(bind=get_engine())