"""
sdk.endpoints
-------------
Clases de endpoint del SDK: BaseEndpoint, MetricsEndpoint y LogsEndpoint.

Cada clase de endpoint encapsula las operaciones HTTP (GET/POST) disponibles
en una sección específica de la API, usando el Authenticator para obtener
las cabeceras y `requests` para realizar las llamadas HTTP.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

from sdk.exceptions import lanzar_por_status, SDKError

logger = logging.getLogger("sdk_nube")


class BaseEndpoint:
    """
    Clase base para todos los endpoints del SDK.

    Encapsula la lógica común de construcción de URL, logging de
    solicitudes/respuestas y despacho de errores HTTP.

    Atributos:
        _auth    : Instancia de Authenticator para obtener cabeceras.
        _path    : Segmento de ruta específico del endpoint (ej. '/metricas').
    """

    def __init__(self, auth: Any, path: str) -> None:
        self._auth = auth
        self._path = path

    @property
    def _url(self) -> str:
        """Construye la URL completa concatenando base_url y el path del endpoint."""
        return f"{self._auth.base_url.rstrip('/')}{self._path}"

    # ------------------------------------------------------------------
    # Métodos protegidos — reutilizables por las subclases
    # ------------------------------------------------------------------
    def _get(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Realiza una solicitud GET al endpoint.
        Registra la solicitud y la respuesta en el log.
        Delega el manejo de errores HTTP a lanzar_por_status().

        Parámetros:
            params : Parámetros de query string opcionales (dict).

        Retorna:
            Diccionario con { status, data, errors }.
        """
        logger.info(f"GET {self._url} | params={params}")
        try:
            respuesta = requests.get(
                self._url,
                headers=self._auth.get_headers(),
                params=params,
                timeout=10
            )
            return self._procesar_respuesta(respuesta)

        except requests.exceptions.Timeout:
            logger.error(f"Timeout en GET {self._url}")
            return {"status": "error", "data": None,
                    "errors": ["La solicitud superó el tiempo de espera (timeout)."]}

        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión en GET {self._url}")
            return {"status": "error", "data": None,
                    "errors": ["No se pudo conectar al servidor. Verifique la red."]}

    def _post(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza una solicitud POST al endpoint con un cuerpo JSON.

        Parámetros:
            body : Diccionario que se serializa como JSON en el cuerpo.

        Retorna:
            Diccionario con { status, data, errors }.
        """
        logger.info(f"POST {self._url} | body_keys={list(body.keys())}")
        try:
            respuesta = requests.post(
                self._url,
                headers=self._auth.get_headers(),
                json=body,
                timeout=10
            )
            return self._procesar_respuesta(respuesta)

        except requests.exceptions.Timeout:
            logger.error(f"Timeout en POST {self._url}")
            return {"status": "error", "data": None,
                    "errors": ["La solicitud superó el tiempo de espera (timeout)."]}

        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión en POST {self._url}")
            return {"status": "error", "data": None,
                    "errors": ["No se pudo conectar al servidor. Verifique la red."]}

    def _procesar_respuesta(self, respuesta: requests.Response) -> Dict[str, Any]:
        """
        Interpreta el objeto Response de requests:
          - Si el status_code es 200 o 201, extrae y retorna los datos JSON.
          - Si el status_code indica un error HTTP, llama a lanzar_por_status()
            para lanzar la excepción personalizada correspondiente.

        Parámetros:
            respuesta : Objeto requests.Response recibido del servidor.

        Retorna:
            Diccionario con { status, data, errors }.
        """
        codigo = respuesta.status_code
        logger.info(f"Respuesta recibida: HTTP {codigo}")

        if codigo in (200, 201):
            datos = respuesta.json()
            logger.info(f"Solicitud exitosa (HTTP {codigo}).")
            return {"status": "ok", "data": datos, "errors": []}

        # Cualquier otro código es un error — despachar excepción personalizada
        try:
            detalle = respuesta.json().get("mensaje", respuesta.text)
        except Exception:
            detalle = respuesta.text

        logger.error(f"Error HTTP {codigo}: {detalle}")
        try:
            lanzar_por_status(codigo, detalle)
        except SDKError as e:
            return {"status": "error", "data": None, "errors": [str(e)]}

        # Fallback (nunca debería llegar aquí)
        return {"status": "error", "data": None, "errors": [f"HTTP {codigo}"]}


# ======================================================================
# Subclases de endpoint
# ======================================================================

class MetricsEndpoint(BaseEndpoint):
    """
    Endpoint para operaciones sobre métricas de sensores.
    Path: /v2/metricas

    Métodos disponibles:
        obtener()          → GET  /v2/metricas
        obtener_por_id()   → GET  /v2/metricas/{sensor_id}
        enviar()           → POST /v2/metricas
    """

    def __init__(self, auth: Any) -> None:
        super().__init__(auth, path="/v2/metricas")

    def obtener(self, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene todas las métricas disponibles, con filtro opcional por región.

        Parámetros:
            region : Filtro de región (ej. 'us-east-1'). Si es None, trae todo.
        """
        params = {"region": region} if region else None
        return self._get(params=params)

    def obtener_por_id(self, sensor_id: str) -> Dict[str, Any]:
        """
        Obtiene las métricas de un sensor específico por su ID.

        Parámetros:
            sensor_id : Identificador único del sensor (ej. 's-001').
        """
        logger.info(f"GET {self._url}/{sensor_id}")
        try:
            respuesta = requests.get(
                f"{self._url}/{sensor_id}",
                headers=self._auth.get_headers(),
                timeout=10
            )
            return self._procesar_respuesta(respuesta)
        except requests.exceptions.ConnectionError:
            return {"status": "error", "data": None,
                    "errors": ["No se pudo conectar al servidor."]}

    def enviar(self, metricas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Envía un lote de métricas al servidor mediante POST.

        Parámetros:
            metricas : Lista de diccionarios con datos de sensores.
        """
        return self._post({"metricas": metricas, "total": len(metricas)})


class LogsEndpoint(BaseEndpoint):
    """
    Endpoint para operaciones sobre logs de eventos del sistema.
    Path: /v2/logs

    Métodos disponibles:
        obtener()             → GET /v2/logs
        obtener_por_nivel()   → GET /v2/logs?nivel={nivel}
    """

    def __init__(self, auth: Any) -> None:
        super().__init__(auth, path="/v2/logs")

    def obtener(self) -> Dict[str, Any]:
        """Obtiene todos los logs disponibles del sistema."""
        return self._get()

    def obtener_por_nivel(self, nivel: str) -> Dict[str, Any]:
        """
        Obtiene logs filtrados por nivel (INFO, WARNING, ERROR).

        Parámetros:
            nivel : Nivel de log a filtrar ('INFO', 'WARNING', 'ERROR').
        """
        return self._get(params={"nivel": nivel.upper()})
