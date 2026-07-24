from agent.state import AgentState
from utils.helpers import obtener_pregunta_del_estado

def arista_decision_triaje(state: AgentState) -> str:
    print("🔮 Decidiendo el flujo después del nodo 'triaje'...")
    tri = state["triaje"]
    decision = tri.get("decision")

    if decision == "CONSULTAR_DOCUMENTACION":
        print(" -> Ruta seleccionada: Base de Conocimiento (RAG)")
        return "rag"
    elif decision == "CONSULTAR_DB":
        print(" -> Ruta seleccionada: Consulta de datos/expedientes (MySQL)")
        return "consultar_db"
    elif decision == "MODIFICAR_DB_O_DOCS":
        print(" -> Ruta seleccionada: Modificación de registros")
        return "modificar_db"
    elif decision == "ANALISIS_DATOS":
        print(" -> Ruta seleccionada: Módulo de analítica y gráficos")
        return "analizar_datos"
    elif decision == "AGENDAR_CITA":
        print(" -> Ruta seleccionada: Agenda/Asesor humano")
        return "cita"
    else:
        print(" -> Ruta seleccionada: Pedir más información / Caso ambiguo")
        return "info"

def arista_decision_rag(state: AgentState) -> str:
    print("📝 Decidiendo el flujo después del nodo 'consultar_documentacion' (RAG)...")

    # Suponiendo que tu nodo de documentación guarda un flag 'rag_exito'
    if state.get("rag_exito"):
        print("RAG exitoso, finalizando el flujo.")
        return "fin_rag"

    # Palabras clave adaptadas al contexto inmobiliario/topográfico de Terrenos TOPO
    KEYWORDS_AGENDAR_CITA = [
        "aprobacion", "aprobar", "excepcion", "liberacion", "autorizacion",
        "autorizar", "levantamiento", "deslinde", "firma de contrato", "asesor"
    ]

    pregunta = obtener_pregunta_del_estado(state)

    if any(keyword in pregunta.lower() for keyword in KEYWORDS_AGENDAR_CITA):
        print("El RAG no bastó, pero detectamos intención de cita presencial o técnica.")
        return "cita"

    print("El RAG no encontró respuesta suficiente; solicitando aclaraciones al usuario.")
    return "info"