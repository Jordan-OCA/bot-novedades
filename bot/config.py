# config.py
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Leer usuario y contraseña
USER = os.getenv("USEROPERA")
PASSWORD = os.getenv("PASSWORDOPERA")

# Validación opcional para asegurarse que existen
if not USER or not PASSWORD:
    raise ValueError("❌ Las variables USEROPERA o PASSWORDOPERA no están definidas en el .env")
