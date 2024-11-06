import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

class Config:
    # Si SECRET_KEY está en .env, úsala; si no, genera una clave aleatoria.
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24))

class DevelopmentConfig(Config):
    DEBUG = os.getenv("FLASK_ENV") == "development"
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB", "seteco")

config = {
    'development': DevelopmentConfig
}