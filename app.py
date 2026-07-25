import streamlit as st
import os
from langchain_core.messages import HumanMessage, AIMessage

# Importamos nuestro agente compilado
from agent.graph import agente_topo
# Importamos la función para agregar documentos (Punto 2)
from services.rag import agregar_documento_rag

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Terrenos TOPO - Asistente IA",
    # 🌟 MODIFICACIÓN (Punto 2: Ícono de página como topo robot)
    page_icon="🤖", 
    layout="centered"
)

# 🌟 MODIFICACIÓN (Punto 1 y 2: Avatares Visuales)
# Definimos los avatares para el chat que evocan los diseños generados
AVATAR_ASISTENTE = "🤖" # Estilo Inteligente-Robot
AVATAR_USUARIO = "👤" # Estilo Persona minimalista

# --- INICIALIZACIÓN DEL ESTADO DE SESIÓN ---
# ... (Bloque de inicialización de mensajes y confirmación igual) ...
if "messages" not in st.session_state:
    st.session_state.messages = [
        AIMessage(content="¡Hola! Soy el Agente Inteligente de Terrenos TOPO. ¿En qué puedo ayudarte hoy?")
    ]
if "esperando_confirmacion" not in st.session_state:
    st.session_state.esperando_confirmacion = False
if "ultima_pregunta" not in st.session_state:
    st.session_state.ultima_pregunta = ""
# VARIABLES DE AUTENTICACIÓN
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = "cliente" # Todos entran como cliente por defecto


# --- 🌟 TÍTULO PRINCIPAL (Logo Integrado) ---
if os.path.exists("logo_topo.png"):
    # Puedes ajustar el width (ej. 300, 400, 500) según qué tan grande lo quieras
    st.image("logo_topo.png", width=450)


# --- 🌟 NUEVO: SECCIÓN DE BIENVENIDA DINÁMICA (Punto 3) ---
# Esta sección muestra la guía de usuario dependiendo del Rol actual.
with st.container():
    rol_actual = st.session_state.rol_usuario.upper()
    
    if st.session_state.rol_usuario == "cliente":
        st.markdown("""
        ### ¡Bienvenido a Terrenos TOPO! 🏔️
        Soy tu Asistente Inteligente. Mi objetivo es ayudarte a resolver tus dudas sobre el sector inmobiliario y nuestros servicios.
        
        **¿Qué puedes hacer como CLIENTE?**
        * 🔎 **Consultar Inventario:** Pregunta por terrenos disponibles en diferentes zonas o presupuestos.
        * 📝 **Información General:** Consulta procesos de compra, requisitos jurídicos y políticas de la empresa.
        * 💰 **Costos:** Pregunta por los costos generales de servicios como levantamientos topográficos.
        * 📅 **Agendar Cita:** Solicita hablar con un asesor humano proporcionando tus datos básicos.
        
        *Escribe tu consulta abajo para comenzar.*
        """)
    elif st.session_state.rol_usuario == "empleado":
        st.markdown(f"""
        ### Portal del Empleado Activo 🛠️
        Estás autenticado como: **{rol_actual}**. Tienes acceso a herramientas avanzadas para agilizar tu trabajo.
        
        **Capacidades de EMPLEADO:**
        * 🗄️ **Consulta Detallada:** Accede al estado completo de folios jurídicos, administrativos o topográficos.
        * 📅 **Ver Agenda:** Revisa el registro de citas programadas por los clientes.
        * 📚 **Análisis RAG:** Consulta la documentación interna de la empresa de forma inteligente.
        * 📊 **Estadísticas:** (Si está configurado) Consulta métricas generales de ventas.
        """)
    elif st.session_state.rol_usuario == "administrador":
        st.markdown(f"""
        ### Panel de ADMINISTRADOR Activo 🏗️
        Estás autenticado como: **{rol_actual}**. Control total del sistema activo.
        
        **Capacidades de ADMINISTRADOR:**
        * ✅ **Confirmar Modificaciones:** Aprueba cambios críticos en el estado de los folios (disponibilidad, documentos).
        * 📚 **Actualizar RAG:** Sube nuevos PDFs en la barra lateral para entrenar al agente de inmediato.
        * 📊 **Analítica Gráfica:** Solicita gráficos de precios y ventas para toma de decisiones.
        * 🔐 **Seguridad:** Todas las funciones de empleado más control de auditoría.
        """)
st.divider()


# --- BARRA LATERAL (SIDEBAR) (Punto 1: Logo al inicio) ---
with st.sidebar:
    # 🌟 Punto 1: Logo al inicio de la barra lateral
    if os.path.exists("logo_topo.png"):
        st.image("logo_topo.png", use_container_width=True)
    st.header("⚙️ Panel de Control")
    
    # ... (Resto del bloque de Login igual) ...
    if not st.session_state.autenticado:
        st.info("Ingresaste como **Cliente**. Si eres parte del equipo, inicia sesión.")
        with st.form("login_form"):
            usuario = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit_login = st.form_submit_button("Ingresar")
            
            if submit_login:
                # Diccionario de credenciales (admin/admin123, empleado/emp123)
                if usuario == "admin" and password == "admin123":
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "administrador"
                    st.rerun()
                elif usuario == "empleado" and password == "emp123":
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "empleado"
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    else:
        st.success(f"Sesión activa: **{st.session_state.rol_usuario.upper()}**")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.autenticado = False
            st.session_state.rol_usuario = "cliente"
            st.rerun()

    st.divider()
    # ... (Campo de Folio y botón Limpiar igual) ...
    folio_ingresado = st.text_input("Folio de Trámite (Opcional):", placeholder="Ej. TT-0101")
    if st.button("🗑️ Limpiar Conversación"):
        st.session_state.messages = [
            AIMessage(content="¡Hola! Soy el Agente Inteligente de Terrenos TOPO. ¿En qué puedo ayudarte hoy?")
        ]
        st.session_state.esperando_confirmacion = False
        st.rerun()

    # --- ZONA EXCLUSIVA PARA EL ADMINISTRADOR (Punto 2) ---
    if st.session_state.rol_usuario == "administrador":
        st.divider()
        st.subheader("📚 Gestión de Conocimiento (RAG)")
        archivo_subido = st.file_uploader("Agregar nuevo documento oficial (PDF)", type=["pdf"])
        
        if archivo_subido is not None:
            if st.button("Subir e Integrar al Sistema"):
                with st.spinner("Procesando y entrenando a la IA con el nuevo documento..."):
                    # Extraemos los bytes y el nombre
                    bytes_data = archivo_subido.getvalue()
                    nombre_archivo = archivo_subido.name
                    
                    # Llamamos a nuestra función de RAG
                    exito = agregar_documento_rag(bytes_data, nombre_archivo)
                    
                    if exito:
                        st.success(f"¡'{nombre_archivo}' agregado con éxito! El agente ya puede consultarlo.")
                    else:
                        st.error("Ocurrió un error al procesar el documento.")

# --- RENDERIZADO DEL HISTORIAL DE CHAT ---
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user", avatar=AVATAR_USUARIO):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant", avatar=AVATAR_ASISTENTE):
            st.write(msg.content)
            
            # 🌟 NUEVO: Buscar si este mensaje en particular tiene un gráfico asociado en su memoria
            grafico_memoria = msg.additional_kwargs.get("grafico_generado")
            if grafico_memoria and os.path.exists(grafico_memoria):
                st.image(grafico_memoria, caption="Análisis Gráfico de Terrenos TOPO")

# --- (SISTEMA DE CONFIRMACIÓN igual) ---
if st.session_state.esperando_confirmacion:
    # ... (Bloque de confirmación/cancelar igual) ...
    st.warning("⚠️ Acción Crítica: La base de datos requiere tu confirmación.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirmar Cambio", use_container_width=True):
            estado_confirmacion = {
                "messages": st.session_state.messages,
                "user_role": st.session_state.rol_usuario,
                "user_folio": folio_ingresado if folio_ingresado else None,
                "confirmacion_modificacion": True
            }
            with st.spinner("Aplicando cambios en la base de datos..."):
                resultado = agente_topo.invoke(estado_confirmacion)
                respuesta_final = resultado["messages"][-1]
                st.session_state.messages.append(respuesta_final)
                st.session_state.esperando_confirmacion = False
                st.rerun()
    with col2:
        if st.button("❌ Cancelar", use_container_width=True):
            mensaje_cancelacion = AIMessage(content="Operación cancelada por el usuario. No se hicieron cambios en la base de datos.")
            st.session_state.messages.append(mensaje_cancelacion)
            st.session_state.esperando_confirmacion = False
            st.rerun()

# --- ENTRADA DE TEXTO DEL USUARIO (igual pero ajustando la memoria visual) ---
prompt = st.chat_input("Escribe tu mensaje aquí...", disabled=st.session_state.esperando_confirmacion)

if prompt:
    # 🌟 Punto 2: Avatar de Persona minimalista al escribir
    with st.chat_message("user", avatar=AVATAR_USUARIO):
        st.write(prompt)
    st.session_state.ultima_pregunta = prompt
    st.session_state.messages.append(HumanMessage(content=prompt))
    mensajes_historial = st.session_state.messages
    
    estado_inicial = {
        "messages": mensajes_historial,
        "user_role": st.session_state.rol_usuario,
        "user_folio": folio_ingresado if folio_ingresado else None,
        "confirmacion_modificacion": False
    }

    with st.spinner("Procesando tu solicitud..."):
        try:
            resultado = agente_topo.invoke(estado_inicial)
            respuesta_final = resultado["messages"][-1]
            accion_final = resultado.get("accion_final", "")
            grafico_generado = resultado.get("grafico_generado")
            
            # 🌟 NUEVO: Pegar la ruta del gráfico a los metadatos del mensaje
            if grafico_generado:
                respuesta_final.additional_kwargs["grafico_generado"] = grafico_generado
                
            # Guardamos el mensaje (que ahora incluye el texto y, opcionalmente, la ruta del gráfico)
            st.session_state.messages.append(respuesta_final)
            
            with st.chat_message("assistant", avatar=AVATAR_ASISTENTE):
                st.write(respuesta_final.content)
                if grafico_generado and os.path.exists(grafico_generado):
                    st.image(grafico_generado, caption="Análisis Gráfico de Terrenos TOPO")
            
            if accion_final == "CONFIRMACION_REQUERIDA":
                st.session_state.esperando_confirmacion = True
                st.rerun()
                
        except Exception as e:
            st.error(f"Ocurrió un error al procesar la solicitud: {str(e)}")