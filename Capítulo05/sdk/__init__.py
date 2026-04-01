"""
sdk — Mini-SDK orientado a objetos para métricas de servicios en la nube.

Clases principales:
  ApiClient        → Punto de entrada del SDK (sdk.client).
  Authenticator    → Gestión de credenciales y cabeceras (sdk.auth).
  MetricsEndpoint  → Operaciones GET/POST sobre métricas (sdk.endpoints).
  LogsEndpoint     → Operaciones GET sobre logs (sdk.endpoints).

Excepciones personalizadas:
  SDKError, AuthenticationError, BadRequestError,
  NotFoundError, ServerError  (sdk.exceptions).
"""

__version__ = "1.0.0"
__author__  = "Laboratorio Python Moderno"
