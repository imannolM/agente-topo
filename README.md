# 🏗️ Agente Topo - Asistente de IA para Terrenos TOPO
![Logo Terrenos TOPO](logo_topo.png)


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

## 🔐 Credenciales de Acceso

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
```
---

## 💬 Ejemplos de Interacción
El Agente Topo es capaz de manejar contextos mixtos de forma fluida. Aquí tienes ejemplos reales de lo que puede responder:

* 📄 Ejemplo 1: Consulta Documental (RAG)
Usuario: "¿Cuáles son los requisitos para apartar un terreno según el reglamento interno?"

Respuesta del Agente: "Basado en los documentos proporcionados, para apartar un lote en Terrenos TOPO el cliente debe presentar una identificación oficial vigente, un comprobante de domicilio no mayor a 3 meses y cubrir el 10% del enganche inicial. (Fuente: manual_ventas_2024.pdf)."

* 🗄️ Ejemplo 2: Análisis de Base de Datos
Usuario: "¿Cuál fue el terreno con mayor costo operativo en el último trimestre?"

Respuesta del Agente: "Revisando la base de datos de costos operativos, el terreno con mayor gasto fue el Lote B-42 en la sección Norte, con un acumulado de $45,200 MXN en el último trimestre debido a movimientos de tierra."

* 📊 Ejemplo 3: Generación de Gráficos (Data Analytics)
Usuario: "Genera un gráfico con los costos operativos de todos los terrenos."

Respuesta del Agente: "¡Claro! He generado el gráfico solicitado con la distribución de los costos operativos por terreno." (El sistema despliega exitosamente en el chat una imagen dinámica de un gráfico de barras a todo color).

---


## 🚧 Dificultades y Soluciones Técnicas
Durante el desarrollo, superamos varios retos técnicos arquitectónicos:

1. Persistencia de Archivos Locales en Streamlit (Gráficos Fantasma):

Problema: El agente generaba gráficos correctamente en el backend, pero Streamlit no anclaba la imagen física al historial visual, desapareciendo al primer re-renderizado.

Solución: Implementamos rutas absolutas dinámicas con pathlib en core/config.py. En nodes.py, modificamos el agente para borrar gráficos previos, verificar en disco la creación del nuevo .png y empaquetar la ruta visual usando additional_kwargs en un AIMessage, asegurando que la interfaz de Streamlit siempre encuentre y renderice el archivo gráfico de manera persistente en la memoria del chat.

2. Infraestructura de Despliegue (Migración de OCI a Streamlit Cloud):

Problema: Restricciones de capacidad de hardware gratuito ("Out of capacity") bloquearon el despliegue de los contenedores en Oracle Cloud Infrastructure (OCI).

Solución: Realizamos un pivote arquitectónico hacia Streamlit Community Cloud. Para sortear el sistema de archivos efímero de esta plataforma, adaptamos la arquitectura asegurando el índice vectorial FAISS y el corpus documental base dentro del repositorio de control de versiones de GitHub. Además, saneamos el archivo requirements.txt para evitar conflictos con librerías nativas de Windows en el entorno Linux de la nube.

---

## 💻 Instrucciones para Ejecución Local
Si deseas correr el proyecto en tu propia máquina para realizar modificaciones o pruebas, sigue estos pasos:

1. Clonar el repositorio:
git clone [https://github.com/imannolM/agente-topo.git](https://github.com/tu-usuario/agente-topo.git)
cd agente-topo

2. Crear y activar un entorno virtual (Python 3.11 recomendado):
python -m venv .venv
* En Windows:
.venv\Scripts\activate
* En Mac/Linux:
source .venv/bin/activate

3. Instalar dependencias:
pip install -r requirements.txt

4. Configurar Variables de Entorno:
Cambia el nombre del archivo .env.example a .env (o crea uno nuevo) en la raíz del proyecto y agrega tus claves privadas:

* GROQ_API_KEY=tu_clave_aqui
* COHERE_API_KEY=tu_clave_aqui
* HOST_AIVEN=tu_host.aivencloud.com
* PORT_AIVEN=10411
* USER_AIVEN=avnadmin
* PASSWORD_AIVEN=tu_password
* DATABASE_AIVEN=defaultdb

5. Ejecutar la aplicación:
* streamlit run app.py