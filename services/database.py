import mysql.connector

# Importamos las credenciales desde nuestro módulo central en lugar de userdata.get()
from core.config import (
    HOST_AIVEN,
    PORT_AIVEN,
    USER_AIVEN,
    PASSWORD_AIVEN,
    DATABASE_AIVEN,
    CA_CERT_PATH
)

# NOTA: Asegúrate de importar o definir aquí las constantes y funciones auxiliares 
# que usas en este archivo (ej. TABLA_INVENTARIO, CAMPOS_PUBLICOS_INVENTARIO, 
# mapear_folio_a_tabla, normalizar_rol, etc.)

def obtener_conexion_db():
    return mysql.connector.connect(
        host=HOST_AIVEN,
        port=PORT_AIVEN,
        user=USER_AIVEN,
        password=PASSWORD_AIVEN,
        database=DATABASE_AIVEN,
        ssl_ca=str(CA_CERT_PATH) # Usamos la ruta dinámica
    )

# Esta función se encarga de insertar un registro limpio cada vez que el socio pida un cambio
def crear_solicitud_pendiente(rol: str, folio: str, campo: str, valor: str, peticion_original: str) -> dict:
    """
    Guarda la petición de modificación en la tabla 'administrativo_solicitudes'
    para que el Administrador la revise posteriormente.
    """
    print(f"📝 Registrando nueva solicitud de modificación para el folio {folio}...")
    try:
        conexion = obtener_conexion_db()
        with conexion.cursor() as cursor:
            sql = """
                INSERT INTO administrativo_solicitudes
                (rol_solicitante, folio_afectado, campo_modificar, nuevo_valor, peticion_original)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (rol, folio, campo, valor, peticion_original))
            conexion.commit()

        conexion.close()
        return {
            "exito": True,
            "mensaje": f"Tu solicitud para modificar el folio '{folio}' ha sido registrada exitosamente. Un Administrador revisará el cambio sugerido ({campo} -> {valor}) a la brevedad."
        }
    except Exception as e:
        print(f"❌ Error al crear solicitud en MySQL: {e}")
        return {
            "exito": False,
            "mensaje": "Hubo un error interno al intentar enviar tu solicitud de modificación."
        }


def consulta_base_de_datos(texto_pregunta: str, user_role: str, user_folio: str = None):
    """
    Herramienta para consultar datos mediante introspección del folio.
    """
    # 1. Identificar tabla y folio de forma dinámica
    tabla, columna_id, folio_completo = mapear_folio_a_tabla(texto_pregunta)

    rol = normalizar_rol(user_role)

    # Caso especial: consulta pública al catálogo de Bienes Raíces
    texto_normalizado = texto_pregunta.lower()

    if not tabla and any(
        termino in texto_normalizado
        for termino in [
            "bienes raíces",
            "bienes raices",
            "propiedades",
            "terrenos en venta"
        ]
    ):
        tabla = TABLA_INVENTARIO
        columna_id = None

    if not tabla:
        return (
            "No logré identificar la propiedad o trámite al que haces referencia "
            "en tu consulta. Por favor provee un folio válido (Ej: TOP-00001)."
        )

    # 2. Validar Seguridad y Roles
    if not validar_acceso_tabla(rol, tabla, folio_completo, user_folio):
        return f"Acceso Denegado: Tu rol de '{user_role}' no tiene permisos para consultar la tabla '{tabla}' o el folio especificado no te pertenece."

    # 3. Conexión a la DB (Aiven MySQL)
    try:
        conexion = obtener_conexion_db()
        cursor = conexion.cursor(dictionary=True)

        columnas_publicas_sql = ", ".join(
            f"`{columna}`" for columna in CAMPOS_PUBLICOS_INVENTARIO
        )

        # Cliente: inventario público, solo campos comerciales y terrenos disponibles.
        if tabla == TABLA_INVENTARIO and rol == "cliente":
            sql = f"""
                SELECT {columnas_publicas_sql}
                FROM `{TABLA_INVENTARIO}`
                WHERE LOWER(TRIM(`estatus`)) = %s
            """
            parametros = ["disponible"]

            if columna_id and folio_completo:
                sql += f" AND `{columna_id}` = %s"
                parametros.append(folio_completo)

            sql += " LIMIT 10"
            cursor.execute(sql, tuple(parametros))

        elif columna_id and folio_completo:
            sql = f"SELECT * FROM `{tabla}` WHERE `{columna_id}` = %s"
            cursor.execute(sql, (folio_completo,))

        else:
            sql = f"SELECT * FROM `{tabla}` LIMIT 10"
            cursor.execute(sql)

        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()

        if not resultados:
            return f"No se encontraron registros en la tabla '{tabla}' con el identificador provisto."

        return str(resultados)

    except Exception as e:
        return f"Error al ejecutar la consulta dinámica: {str(e)}"


def modificacion_base_de_datos(
    pregunta: str,
    user_role: str,
    datos_modificacion: dict | None = None,
    confirmada_por_admin: bool = False,
) -> dict:
    """Gestiona solicitudes y modificaciones seguras en la base de datos."""
    rol = normalizar_rol(user_role)
    datos_modificacion = datos_modificacion or {}

    folio_target = datos_modificacion.get("folio")
    campo_solicitado = datos_modificacion.get("campo_a_modificar")
    nuevo_valor = datos_modificacion.get("nuevo_valor")

    if not folio_target or not campo_solicitado or not nuevo_valor:
        return {
            "respuesta": (
                "Necesito el folio, el campo que deseas modificar y el nuevo valor "
                "para registrar o realizar el cambio."
            ),
            "db_exito": False,
        }

    tabla, columna_id, folio_completo = mapear_folio_a_tabla(folio_target)

    if not tabla or not columna_id:
        return {
            "respuesta": "No pude identificar una tabla válida para el folio indicado.",
            "db_exito": False,
        }

    campo = obtener_campo_autorizado(tabla, campo_solicitado)

    if not campo:
        return {
            "respuesta": (
                f"El campo '{campo_solicitado}' no está autorizado para modificarse "
                "en este registro."
            ),
            "db_exito": False,
        }

    if rol == "empleado":
        resultado = crear_solicitud_pendiente(
            rol=rol,
            folio=folio_completo,
            campo=campo,
            valor=str(nuevo_valor),
            peticion_original=pregunta,
        )
        return {
            "respuesta": resultado["mensaje"],
            "db_exito": resultado["exito"],
        }

    if rol not in {"administrador", "admin"}:
        return {
            "respuesta": "No tienes permisos para modificar registros ni generar solicitudes.",
            "db_exito": False,
        }

    if not confirmada_por_admin:
        return {
            "respuesta": (
                f"Confirmación requerida: se modificará '{campo}' del folio "
                f"'{folio_completo}' al valor '{nuevo_valor}'."
            ),
            "db_exito": False,
            "requiere_confirmacion": True,
        }

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion_db()
        cursor = conexion.cursor()

        sql = f"""
            UPDATE `{tabla}`
            SET `{campo}` = %s
            WHERE `{columna_id}` = %s
        """

        cursor.execute(sql, (str(nuevo_valor), folio_completo))
        conexion.commit()

        if cursor.rowcount == 0:
            return {
                "respuesta": f"No se encontró el folio '{folio_completo}' para actualizar.",
                "db_exito": False,
            }

        return {
            "respuesta": (
                f"El registro '{folio_completo}' fue actualizado correctamente: "
                f"{campo} = {nuevo_valor}."
            ),
            "db_exito": True,
        }

    except Exception:
        if conexion:
            conexion.rollback()

        return {
            "respuesta": "No fue posible guardar el cambio. Inténtalo más tarde.",
            "db_exito": False,
        }

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()