# --- FUNCIÓN LOGICA: PEDIR INFORMACIÓN / SOPORTE ---
def soporte_pedir_info(pregunta: str) -> Dict:
    # Lógica para responder cuando algo es ambiguo o fuera de contexto
    return {
        "respuesta": "Para poder ayudarte mejor en Terrenos TOPO, ¿podrías ser un poco más específico con tu consulta o indicarme con qué departamento deseas hablar?",
        "info_completada": False
    }

# --- FUNCIÓN LOGICA: AGENDAR CITA ---
def gestion_agendar_cita(pregunta: str) -> Dict:
    # Nota: Aquí conectaremos con Google Calendar o una tabla de citas en el Chat 5
    return {
        "respuesta": "¡Por supuesto! Para agendar una cita con uno de nuestros asesores de Terrenos TOPO, por favor indícame tu nombre completo, teléfono y el día de tu preferencia.",
        "cita_agendada": False
    }