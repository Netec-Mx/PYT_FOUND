"""
sdk.processing
--------------
Carga y procesamiento estadístico de métricas de sensores simulados.
Calcula estadísticas por campo numérico y genera alertas según los
umbrales definidos en la configuración del SDK.
"""

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

from sdk.logging_utils import configurar_logger

logger = configurar_logger()

CAMPOS_NUMERICOS   = ["cpu_pct", "mem_pct", "latency_ms"]
CAMPOS_OBLIGATORIOS = ["sensor_id", "service", "timestamp"] + CAMPOS_NUMERICOS


class DatosFaltantes(Exception):
    """Error de procesamiento: registro con campos nulos o ausentes."""
    def __init__(self, mensaje: str, campo: str = ""):
        super().__init__(mensaje)
        self.campo = campo


def cargar_metricas(ruta: str) -> List[Dict[str, Any]]:
    """
    Carga registros de métricas desde un archivo JSON usando pathlib.

    Parámetros:
        ruta : Ruta al archivo JSON de métricas.

    Retorna:
        Lista de diccionarios con los registros cargados.

    Lanza:
        DatosFaltantes si el archivo no existe o el JSON es inválido.
    """
    ruta_obj = Path(ruta)

    if not ruta_obj.exists():
        logger.error(f"Archivo de métricas no encontrado: '{ruta_obj}'")
        raise DatosFaltantes(
            f"No se encontró el archivo de métricas: '{ruta_obj.resolve()}'"
        )

    try:
        datos = json.loads(ruta_obj.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        logger.error(f"JSON inválido en '{ruta_obj}': {e}")
        raise DatosFaltantes(f"Archivo JSON malformado '{ruta_obj}': {e}")

    logger.info(f"Métricas cargadas: {len(datos)} registros desde '{ruta_obj.name}'.")
    return datos


def _validar_registro(registro: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Valida que un registro tenga todos los campos obligatorios y sin nulos.
    Retorna (es_valido, nombre_del_campo_con_error).
    (Función privada — uso interno del módulo.)
    """
    for campo in CAMPOS_OBLIGATORIOS:
        if campo not in registro:
            return False, campo
        if registro[campo] is None:
            return False, campo
    return True, ""


def procesar_metricas(
    registros: List[Dict[str, Any]],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Procesa el lote completo de registros de sensores:
      - Filtra registros inválidos (nulos/faltantes) y los registra.
      - Calcula estadísticas (promedio, máx, mín, desv. std) por campo numérico.
      - Genera alertas si los valores superan los umbrales de configuración.

    Parámetros:
        registros : Lista de registros de sensores (dicts).
        config    : Diccionario de configuración del SDK.

    Retorna siempre:
        {
            "status"   : "ok" | "parcial" | "error",
            "resultado": { estadísticas por campo numérico },
            "errores"  : [ lista de registros inválidos ],
            "alertas"  : [ lista de mensajes de alerta ]
        }
    """
    umbral_cpu = config["procesamiento"]["umbral_cpu_alerta"]
    umbral_lat = config["procesamiento"]["umbral_latencia_ms"]

    CAMPOS = ["sensor_id", "service", "timestamp", "cpu_pct", "mem_pct", "latency_ms"]

    # ------------------------------------------------------------------
    # COMPLETAR EL CODIGO ESCOGIDO DE Análisis de código — 3.2 Validar registros
    # ------------------------------------------------------------------
    ______________________________

    alertas: List[str]  = []

    for reg in validos:

        # Verificar umbrales
        if reg["cpu_pct"] >= umbral_cpu:
            msg = (f"ALERTA CPU — {reg['sensor_id']} ({reg['service']}): "
                   f"{reg['cpu_pct']}% ≥ umbral {umbral_cpu}%")
            logger.warning(msg)
            alertas.append(msg)

        if reg["latency_ms"] >= umbral_lat:
            msg = (f"ALERTA LATENCIA — {reg['sensor_id']} ({reg['service']}): "
                   f"{reg['latency_ms']} ms ≥ umbral {umbral_lat} ms")
            logger.warning(msg)
            alertas.append(msg)

    # Calcular estadísticas por campo numérico
    estadisticas: Dict[str, Any] = {}
    if validos:
        for campo in CAMPOS_NUMERICOS:
            valores = [r[campo] for r in validos]
            promedio = sum(valores) / len(valores)
            varianza = sum((v - promedio) ** 2 for v in valores) / len(valores)
            estadisticas[campo] = {
                "promedio" : round(promedio, 2),
                "maximo"   : max(valores),
                "minimo"   : min(valores),
                "desv_std" : round(math.sqrt(varianza), 2),
                "muestras" : len(valores)
            }

    status = "ok" if not errores else ("parcial" if validos else "error")

    logger.info(
        f"Procesamiento finalizado — válidos: {len(validos)}, "
        f"inválidos: {len(errores)}, alertas: {len(alertas)}, status: '{status}'"
    )

    return {
        "status"   : status,
        "resultado": estadisticas,
        "errores"  : errores,
        "alertas"  : alertas
    }
