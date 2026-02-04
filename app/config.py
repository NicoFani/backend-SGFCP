import os
from pathlib import Path
from dotenv import load_dotenv

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent.parent

# Cargar variables desde .env si existe
load_dotenv(BASE_DIR / '.env')
# Compatibilidad: .env dentro de app/
load_dotenv(Path(__file__).parent / '.env')

class Config:
    # Usar SQLite para desarrollo (sin problemas de encoding en Windows)
    # Para PostgreSQL en producción, establece la variable de entorno DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR / "sgfcp.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 días
    
    # Opciones del engine
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'echo': False  # Cambiar a True para ver las consultas SQL en consola
    }

    # Brevo (Sendinblue) Email
    BREVO_API_KEY = os.getenv('BREVO_API_KEY', '')
    BREVO_SENDER_EMAIL = os.getenv('BREVO_SENDER_EMAIL', 'utnros2023@gmail.com')
    BREVO_SENDER_NAME = os.getenv('BREVO_SENDER_NAME', 'Fleeight')
    BREVO_ACCOUNTING_RECIPIENTS = os.getenv(
        'BREVO_ACCOUNTING_RECIPIENTS',
        'nicolasfani02@hotmail.com,mongelosmanuel6@gmail.com'
    )
