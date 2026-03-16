"""
sdk.client
----------
Simulación de cliente REST para envío de datos procesados a un endpoint.
Mantiene un contrato fijo de retorno independientemente del resultado,
usando os.environ para leer variables de entorno opcionales.
"""

import os
import random
from datetime import datetime, timezone
from typing import Any, Dict

from sdk.logging_utils import configurar_logger

logger = configurar_logger()


class APIResponseInvalida(Exception):
    """Error de cliente: la respuesta simulada tiene un status code inesperado."""
    def __init__(self, mensaje: str, status_code: int = 0):
        super().__init__(mensaje)
        self.status_code = status_code


def enviar_metricas(
    payload: Dict[str, Any],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Simula el envío del payload procesado a un endpoint REST.
    Lee variables de entorno opcionales (SDK_REGION, SDK_TOKEN) para
    demostrar el uso de os.environ en proyectos de nube.

    Parámetros:
        payload : Diccionario con los datos a enviar (resultado del procesamiento).
        config  : Diccionario de configuración del SDK.

    Retorna siempre un dict con contrato fijo:
        {
            "status_code"      : int,
            "exito"            : bool,
            "endpoint"         : str,
            "region"           : str,
            "registros_enviados: int,
            "timestamp_envio"  : str (ISO 8601),
            "mensaje"          : str
        }

    Lanza:
        APIResponseInvalida si el status_code simulado es inesperado (>= 500).
    """
    # Leer parámetros de configuración, con sobrescritura desde variables de entorno
    endpoint = config["api"]["endpoint"]
    # ------------------------------------------------------------------
    # COMPLETAR EL CODIGO ESCOGIDO DE Análisis de código — 3.3 Leer una variable de entorno
    # ------------------------------------------------------------------
    ______________________________
    token    = os.environ.get("SDK_TOKEN",  config["api"]["token"])
    timeout  = config["api"]["timeout_s"]

    logger.info(
        f"Iniciando envío → endpoint: '{endpoint}' | "
        f"región: '{region}' | timeout: {timeout}s"
    )

    # Simular comportamiento de red (80% éxito, 10% error 503, 10% error 429)
    simulacion = random.random()
    if simulacion < 0.80:
        status_code = 200
    elif simulacion < 0.90:
        status_code = 503
    else:
        status_code = 429

    exito   = status_code == 200
    # ------------------------------------------------------------------
    # COMPLETAR EL CODIGO ESCOGIDO DE Análisis de código — 3.4 Mapear códigos HTTP a mensajes
    # ------------------------------------------------------------------
    ______________________________

    resultado = {
        "status_code"       : status_code,
        "exito"             : exito,
        "endpoint"          : endpoint,
        "region"            : region,
        "token_usado"       : token[:20] + "...",    # ocultar token completo en logs
        "registros_enviados": payload.get("total_procesados", 0),
        "timestamp_envio"   : datetime.now(timezone.utc).isoformat(),
        "mensaje"           : mensaje
    }

    if exito:
        logger.info(f"Envío exitoso (HTTP {status_code}): {mensaje}")
    else:
        logger.error(f"Envío fallido (HTTP {status_code}): {mensaje}")
        raise APIResponseInvalida(
            f"El servidor respondió con HTTP {status_code}: {mensaje}",
            status_code=status_code
        )

    return resultado
