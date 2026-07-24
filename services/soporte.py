from pydantic import BaseModel, Field
from typing import Dict, Optional
from core.llm import llm_groq
from services.database import guardar_cita_bd

# --- FUNCIÓN LOGICA: PEDIR INFORMACIÓN / SOPORTE ---
def soporte_pedir_info(pregunta: str) -> Dict:
    # Lógica para responder cuando algo es ambiguo o fuera de contexto
    return {
        "respuesta": "Para poder ayudarte mejor en Terrenos TOPO, ¿podrías ser un poco más específico con tu consulta o indicarme con qué departamento deseas hablar?",
        "info_completada": False
    }

# --- MODELO DE EXTRACCIÓN ---
class ExtraccionCita(BaseModel):
    tiene_datos: bool = Field(description="True SOLAMENTE si el texto contiene un nombre, un teléfono y un día/fecha.")
    nombre: Optional[str] = Field(description="El nombre del cliente extraído del texto.")
    telefono: Optional[str] = Field(description="El número de teléfono extraído del texto.")     
    fecha: Optional[str] = Field(description="El día o fecha solicitada extraída del texto.")

# --- FUNCIÓN INTELIGENTE ---
def gestion_agendar_cita(texto_pregunta: str) -> dict:
    """Extrae los datos y guarda la cita, o pide los datos faltantes."""
    
    # Invocamos al LLM con salida estructurada para que busque los datos
    llm_estructurado = llm_groq.with_structured_output(ExtraccionCita)
    
    # 🌟 CORRECCIÓN: Usamos una lista de mensajes para darle un rol de sistema fuerte
    # y evitar que el LLM alucine etiquetas <function> con los acentos.
    mensajes = [
        ("system", "Eres un asistente experto en extracción de datos. Tu ÚNICA tarea es extraer el nombre, teléfono y fecha del mensaje del usuario. NUNCA devuelvas etiquetas XML como <function>. Responde exclusivamente con la estructura requerida."),
        ("human", f"Analiza el siguiente mensaje del usuario y extrae los datos para una cita: '{texto_pregunta}'")
    ]
    
    try:
        datos = llm_estructurado.invoke(mensajes)
    except Exception as e:
        print(f"❌ Error en la API de Groq (Extracción): {e}")
        return {"respuesta": "Hubo un pequeño problema técnico al leer los caracteres de tu nombre. ¿Podrías volver a escribir tus datos sin usar acentos, por favor?"}
    
    # Validamos si el usuario ya nos dio la información completa
    if datos.tiene_datos and datos.nombre and datos.telefono and datos.fecha:
        # Guardamos en la base de datos
        exito = guardar_cita_bd(datos.nombre, datos.telefono, datos.fecha)
        
        if exito:
            return {"respuesta": "¡Datos enviados con éxito! Nos comunicaremos contigo a la brevedad."}
        else:
            return {"respuesta": "Hubo un pequeño error interno al guardar tu cita. Por favor, intenta de nuevo más tarde."}
    
    # Si faltan datos, devolvemos el mensaje solicitándolos
    else:
        return {"respuesta": "¡Por supuesto! Para agendar una cita con uno de nuestros asesores de Terrenos TOPO, por favor indícame tu nombre completo, teléfono y el día de tu preferencia."}