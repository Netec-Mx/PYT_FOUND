"""
sdk.exceptions
--------------
Jerarquía de excepciones personalizadas del SDK.
Cada excepción representa un error específico del protocolo HTTP
o de la lógica interna del cliente, con atributos de contexto adicionales.
"""


class SDKError(Exception):
    """
    Excepción base del SDK. Todas las demás excepciones del SDK
    heredan de esta clase, lo que permite capturarlas todas con
    un único bloque: except SDKError.
    """
    def __init__(self, mensaje: str, status_code: int = 0, detalle: str = ""):
        super().__init__(mensaje)
        self.status_code = status_code
        self.detalle     = detalle

    def __str__(self) -> str:
        base = super().__str__()
        if self.status_code:
            return f"[HTTP {self.status_code}] {base}"
        return base


class AuthenticationError(SDKError):
    """HTTP 401 — Credenciales inválidas o token expirado."""
    def __init__(self, mensaje: str = "Autenticación fallida: token inválido o expirado.",
                 detalle: str = ""):
        super().__init__(mensaje, status_code=401, detalle=detalle)


class BadRequestError(SDKError):
    """HTTP 400 — La solicitud tiene parámetros incorrectos o malformados."""
    def __init__(self, mensaje: str = "Solicitud incorrecta.", detalle: str = ""):
        super().__init__(mensaje, status_code=400, detalle=detalle)


class NotFoundError(SDKError):
    """HTTP 404 — El recurso solicitado no existe en el servidor."""
    def __init__(self, mensaje: str = "Recurso no encontrado.", detalle: str = ""):
        super().__init__(mensaje, status_code=404, detalle=detalle)


class ServerError(SDKError):
    """HTTP 500 — Error interno del servidor. Probable fallo en la infraestructura."""
    def __init__(self, mensaje: str = "Error interno del servidor.", detalle: str = ""):
        super().__init__(mensaje, status_code=500, detalle=detalle)


class RateLimitError(SDKError):
    """HTTP 429 — Demasiadas solicitudes en un período de tiempo."""
    def __init__(self, mensaje: str = "Límite de solicitudes superado. Reintente más tarde.",
                 detalle: str = ""):
        super().__init__(mensaje, status_code=429, detalle=detalle)


# Mapa de status_code → clase de excepción (útil para despacho automático)
HTTP_ERROR_MAP = {
    400: BadRequestError,
    401: AuthenticationError,
    404: NotFoundError,
    429: RateLimitError,
    500: ServerError,
}


def lanzar_por_status(status_code: int, detalle: str = "") -> None:
    """
    Lanza la excepción correspondiente al código HTTP recibido.
    Si el código no está mapeado, lanza SDKError genérico.

    Parámetros:
        status_code : Código HTTP de la respuesta (ej. 401, 500).
        detalle     : Mensaje adicional del servidor para incluir en el error.
    """

    
    # ------------------------------------------------------------------
    # COMPLETAR EL CODIGO ESCOGIDO DE Análisis de código — Despacho automático de excepciones
    # ------------------------------------------------------------------
    exc_cls = ______________________________
    raise _________________________________
