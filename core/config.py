import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Rutas base del proyecto (útil para despliegues dinámicos)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "documentos"
FAISS_DIR = DATA_DIR / "faiss_index"
CA_CERT_PATH = DATA_DIR / "ca.pem"

# Credenciales APIs
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Credenciales Aiven (MySQL)
HOST_AIVEN = os.getenv("HOST_AIVEN")
PORT_AIVEN = int(os.getenv("PORT_AIVEN", 3306))
USER_AIVEN = os.getenv("USER_AIVEN")
PASSWORD_AIVEN = os.getenv("PASSWORD_AIVEN")
DATABASE_AIVEN = os.getenv("DATABASE_AIVEN")