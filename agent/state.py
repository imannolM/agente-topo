from typing import TypedDict, Optional, Annotated, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# 1. Definimos AgentState, expandido solo con los roles de seguridad
class AgentState(TypedDict, total=False):
    # CRÍTICO: add_messages asegura que el historial se anexe y no se sobreescriba
    messages: Annotated[list[Any], add_messages]

    # Datos de sesión enviados por Streamlit
    user_role: str
    user_folio: Optional[str]

    # Datos de la solicitud actual
    folio_consultado: Optional[str]
    tabla_analisis: Optional[str]
    triaje: dict

    # Confirmación de modificación al administrador
    confirmacion_modificacion: bool

    # Streamlit podrá usar gráfico_generado para mostrarlo
    grafico_generado: Optional[str]

    # Resultado del agente
    respuesta: Optional[str]
    citaciones: Optional[list]
    rag_exito: bool
    accion_final: str