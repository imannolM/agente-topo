# Estructura del proyecto

```text
agente_topo/
├── .env.example                 # Variables de entorno (Groq, Cohere, Aiven)
├── requirements.txt             # Dependencias de Python
├── app.py                       # Frontend en Streamlit (Punto de entrada)
│
├── data/
│   ├── documentos/              # PDFs oficiales utilizados por el sistema RAG
│   ├── faiss_index/             # Índice vectorial persistente de FAISS
│   └── ca.pem                   # Certificado SSL para MySQL en Aiven
│
├── core/                        # Infraestructura y configuración base
│   ├── __init__.py
│   ├── config.py                # Carga de variables de entorno (.env)
│   └── llm.py                   # Inicialización de Groq y Cohere
│
├── services/                    # Lógica de negocio
│   ├── __init__.py
│   ├── database.py              # Conexión MySQL, validación de accesos y consultas
│   ├── rag.py                   # Carga de documentos, embeddings y FAISS
│   └── analytics.py             # Análisis con Pandas, Matplotlib y agente ReAct
│
├── agent/                       # Implementación del flujo con LangGraph
│   ├── __init__.py
│   ├── state.py                 # Definición del AgentState (TypedDict)
│   ├── nodes.py                 # Implementación de los nodos del grafo
│   ├── edges.py                 # Funciones de enrutamiento entre nodos
│   └── graph.py                 # Construcción y compilación del StateGraph
│
└── utils/                       # Funciones auxiliares
    ├── __init__.py
    └── helpers.py               # Funciones de apoyo (normalización, utilidades, etc.)
```