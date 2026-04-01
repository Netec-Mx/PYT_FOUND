"""
sdk.client
----------
Clase ApiClient: punto de entrada principal del mini-SDK.

Coordina la autenticación y expone los endpoints disponibles
como propiedades, siguiendo el patrón de SDK profesional donde
el cliente es el único objeto que el código externo necesita instanciar.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

from sdk.auth      import Authenticator
from sdk.endpoints import MetricsEndpoint, LogsEndpoint

logger = logging.getLogger("sdk_nube")


def _configurar_logger(nivel: str = "INFO",
                       archivo_log: str = "sdk_eventos.log") -> None:
    """Configura el logger raíz del SDK si aún no tiene handlers."""
    raiz = logging.getLogger("sdk_nube")
    if raiz.handlers:
        return

    nivel_num = getattr(logging, nivel.upper(), logging.INFO)
    raiz.setLevel(nivel_num)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    h_consola = logging.StreamHandler(sys.stdout)
    h_consola.setFormatter(fmt)
    raiz.addHandler(h_consola)

    ruta_log = Path(archivo_log)
    ruta_log.parent.mkdir(parents=True, exist_ok=True)
    h_archivo = logging.FileHandler(ruta_log, encoding="utf-8")
    h_archivo.setFormatter(fmt)
    raiz.addHandler(h_archivo)

    raiz.info(f"Logger inicializado. Log guardado en: '{ruta_log}'")


class ApiClient:
    """
    Punto de entrada del mini-SDK.

    Gestiona el ciclo de vida completo de la sesión:
      1. Inicialización con configuración (base_url, api_key).
      2. Autenticación (autenticar()).
      3. Acceso a endpoints mediante propiedades (metrics, logs).
      4. Cierre de sesión (cerrar_sesion()).

    Uso típico:
        cliente = ApiClient(config)
        cliente.autenticar(token="mi-token-aqui")
        resultado = cliente.metrics.obtener(region="us-east-1")
        cliente.cerrar_sesion()

    Atributos (privados):
        _auth    : Instancia de Authenticator.
        _metrics : Instancia de MetricsEndpoint (lazy init).
        _logs    : Instancia de LogsEndpoint (lazy init).
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Inicializa el cliente con la configuración proporcionada.

        Parámetros:
            config : Diccionario de configuración del SDK con las claves
                     'api' (endpoint, token, timeout_s) y 'logging'.
        """
        _configurar_logger(
            nivel       = config.get("logging", {}).get("nivel", "INFO"),
            archivo_log = config.get("logging", {}).get("archivo_log", "sdk_eventos.log")
        )

        self._auth    = Authenticator(
            api_key  = config["api"]["token"],
            base_url = config["api"]["endpoint"]
        )
        self._metrics : MetricsEndpoint | None = None
        self._logs    : LogsEndpoint    | None = None

        logger.info(
            f"ApiClient inicializado → base_url: '{self._auth.base_url}'"
        )

    # ------------------------------------------------------------------
    # Propiedades de acceso a endpoints (lazy initialization)
    # ------------------------------------------------------------------
    @property
    def metrics(self) -> MetricsEndpoint:
        """
        Retorna la instancia de MetricsEndpoint.
        Se crea en la primera llamada (lazy init) para evitar
        instanciar endpoints que no serán usados.
        """
        # ------------------------------------------------------------------
        # COMPLETAR EL CODIGO ESCOGIDO DE Análisis de código — Inicialización diferida (lazy init)
        # ------------------------------------------------------------------

    @property
    def logs(self) -> LogsEndpoint:
        """
        Retorna la instancia de LogsEndpoint.
        Se crea en la primera llamada (lazy init).
        """
        if self._logs is None:
            self._logs = LogsEndpoint(self._auth)
            logger.info("LogsEndpoint inicializado.")
        return self._logs

    # ------------------------------------------------------------------
    # Métodos de sesión
    # ------------------------------------------------------------------
    def autenticar(self, token: str) -> None:
        """
        Autentica el cliente con el token proporcionado.
        Delega en el Authenticator interno.

        Parámetros:
            token : Token Bearer de acceso a la API.
        """
        logger.info(f"Iniciando autenticación del cliente...")
        self._auth.autenticar(token)

    def cerrar_sesion(self) -> None:
        """Cierra la sesión activa e invalida el token."""
        self._auth.cerrar_sesion()

    @property
    def esta_autenticado(self) -> bool:
        """Retorna True si el cliente tiene una sesión activa."""
        return self._auth.autenticado

    def __repr__(self) -> str:
        estado = "autenticado" if self.esta_autenticado else "no autenticado"
        return f"ApiClient(base_url='{self._auth.base_url}', estado='{estado}')"
