import re
from typing import Any

# ---------------------------------------------------------
# CONSTANTES Y CONFIGURACIONES DE PERMISOS
# ---------------------------------------------------------
ROLES_VALIDOS = {"administrador", "empleado", "cliente"}
TABLA_INVENTARIO = "bienes_raices_inventario"
# Solo estas tablas pueden cargarse para análisis desde MySQL.
TABLAS_ANALISIS_PERMITIDAS = {"ventas_analitica"}

# Tablas de análisis autorizadas para cada rol.
# Ajusta la lista al ampliar el proyecto.
PERMISOS_ANALISIS = {
    "administrador": {"ventas_analitica"},
    "empleado": {"ventas_analitica"},
    "cliente": set(),
}

# Aquí definimos los campos que serán publicos de la tabla bienes_raices_inventario
CAMPOS_PUBLICOS_INVENTARIO = (
    "clave_terreno",
    "ubicacion",
    "superficie_m2",
    "uso_suelo",
    "precio_m2",
    "precio_total",
    "estatus"
)

PERMISOS_LECTURA = {
    "administrador": "*",
    "empleado": [
        "topografia_proyectos",
        "juridico_tramites",
        "administrativo_catastral",
        TABLA_INVENTARIO,
        "ventas_analitica",
    ],
    "cliente": [TABLA_INVENTARIO],
}

# Campos que el administrador tiene permitido modificar por tabla.
CAMPOS_MODIFICABLES = {
    "topografia_proyectos": {
        "estatus",
        "costo_total",
        "anticipo",
        "restante",
        "fecha_estimada_entrega"
    },
    "juridico_tramites": {
        "estatus",
        "documentos_faltantes",
        "precio",
        "anticipo",
        "restante"
    },
    "administrativo_catastral": {
        "estatus",
        "documentos_entregados",
        "costo"
    },
    "bienes_raices_inventario": {
        "estatus",
        "precio_m2",
        "precio_total",
        "documentos_disponibles",
        "enganche_minimo",
        "socio_asignado"
    },
}

# Alias que el usuario o el LLM puede mencionar.
ALIAS_CAMPOS = {
    "estado": "estatus",
    "status": "estatus",
    "costo": "precio_total",
    "precio de venta": "precio_total",
}

PALABRAS_GRAFICO = [
        "gráfico",
        "grafico",
        "gráfica",
        "grafica",
        "histograma",
        "visualización",
        "visualizacion",
        "diagrama",
        "barras",
        "pastel",
        "líneas",
        "lineas",
    ]


# ---------------------------------------------------------
# FUNCIONES DE APOYO
# ---------------------------------------------------------

def normalizar_rol(rol: str) -> str:
    rol_normalizado = rol.strip().lower()

    if rol_normalizado not in ROLES_VALIDOS:
        raise ValueError(f"Rol no autorizado: {rol_normalizado}")

    return rol_normalizado


def mapear_folio_a_tabla(texto_pregunta: str):
    """
    Analiza el texto buscando patrones como TOP-00001, JUR-00997, VTA-00995, etc.
    Retorna: (nombre_tabla, columna_id, folio_completo) o (None, None, None)
    """
    patron = r'\b([A-Z]{2,4}-\d{4,5})\b'
    match = re.search(patron, texto_pregunta.upper())

    if not match:
        return None, None, None

    folio_completo = match.group(1)
    prefijo = folio_completo.split('-')[0]

    MAPEO_PREFIJOS = {
        "TOP": ("topografia_proyectos", "id_proyecto"),
        "JUR": ("juridico_tramites", "id_tramite"),
        "ADM": ("administrativo_catastral", "id_tramite"),
        "TT": ("bienes_raices_inventario", "clave_terreno"),
    }

    tabla, columna_id = MAPEO_PREFIJOS.get(prefijo, (None, None))
    return tabla, columna_id, folio_completo


def validar_acceso_tabla(
    rol: str,
    tabla: str,
    folio_pregunta: str = None,
    folio_usuario_autenticado: str = None,
) -> bool:
    """Valida el acceso de lectura según rol, tabla y folio autenticado."""
    rol = normalizar_rol(rol)

    if rol in {"administrador", "admin"}:
        return True

    if tabla == TABLA_INVENTARIO:
        return True

    if rol == "cliente":
        return bool(
            folio_pregunta
            and folio_usuario_autenticado
            and folio_pregunta == folio_usuario_autenticado
        )

    tablas_permitidas = PERMISOS_LECTURA.get(rol, [])
    return tabla in tablas_permitidas


def obtener_campo_autorizado(tabla: str, campo_solicitado: str | None) -> str | None:
    """Devuelve una columna permitida o None si no está autorizada."""
    if not campo_solicitado:
        return None

    campo_normalizado = campo_solicitado.strip().lower()
    campo_bd = ALIAS_CAMPOS.get(campo_normalizado, campo_normalizado)

    if campo_bd in CAMPOS_MODIFICABLES.get(tabla, set()):
        return campo_bd

    return None


def obtener_pregunta_del_estado(state: Any) -> str:
    """Obtiene la última pregunta del usuario desde messages."""
    messages = state.get("messages", [])

    if not messages:
        raise ValueError("El estado no contiene mensajes para procesar.")

    ultimo_mensaje = messages[-1]

    if isinstance(ultimo_mensaje, tuple):
        return str(ultimo_mensaje[1])

    if hasattr(ultimo_mensaje, "content"):
        return str(ultimo_mensaje.content)

    return str(ultimo_mensaje)