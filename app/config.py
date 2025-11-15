import os
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent.parent

class Config:
    # Usar SQLite para desarrollo (sin problemas de encoding en Windows)
    # Para PostgreSQL en producción, establece la variable de entorno DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR / "sgfcp.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    
    # Opciones del engine
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'echo': False  # Cambiar a True para ver las consultas SQL en consola
    }
