import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24))

class DevelopmentConfig(Config):
    DEBUG = os.getenv("FLASK_ENV") == "development"
    MYSQL_HOST = os.getenv("DB_HOST", "localhost")  # DB_HOST en lugar de MYSQL_HOST
    MYSQL_PORT = os.getenv("DB_PORT", 3306)  # Añadir el puerto
    MYSQL_USER = os.getenv("DB_USERNAME", "root")  # DB_USERNAME
    MYSQL_PASSWORD = os.getenv("DB_PASSWORD")
    MYSQL_DB = os.getenv("DB_DATABASE", "seteco")

config = {
    'development': DevelopmentConfig
}
