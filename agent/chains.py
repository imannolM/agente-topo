from pydantic import BaseModel, Field
from typing import Optional, List
from core.llm import llm_groq
from core.prompts import prompt_triaje

# 1. El modelo Pydantic
class TriajeOut(BaseModel):
    decision: Literal["CONSULTAR_DOCUMENTACION", "CONSULTAR_DB", "MODIFICAR_DB_O_DOCS", "ANALISIS_DATOS", "PEDIR_INFO", "AGENDAR_CITA"]
    urgencia: Literal["BAJA", "MEDIANA", "ALTA"]
    campos_faltantes: List[str] = Field(default_factory=list)
    # Nuevos campos para capturar qué quiere cambiar exactamente el usuario
    campo_a_modificar: Optional[str] = Field(default=None, description="El nombre de la columna o dato a cambiar (ej. estatus, costo, descripcion)")
    nuevo_valor: Optional[str] = Field(default=None, description="El nuevo valor a asignar (ej. Aprobado, 5000)")

# 2. La cadena ensamblada lista para usarse
chain_de_triaje = prompt_triaje_template | llm_groq.with_structured_output(TriajeOut)