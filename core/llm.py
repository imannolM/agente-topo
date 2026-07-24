from langchain_groq import ChatGroq
from langchain_cohere import CohereEmbeddings
from core.config import GROQ_API_KEY, COHERE_API_KEY

# Validar que las llaves existan
if not GROQ_API_KEY or not COHERE_API_KEY:
    raise ValueError("Faltan las credenciales de Groq o Cohere en el archivo .env")

# Inicializar LLM Principal (Versatile)
llm_groq = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=GROQ_API_KEY,
    temperature=0
)

# Inicializar Modelo de Embeddings
modelo_embeddings = CohereEmbeddings(
    model="embed-multilingual-v3.0",
    cohere_api_key=COHERE_API_KEY
)