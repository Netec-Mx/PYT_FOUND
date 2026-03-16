"""
sdk.auth
--------
Clase Authenticator: gestiona credenciales de acceso a la API
y genera las cabeceras HTTP necesarias para cada solicitud.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger("sdk_nube")


class Authenticator:
    """
    Gestiona la autenticación del cliente hacia la API REST.

    Encapsula el API key y el token de acceso, y expone un método
    para generar las cabeceras HTTP requeridas en cada solicitud.

    Atributos:
        _api_key     : Clave de API proporcionada en la configuración.
        _token       : Token de acceso Bearer (None hasta que se autentica).
        _autenticado : Bandera booleana que indica si la sesión es válida.
    """

    def __init__(self, api_key: str, base_url: str) -> None:
        self._api_key     : str            = api_key
        self._base_url    : str            = base_url
        self._token       : Optional[str]  = None
        self._autenticado : bool           = False

    # ------------------------------------------------------------------
    # Propiedades de solo lectura (encapsulamiento: el token no se expone
    # directamente; se consume solo a través de get_headers())
    # ------------------------------------------------------------------
    @property
    def autenticado(self) -> bool:
        """Retorna True si el cliente tiene una sesión activa."""
        return self._autenticado

    @property
    def base_url(self) -> str:
        """Retorna la URL base de la API."""
        return self._base_url

    # ------------------------------------------------------------------
    # Métodos públicos
    # ------------------------------------------------------------------
    def autenticar(self, token_simulado: str) -> None:
        """
        Establece el token de acceso y marca la sesión como autenticada.
        En un SDK real, este método realizaría una solicitud POST al
        endpoint de autenticación y recibiría el token del servidor.

        Parámetros:
            token_simulado : Token que la simulación entrega al SDK.
        """
        self._token       = token_simulado
        self._autenticado = True
        logger.info("Autenticación completada. Sesión activa.")

    def cerrar_sesion(self) -> None:
        """Invalida el token y cierra la sesión activa."""
        self._token       = None
        self._autenticado = False
        logger.info("Sesión cerrada. Token revocado.")

    def get_headers(self) -> Dict[str, str]:
        """
        Genera y retorna el diccionario de cabeceras HTTP necesarias
        para autenticar las solicitudes a la API.

        Retorna:
            Dict con las cabeceras Authorization, Content-Type y X-API-Key.

        Lanza:
            RuntimeError si se llama antes de autenticar la sesión.
        """

        # ------------------------------------------------------------------
        # COMPLETAR EL CODIGO ESCOGIDO DE Análisis de código — Protección del estado interno
        # ------------------------------------------------------------------

        return {
            "Authorization" : f"Bearer {self._token}",
            "Content-Type"  : "application/json",
            "X-API-Key"     : self._api_key,
        }

    def __repr__(self) -> str:
        estado = "autenticado" if self._autenticado else "no autenticado"
        return f"Authenticator(base_url='{self._base_url}', estado='{estado}')"
