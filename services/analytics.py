import pandas as pd
import matplotlib.pyplot as plt
from langchain_core.tools import tool
from sqlalchemy import create_engine
import urllib.parse
import os

# Importamos credenciales y rutas desde nuestro core
from core.config import (
    HOST_AIVEN,
    PORT_AIVEN,
    USER_AIVEN,
    PASSWORD_AIVEN,
    DATABASE_AIVEN,
    CA_CERT_PATH,
    DATA_DIR
)

# Definimos la ruta segura absoluta donde se guardará el gráfico generado
RUTA_GRAFICO = DATA_DIR / "grafico_analisis.png"


def extraer_df_desde_mysql(nombre_tabla: str) -> pd.DataFrame:
    """Carga únicamente tablas aprobadas para análisis."""
    if nombre_tabla not in TABLAS_ANALISIS_PERMITIDAS:
        raise ValueError(f"La tabla '{nombre_tabla}' no está autorizada para análisis.")

    usuario = USER_AIVEN
    password = urllib.parse.quote_plus(PASSWORD_AIVEN)
    host = HOST_AIVEN
    puerto = int(PORT_AIVEN)
    db = DATABASE_AIVEN
    ssl_ca = str(CA_CERT_PATH)

    conexion_uri = (
        f"mysql+pymysql://{usuario}:{password}@{host}:{puerto}/{db}"
        f"?ssl_ca={ssl_ca}"
    )

    engine = create_engine(conexion_uri)

    # El nombre ya fue validado contra una lista cerrada.
    return pd.read_sql_table(nombre_tabla, con=engine)


def crear_herramientas_analisis(df: pd.DataFrame):
    """Crea herramientas sin ejecución arbitraria de código."""
    columnas_validas = set(df.columns)

    def validar_columna(columna: str) -> str:
        columna = columna.strip()

        if columna not in columnas_validas:
            disponibles = ", ".join(sorted(columnas_validas))
            raise ValueError(
                f"La columna '{columna}' no existe. Columnas disponibles: {disponibles}"
            )

        return columna

    @tool
    def informacion_dataset() -> str:
        """Muestra columnas, tipos de datos y una muestra de los primeros registros."""
        return (
            f"Columnas y tipos:\n{df.dtypes.to_string()}\n\n"
            f"Primeros registros:\n{df.head(5).to_string()}"
        )

    @tool
    def resumen_estadistico() -> str:
        """Genera un resumen estadístico de todo el conjunto de datos."""
        return df.describe(include="all").fillna("Sin dato").to_string()

    @tool
    def conteo_por_categoria(columna: str) -> str:
        """Cuenta registros agrupados por una columna categórica."""
        try:
            columna = validar_columna(columna)

            conteo = (
                df[columna]
                .fillna("Sin dato")
                .value_counts()
                .head(20)
            )

            return conteo.to_string()

        except ValueError as error:
            return str(error)

    @tool
    def generar_grafico(columna: str) -> str:
        """
        Genera un gráfico seguro para una columna.
        Si es numérica, crea un histograma; de otro modo, una gráfica de barras.
        """
        try:
            columna = validar_columna(columna)

            fig, ax = plt.subplots(figsize=(9, 5))

            if pd.api.types.is_numeric_dtype(df[columna]):
                df[columna].dropna().plot(
                    kind="hist",
                    bins=15,
                    ax=ax,
                    edgecolor="black",
                )
                ax.set_title(f"Distribución de {columna}")
                ax.set_xlabel(columna)
                ax.set_ylabel("Frecuencia")
            else:
                conteo = df[columna].fillna("Sin dato").value_counts().head(10)
                conteo.plot(kind="bar", ax=ax)
                ax.set_title(f"Registros por {columna}")
                ax.set_xlabel(columna)
                ax.set_ylabel("Cantidad")
                plt.xticks(rotation=45, ha="right")

            plt.tight_layout()

            # Guardado en ruta dinámica para Streamlit
            fig.savefig(str(RUTA_GRAFICO), bbox_inches="tight")
            plt.close(fig)

            return f"Gráfico generado correctamente en '{RUTA_GRAFICO}'."

        except ValueError as error:
            return str(error)

    return [
        informacion_dataset,
        resumen_estadistico,
        conteo_por_categoria,
        generar_grafico,
    ]

def resolver_tabla_analisis(state: dict) -> str:
    """Obtiene y valida la tabla de análisis solicitada."""
    # Importamos normalizar_rol desde nuestros helpers (lo crearemos pronto)
    from utils.helpers import normalizar_rol
    
    rol = normalizar_rol(state.get("user_role", "cliente"))

    # Si no se especifica tabla, el análisis general se realiza sobre ventas.
    tabla_solicitada = state.get("tabla_analisis", "ventas_analitica")

    tablas_autorizadas = PERMISOS_ANALISIS.get(rol, set())

    if tabla_solicitada not in tablas_autorizadas:
        raise PermissionError(
            "Tu rol no tiene permiso para analizar esta información."
        )

    return tabla_solicitada