import os
from typing import Dict
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from re import search
from langchain_community.vectorstores import FAISS
from core.prompts import prompt_rag

# Importamos las configuraciones de nuestro core
from core.config import DOCS_DIR, FAISS_DIR
from core.llm import modelo_embeddings, llm_groq

#PromptTemplate para document_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

def construir_o_cargar_retriever():
    """Carga FAISS localmente o lo procesa desde cero, devolviendo el retriever."""
    if os.path.exists(FAISS_DIR) and os.listdir(FAISS_DIR):
        print("Cargando índice vectorial FAISS existente desde el disco...")
        vectorstore = FAISS.load_local(
            folder_path=str(FAISS_DIR), 
            embeddings=modelo_embeddings, 
            allow_dangerous_deserialization=True
        )
    else:
        print("Índice no encontrado. Leyendo PDFs y construyendo FAISS...")
        loader = PyPDFDirectoryLoader(str(DOCS_DIR))
        documentos = loader.load()
        
        if not documentos:
            raise ValueError(f"No se encontraron PDFs en: {DOCS_DIR}")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
        chunks = text_splitter.split_documents(documentos)

        vectorstore = FAISS.from_documents(documents=chunks, embedding=modelo_embeddings)
        
        os.makedirs(FAISS_DIR, exist_ok=True)
        vectorstore.save_local(str(FAISS_DIR))
        print("Índice FAISS guardado exitosamente.")
        
    return vectorstore.as_retriever(search_type = 'similarity_score_threshold', search_kwargs = {'score_threshold': 0.3, 'k': 4})

# 1. Inicializamos el retriever de forma global para que la función lo pueda usar
retriever = construir_o_cargar_retriever()

document_chain = create_stuff_documents_chain(llm_groq, prompt_rag)

# --- FUNCIÓN RAG EXACTA DE TU NOTEBOOK ---
def busqueda_de_respuestas_RAG(pregunta: str) -> Dict:
    documentos_relacionados = retriever.invoke(pregunta)
    frase_no_info = "Lo siento, no dispongo de información oficial sobre ese tema en este momento."

    if not documentos_relacionados:
        return {
            'respuesta': frase_no_info,
            'citaciones': [],
            'documentos_encontrados': False
        }

    # Asumiendo que document_chain ya está configurado arriba
    answer = document_chain.invoke({
        'input': pregunta,
        'context': documentos_relacionados
    })

    # Verificamos si el LLM generó la frase de contingencia
    if answer.strip().rstrip('.!?') == frase_no_info.rstrip('.!?'):
        return {
            'respuesta': frase_no_info,
            'citaciones': [],
            'documentos_encontrados': False
        }

    return {
        'respuesta': answer,
        'citaciones': documentos_relacionados,
        'documentos_encontrados': True
    }