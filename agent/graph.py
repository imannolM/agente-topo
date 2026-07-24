from langgraph.graph import StateGraph, START, END

# Importamos nuestro Estado
from agent.state import AgentState

# Importamos nuestros Nodos
from agent.nodes import (
    nodo_triaje,
    nodo_consultar_documentacion,
    nodo_consultar_db,
    nodo_modificar_db_o_docs,
    nodo_analisis_datos,
    nodo_pedir_info,
    nodo_agendar_cita
)

# Importamos nuestras reglas de enrutamiento (Edges)
from agent.edges import arista_decision_triaje, arista_decision_rag

def compilar_agente():
    """
    Construye y compila el flujo de trabajo (workflow) del agente Terrenos TOPO.
    Retorna el agente compilado listo para invocarse.
    """

    # 1. Inicializamos el grafo con nuestro estado definido
    workflow = StateGraph(AgentState)

    # 1. Registro de todos tus Nodos del sistema
    workflow.add_node("triaje", nodo_triaje)
    workflow.add_node("consultar_documentacion", nodo_consultar_documentacion)
    workflow.add_node("consultar_db", nodo_consultar_db)
    workflow.add_node("modificar_db", nodo_modificar_db_o_docs)
    workflow.add_node("analisis_datos", nodo_analisis_datos) # El nuevo nodo con las 4 tools
    workflow.add_node("pedir_info", nodo_pedir_info)
    workflow.add_node("agendar_cita", nodo_agendar_cita)

    # Punto de entrada obligatorio
    workflow.set_entry_point("triaje")

    # 2. Aristas Condicionales desde el Triaje
    workflow.add_conditional_edges(
        "triaje",
        arista_decision_triaje,
        {
            "rag": "consultar_documentacion",
            "consultar_db": "consultar_db",
            "modificar_db": "modificar_db",
            "analizar_datos": "analisis_datos",  # Enlace directo al módulo de analítica
            "cita": "agendar_cita",
            "info": "pedir_info"
        }
    )

    # 3. Aristas Condicionales desde el RAG (Siguiendo tu estructura del curso)
    workflow.add_conditional_edges(
        "consultar_documentacion",
        arista_decision_rag,
        {
            "ok": END,                  # Si el RAG contestó bien, termina
            "cita": "agendar_cita",     # Si falló pero quiere cita, va al nodo cita
            "info": "pedir_info"        # Si falló por completo, pide más contexto
        }
    )

    # 4. Los demás nodos terminan directo el flujo al ejecutarse
    workflow.add_edge("consultar_db", END)
    workflow.add_edge("modificar_db", END)
    workflow.add_edge("analisis_datos", END) # Tu nuevo flujo de datos termina limpio aquí
    workflow.add_edge("pedir_info", END)
    workflow.add_edge("agendar_cita", END)

    # Compilación final
    agente_compilado = workflow.compile()
    return agente_compilado

# Instanciamos el agente de forma global para que app.py solo tenga que importarlo
agente_topo = compilar_agente()