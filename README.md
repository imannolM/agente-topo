# 🏗️ Agente Topo - Asistente de IA para Terrenos TOPO
![Logo Terrenos TOPO](logo_topo.png)

[Streamlit App] (https://agente-topo.streamlit.app/)

**Agente Topo** es un asistente conversacional inteligente impulsado por Inteligencia Artificial, diseñado específicamente para optimizar la gestión operativa, el análisis de datos financieros y la consulta de normativas internas de la empresa de bienes raíces "Terrenos TOPO".

🔗 **Enlace de la aplicación en vivo:** [https://agente-topo.streamlit.app/](https://agente-topo.streamlit.app/)

---

## 📖 Descripción General del Proyecto

En el sector inmobiliario y de gestión de terrenos, el personal a menudo pierde tiempo valioso buscando información en reglamentos extensos o solicitando reportes manuales sobre ventas y presupuestos. 

El **Agente Topo** centraliza y automatiza estos procesos. Utiliza un enfoque avanzado de **Agente ReAct** (Razonamiento y Acción) que evalúa las intenciones del usuario en lenguaje natural y decide inteligentemente qué herramienta utilizar:
1. Buscar en documentos PDF corporativos (RAG) para resolver dudas sobre reglamentos o ventas.
2. Conectarse a la base de datos MySQL de la empresa para realizar consultas analíticas o generar reportes financieros.
3. Responder de forma conversacional utilizando memoria del chat.

---

## 🔐 Credenciales de Acceso (Para Evaluadores)

El sistema cuenta con seguridad de autenticación basada en roles para proteger la información y habilitar funciones específicas dependiendo del usuario. Puedes acceder a la plataforma utilizando las siguientes credenciales:

| Rol | Usuario | Contraseña | Permisos |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `admin123` | Chat, Análisis de DB, Generación de Gráficos y **Actualización de base de conocimiento (RAG)** mediante carga de PDFs. |
| **Empleado** | `empleado` | `empleado123` | Chat, Análisis de DB y Generación de Gráficos. |

---

## 🧠 Arquitectura de la Solución

El proyecto está construido bajo una arquitectura modular y escalable, orquestada mediante grafos de estado.

1. **Interfaz de Usuario (Frontend):** Construida con Streamlit, maneja el estado de la sesión, la autenticación, el historial de chat y el renderizado dinámico de texto e imágenes.
2. **Motor Cognitivo (Cerebro):** Un agente orquestado por LangGraph e impulsado por el LLM Llama 3 (vía Groq), el cual actúa como enrutador inteligente.
3. **Herramientas (Tools):**
   * **RAG Engine:** Utiliza FAISS y Cohere Embeddings para vectorizar e indexar PDFs. La interfaz permite al administrador inyectar nuevos documentos en caliente.
   * **Data Analytics:** Conexión segura a una base de datos MySQL en la nube (Aiven). Ejecuta consultas SQL generadas por el LLM y utiliza Pandas/Matplotlib para retornar cálculos numéricos y renderizar gráficos.

---

## 🛠️ Tecnologías y Herramientas Utilizadas

* **Lenguaje:** Python 3.11
* **Frontend:** Streamlit
* **Orquestación de IA:** LangChain & LangGraph
* **Modelos LLM:** Groq API (Llama 3)
* **Embeddings:** Cohere API
* **Base de Datos & Vector Store:** Aiven Cloud (MySQL) y FAISS (Local Vector Search)
* **Análisis de Datos:** Pandas, Matplotlib, SQLAlchemy
* **Despliegue (Deploy):** Streamlit Community Cloud & GitHub

---

## 📂 Estructura del Proyecto

El código fuente está modularizado aplicando separación de responsabilidades para asegurar su mantenibilidad:

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
│   ├── llm.py                   # Inicialización de Groq y Cohere
│   └── prompts.py               # Todos los prompts utilizados
│
├── services/                    # Lógica de negocio
│   ├── __init__.py
│   ├── database.py              # Conexión MySQL, validación de accesos y consultas
│   ├── rag.py                   # Carga de documentos, embeddings y FAISS
│   ├── analytics.py             # Análisis con Pandas, Matplotlib y agente ReAct
│   └── soporte.py               # Aquí van pedir_info() y agendar_cita()
│
├── agent/                       # Implementación del flujo con LangGraph
│   ├── __init__.py
│   ├── state.py                 # Definición del AgentState (TypedDict)
│   ├── nodes.py                 # Implementación de los nodos del grafo
│   ├── edges.py                 # Funciones de enrutamiento entre nodos
│   ├── graph.py                 # Construcción y compilación del StateGraph
│   └── chains.py                # Aquí va TriajeOut y chain_de_triaje
│
└── utils/                       # Funciones auxiliares
    ├── __init__.py
    └── helpers.py               # Funciones de apoyo (normalización, utilidades, etc.)