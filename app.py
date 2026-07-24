import streamlit as st
import os
from langchain_core.messages import HumanMessage, AIMessage

# Importamos nuestro agente compilado
from agent.graph import agente_topo

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Terrenos TOPO - Asistente IA",
    page_icon="🏔️",
    layout="centered"
)

st.title("🤖 Agente Inteligente - Terrenos TOPO")

# --- INICIALIZACIÓN DEL ESTADO DE SESIÓN ---
if "messages" not in st.session_state:
    # Agregamos un saludo inicial automático
    st.session_state.messages = [
        AIMessage(content="¡Hola! Soy el Agente Inteligente de Terrenos TOPO. ¿En qué puedo ayudarte hoy?")
    ]
if "esperando_confirmacion" not in st.session_state:
    st.session_state.esperando_confirmacion = False
if "ultima_pregunta" not in st.session_state:
    st.session_state.ultima_pregunta = ""

# --- BARRA LATERAL (SIDEBAR) PARA CONFIGURACIÓN ---
with st.sidebar:
    st.header("⚙️ Configuración de Sesión")
    
    # Selector de Rol
    rol_seleccionado = st.selectbox(
        "Selecciona tu rol:",
        ["cliente", "empleado", "administrador"],
        index=0
    )
    
    # Campo de Folio
    folio_ingresado = st.text_input("Folio de Trámite (Opcional):", placeholder="Ej. TT-0101")
    
    # Botón para limpiar el chat
    if st.button("🗑️ Limpiar Conversación"):
        st.session_state.messages = [
            AIMessage(content="¡Hola! Soy el Agente Inteligente de Terrenos TOPO. ¿En qué puedo ayudarte hoy?")
        ]
        st.session_state.esperando_confirmacion = False
        st.rerun()

# --- RENDERIZADO DEL HISTORIAL DE CHAT ---
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)

# --- SISTEMA DE CONFIRMACIÓN PARA MODIFICAR DB ---
# Se activa si el agente devolvió "CONFIRMACION_REQUERIDA" en el turno anterior
if st.session_state.esperando_confirmacion:
    st.warning("⚠️ Acción Crítica: La base de datos requiere tu confirmación.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirmar Cambio", use_container_width=True):
            # Armamos el estado inyectando el true en la confirmación
            estado_confirmacion = {
                "messages": st.session_state.messages + [HumanMessage(content=st.session_state.ultima_pregunta)],
                "user_role": rol_seleccionado,
                "user_folio": folio_ingresado if folio_ingresado else None,
                "confirmacion_modificacion": True
            }
            
            with st.spinner("Aplicando cambios en la base de datos..."):
                # Ejecutamos el agente nuevamente
                resultado = agente_topo.invoke(estado_confirmacion)
                respuesta_final = resultado["messages"][-1]
                
                # Guardamos y mostramos el resultado
                st.session_state.messages.append(respuesta_final)
                st.session_state.esperando_confirmacion = False
                st.rerun()
                
    with col2:
        if st.button("❌ Cancelar", use_container_width=True):
            mensaje_cancelacion = AIMessage(content="Operación cancelada por el usuario. No se hicieron cambios en la base de datos.")
            st.session_state.messages.append(mensaje_cancelacion)
            st.session_state.esperando_confirmacion = False
            st.rerun()

# --- ENTRADA DE TEXTO DEL USUARIO ---
# Desactivamos el input si estamos esperando que el administrador presione un botón
prompt = st.chat_input("Escribe tu mensaje aquí...", disabled=st.session_state.esperando_confirmacion)

if prompt:
    # 1. Mostramos el mensaje del usuario en la pantalla
    with st.chat_message("user"):
        st.write(prompt)
    
    # 2. Guardamos la pregunta actual por si luego se requiere confirmación
    st.session_state.ultima_pregunta = prompt

    # *: Guardamos tu pregunta en la memoria visual de Streamlit DE INMEDIATO
    st.session_state.messages.append(HumanMessage(content=prompt))
    
    # 3. Anexamos al historial que LangGraph usará
    mensajes_historial = st.session_state.messages
    
    # 4. Construimos el estado inicial
    estado_inicial = {
        "messages": mensajes_historial,
        "user_role": rol_seleccionado,
        "user_folio": folio_ingresado if folio_ingresado else None,
        "confirmacion_modificacion": False
    }

    # 5. Ejecutamos el agente (Mostrando un spinner de carga)
    with st.spinner("Procesando tu solicitud..."):
        try:
            resultado = agente_topo.invoke(estado_inicial)
            respuesta_final = resultado["messages"][-1]
            accion_final = resultado.get("accion_final", "")
            grafico_generado = resultado.get("grafico_generado")
            
            # 6. Guardamos la respuesta del agente en el historial local
            st.session_state.messages.append(respuesta_final)
            
            # 7. Mostramos la respuesta en pantalla
            with st.chat_message("assistant"):
                st.write(respuesta_final.content)
                
                # --- MANEJO DE GRÁFICOS ---
                # Si el agente generó un gráfico, Streamlit lo detecta y lo dibuja
                if grafico_generado and os.path.exists(grafico_generado):
                    st.image(grafico_generado, caption="Análisis Gráfico de Terrenos TOPO")
            
            # 8. Verificamos si se activó el candado de seguridad
            if accion_final == "CONFIRMACION_REQUERIDA":
                st.session_state.esperando_confirmacion = True
                st.rerun() # Recargamos la interfaz para que aparezcan los botones
                
        except Exception as e:
            st.error(f"Ocurrió un error al procesar la solicitud: {str(e)}")