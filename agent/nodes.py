import json
import re
from pydantic import BaseModel, Field
from typing import Optional, List

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain.agents import create_react_agent, AgentExecutor

# Importamos nuestro estado, llm, prompts y utilidades
from agent.chains import chain_de_triaje
from agent.state import AgentState
from services.soporte import soporte_pedir_info, gestion_agendar_cita
from core.llm import llm_groq
from core.prompts import obtener_prompt_react
from utils.helpers import (
    obtener_pregunta_del_estado, 
    normalizar_rol, 
    mapear_folio_a_tabla
)

# Importamos los servicios pesados
from services.rag import busqueda_de_respuestas_RAG
from services.database import consulta_base_de_datos, modificacion_base_de_datos
from services.analytics import extraer_df_desde_mysql, crear_herramientas_analisis, resolver_tabla_analisis


# --- NODO: TRIAJE ---
def nodo_triaje(state: AgentState) -> dict:
    print("🔮 Ejecutando nodo triaje...")
    texto_pregunta = obtener_pregunta_del_estado(state)
    rol_usuario = normalizar_rol(state.get("user_role", "cliente"))

    print(f"💬 Pregunta procesada: '{texto_pregunta}' | Rol detectado: {rol_usuario}")

    try:
        salida = chain_de_triaje.invoke({
            "user_role": rol_usuario,
            "pregunta": texto_pregunta
        })
        return {"triaje": salida.model_dump()}
    except Exception as e:
        print(f"⚠️ Error en triaje, usando fallback PEDIR_INFO: {e}")
        return {
            "triaje": {
                "decision": "PEDIR_INFO",
                "urgencia": "BAJA",
                "campos_faltantes": [],
                "campo_a_modificar": None,
                "nuevo_valor": None
            }
        }


# --- NODO: CONSULTAR DOCUMENTACIÓN (RAG) ---
def nodo_consultar_documentacion(state: AgentState) -> dict:
    print("📚 Ejecutando nodo consultar_documentacion (RAG)...")
    texto_pregunta = obtener_pregunta_del_estado(state)

    respuesta_RAG = busqueda_de_respuestas_RAG(texto_pregunta)

    # CRÍTICO: Añadimos messages para que Streamlit pueda renderizar la respuesta
    update = {
        "messages": [AIMessage(content=respuesta_RAG["respuesta"])],
        "respuesta": respuesta_RAG["respuesta"],
        "citaciones": respuesta_RAG["citaciones"],
        "rag_exito": respuesta_RAG["documentos_encontrados"]
    }

    if respuesta_RAG["documentos_encontrados"]:
        update["accion_final"] = "DOCUMENTACION_RESUELTA"
    else:
        update["accion_final"] = "PEDIR_INFO"

    return update


# --- NODO: CONSULTAR DB ---
def nodo_consultar_db(state: AgentState) -> dict:
    print("🗄️ Ejecutando nodo consultar_db...")
    texto_pregunta = obtener_pregunta_del_estado(state)
    rol = state.get("user_role", "cliente")
    folio_sesion = state.get("user_folio")

    tabla, col_id, folio_detectado = mapear_folio_a_tabla(texto_pregunta)
    if folio_detectado:
        print(f"📌 Folio detectado para consulta: {folio_detectado}")

    resultado_db = consulta_base_de_datos(texto_pregunta, user_role=rol, user_folio=folio_sesion)
    
    # Formateamos la respuesta en texto para el usuario
    respuesta_texto = f"Aquí tienes la información solicitada:\n{resultado_db}"

    return {
        "messages": [AIMessage(content=respuesta_texto)],
        "respuesta": respuesta_texto,
        "accion_final": "CONSULTA_DB_PROCESADA",
        "folio_consultado": folio_detectado
    }


# --- NODO: MODIFICAR DB O DOCS ---
def nodo_modificar_db_o_docs(state: AgentState) -> dict:
    print("✍️ Ejecutando nodo modificar_db_o_docs...")
    texto_pregunta = obtener_pregunta_del_estado(state)
    rol = state.get("user_role", "cliente")

    _, _, folio_tramite = mapear_folio_a_tabla(texto_pregunta)
    if not folio_tramite:
        match = re.search(r'\b([A-Z]{2,4}-\d{4,5})\b', texto_pregunta.upper())
        if match:
            folio_tramite = match.group(1)

    triaje_data = state.get("triaje", {})
    campo_mod = triaje_data.get("campo_a_modificar")
    nuevo_val = triaje_data.get("nuevo_valor")

    datos_modificacion = {
        "folio": folio_tramite,
        "campo_a_modificar": campo_mod,
        "nuevo_valor": nuevo_val
    }

    resultado_modificacion = modificacion_base_de_datos(
        texto_pregunta,
        user_role=rol,
        datos_modificacion=datos_modificacion,
        confirmada_por_admin=state.get("confirmacion_modificacion", False),
    )

    update = {
        "messages": [AIMessage(content=resultado_modificacion["respuesta"])],
        "respuesta": resultado_modificacion["respuesta"],
        "folio": folio_tramite
    }

    if resultado_modificacion.get("requiere_confirmacion"):
        update["accion_final"] = "CONFIRMACION_REQUERIDA"
    elif resultado_modificacion["db_exito"]:
        update["accion_final"] = "MODIFICACION_EXITOSA"
    else:
        update["accion_final"] = "ERROR_PERMISOS"

    return update


# --- NODO: ANÁLISIS DE DATOS ---
def nodo_analisis_datos(state: AgentState) -> dict:
    print("📊 Ejecutando nodo de análisis de datos...")
    texto_pregunta = obtener_pregunta_del_estado(state)

    try:
        nombre_tabla = resolver_tabla_analisis(state)
    except PermissionError as error:
        return {
            "messages": [AIMessage(content=str(error))],
            "respuesta": str(error),
            "accion_final": "ACCESO_ANALISIS_DENEGADO",
        }

    try:
        df = extraer_df_desde_mysql(nombre_tabla)
    except Exception as error:
        print(f"\n❌ [DEBUG] ERROR REAL EN MYSQL/PANDAS: {error}\n")
        return {
            "messages": [AIMessage(content="No fue posible cargar los datos para el análisis.")],
            "respuesta": "No fue posible cargar los datos para el análisis.",
            "accion_final": "ANALISIS_FALLIDO",
        }

    herramientas = crear_herramientas_analisis(df)
    texto_normalizado = texto_pregunta.lower()

    PALABRAS_GRAFICO = ["gráfico", "grafico", "gráfica", "grafica", "histograma", "visualización", "visualizacion", "diagrama", "barras", "pastel", "líneas", "lineas"]
    solicita_grafico = any(palabra in texto_normalizado for palabra in PALABRAS_GRAFICO)

    if not solicita_grafico:
        herramientas = [h for h in herramientas if h.name != "generar_grafico"]

    prompt = obtener_prompt_react(nombre_tabla)

    agente = create_react_agent(llm_groq, herramientas, prompt)
    ejecutor = AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )

    resultado = ejecutor.invoke({"input": texto_pregunta})

    se_genero_grafico = any(
        accion.tool == "generar_grafico"
        for accion, _ in resultado.get("intermediate_steps", [])
    )

    return {
        "messages": [AIMessage(content=resultado["output"])],
        "respuesta": resultado["output"],
        "accion_final": "ANALISIS_COMPLETADO",
        "grafico_generado": "grafico_analisis.png" if se_genero_grafico else None,
    }

# --- NODO: PEDIR INFO ---
def nodo_pedir_info(state: AgentState) -> dict:
    print("💬 Ejecutando nodo pedir_info...")
    texto_pregunta = obtener_pregunta_del_estado(state)
    resultado_soporte = soporte_pedir_info(texto_pregunta)

    return {
        # 🌟 CORRECCIÓN: Agregamos el AIMessage a la lista
        "messages": [AIMessage(content=resultado_soporte["respuesta"])],
        "respuesta": resultado_soporte["respuesta"],
        "accion_final": "PEDIR_INFO_CLIENTE"
    }

# --- NODO: AGENDAR CITA ---
def nodo_agendar_cita(state: AgentState) -> dict:
    print("📅 Ejecutando nodo agendar_cita...")
    texto_pregunta = obtener_pregunta_del_estado(state)
    resultado_cita = gestion_agendar_cita(texto_pregunta)

    return {
        # 🌟 CORRECCIÓN: Agregamos el AIMessage a la lista
        "messages": [AIMessage(content=resultado_cita["respuesta"])],
        "respuesta": resultado_cita["respuesta"],
        "accion_final": "SOLICITAR_DATOS_CITA"
    }