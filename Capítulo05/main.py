"""
main.py — Script principal del mini-SDK orientado a objetos.

Este script demuestra el uso completo del SDK en un flujo de 4 pasos:
  1. Cargar configuración.
  2. Crear ApiClient y autenticar la sesión.
  3. Llamar a MetricsEndpoint y LogsEndpoint (con respuestas mockeadas).
  4. Procesar resultados y manejar errores HTTP.

Las llamadas HTTP se simulan con unittest.mock.patch para que el lab
funcione sin conexión a un servidor real. La lógica del SDK (clases,
cabeceras, manejo de errores) es completamente real y funcional.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# -----------------------------------------------------------------------
# Ajuste de sys.path para importar el paquete 'sdk' correctamente
# -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sdk.client     import ApiClient
from sdk.exceptions import SDKError

# -----------------------------------------------------------------------
# Constantes de simulación
# -----------------------------------------------------------------------
TOKEN_SIMULADO = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.lab-simulado"

RESPUESTA_METRICAS = {
    "total": 3,
    "region": "us-east-1",
    "metricas": [
        {"sensor_id": "s-001", "service": "api-gateway",
         "cpu_pct": 72.4, "mem_pct": 65.1, "latency_ms": 210},
        {"sensor_id": "s-002", "service": "db-primary",
         "cpu_pct": 91.8, "mem_pct": 88.3, "latency_ms": 620},
        {"sensor_id": "s-003", "service": "auth-service",
         "cpu_pct": 34.5, "mem_pct": 42.0, "latency_ms": 95},
    ]
}

RESPUESTA_LOGS = {
    "total": 2,
    "logs": [
        {"timestamp": "2024-06-01T09:00:05Z", "nivel": "WARNING",
         "mensaje": "CPU alta en db-primary: 91.8%"},
        {"timestamp": "2024-06-01T09:00:20Z", "nivel": "INFO",
         "mensaje": "Métricas procesadas correctamente."},
    ]
}

RESPUESTA_POST_OK = {
    "mensaje": "Lote recibido correctamente.",
    "registros_procesados": 3,
    "job_id": "job-7f3a9c12"
}

RESPUESTA_ERROR_401 = {"mensaje": "Token inválido o expirado."}
RESPUESTA_ERROR_500 = {"mensaje": "Error interno del servidor al procesar el lote."}


# -----------------------------------------------------------------------
# Helpers para crear mocks de requests.Response
# -----------------------------------------------------------------------
def _mock_response(status_code: int, data: dict) -> MagicMock:
    """
    Crea un objeto MagicMock que simula un requests.Response con
    el status_code y el JSON indicados.
    """
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = data
    mock.text = json.dumps(data)
    return mock


# -----------------------------------------------------------------------
# Función principal
# -----------------------------------------------------------------------
def main() -> None:

    # -------------------------------------------------------------------
    # 1. Cargar configuración
    # -------------------------------------------------------------------
    ruta_config = ROOT / "data" / "config.json"
    config = json.loads(ruta_config.read_text(encoding="utf-8"))
    print(f"\n{'='*60}")
    print("PASO 1 — CONFIGURACIÓN CARGADA")
    print('='*60)
    print(f"  Base URL : {config['api']['endpoint']}")
    print(f"  Región   : {config['procesamiento']['region']}")

    # -------------------------------------------------------------------
    # 2. Crear cliente y autenticar
    # -------------------------------------------------------------------
    print(f"\n{'='*60}")
    print("PASO 2 — CREACIÓN Y AUTENTICACIÓN DEL CLIENTE")
    print('='*60)

    cliente = ApiClient(config)
    print(f"\n  Estado inicial : {cliente}")

    cliente.autenticar(token=TOKEN_SIMULADO)
    print(f"  Estado final   : {cliente}")
    print(f"  Autenticado    : {cliente.esta_autenticado}")

    # -------------------------------------------------------------------
    # 3. Llamadas a MetricsEndpoint (GET y POST)
    # -------------------------------------------------------------------
    print(f"\n{'='*60}")
    print("PASO 3 — OPERACIONES SOBRE MÉTRICAS")
    print('='*60)

    # -- 3a. GET exitoso (HTTP 200) --
    print(f"\n  [3a] GET metricas (HTTP 200 — éxito)")
    
    # ------------------------------------------------------------------
    # COLOCAR LA IMPLEMENTACIÓN CORRECTA ACA
    # ------------------------------------------------------------------

    print(f"  Status   : {resultado['status']}")
    print(f"  Total    : {resultado['data']['total']} sensores")
    for sensor in resultado["data"]["metricas"]:
        print(f"    • {sensor['sensor_id']} ({sensor['service']}) "
              f"CPU={sensor['cpu_pct']}%  LAT={sensor['latency_ms']}ms")

    # -- 3b. GET de sensor por ID (HTTP 200) --
    print(f"\n  [3b] GET /metricas/s-002 (HTTP 200 — éxito)")
    sensor_detalle = {
        "sensor_id": "s-002", "service": "db-primary",
        "cpu_pct": 91.8, "mem_pct": 88.3, "latency_ms": 620
    }
    with patch("requests.get",
               return_value=_mock_response(200, sensor_detalle)):
        resultado = cliente.metrics.obtener_por_id("s-002")

    print(f"  Status   : {resultado['status']}")
    print(f"  Sensor   : {resultado['data']}")

    # -- 3c. POST exitoso (HTTP 201) --
    print(f"\n  [3c] POST metricas (HTTP 201 — creado)")
    lote = RESPUESTA_METRICAS["metricas"]
    with patch("requests.post",
               return_value=_mock_response(201, RESPUESTA_POST_OK)):
        resultado = cliente.metrics.enviar(lote)

    print(f"  Status   : {resultado['status']}")
    print(f"  Mensaje  : {resultado['data']['mensaje']}")
    print(f"  Job ID   : {resultado['data']['job_id']}")

    # -- 3d. POST con error 500 --
    print(f"\n  [3d] POST metricas (HTTP 500 — error de servidor)")
    with patch("requests.post",
               return_value=_mock_response(500, RESPUESTA_ERROR_500)):
        resultado = cliente.metrics.enviar(lote)

    print(f"  Status   : {resultado['status']}")
    print(f"  Errores  : {resultado['errors']}")

    # -------------------------------------------------------------------
    # 4. Llamadas a LogsEndpoint
    # -------------------------------------------------------------------
    print(f"\n{'='*60}")
    print("PASO 4 — OPERACIONES SOBRE LOGS")
    print('='*60)

    # -- 4a. GET logs (HTTP 200) --
    print(f"\n  [4a] GET logs (HTTP 200 — éxito)")
    with patch("requests.get",
               return_value=_mock_response(200, RESPUESTA_LOGS)):
        resultado = cliente.logs.obtener()

    print(f"  Status   : {resultado['status']}")
    print(f"  Total    : {resultado['data']['total']} entradas")
    for entrada in resultado["data"]["logs"]:
        print(f"    [{entrada['nivel']}] {entrada['timestamp']} — {entrada['mensaje']}")

    # -- 4b. GET logs con error 401 --
    print(f"\n  [4b] GET logs por nivel (HTTP 401 — no autorizado)")
    with patch("requests.get",
               return_value=_mock_response(401, RESPUESTA_ERROR_401)):
        resultado = cliente.logs.obtener_por_nivel("ERROR")

    print(f"  Status   : {resultado['status']}")
    print(f"  Errores  : {resultado['errors']}")

    # -------------------------------------------------------------------
    # 5. Probar el guard de autenticación
    # -------------------------------------------------------------------
    print(f"\n{'='*60}")
    print("PASO 5 — CIERRE DE SESIÓN Y GUARD DE AUTENTICACIÓN")
    print('='*60)

    cliente.cerrar_sesion()
    print(f"\n  Estado tras cerrar sesión: {cliente}")

    print(f"\n  [Prueba] Intentar solicitud sin sesión activa:")
    try:
        with patch("requests.get",
                   return_value=_mock_response(200, RESPUESTA_METRICAS)):
            cliente.metrics.obtener()
    except RuntimeError as e:
        print(f"  RuntimeError capturado correctamente: {e}")

    print(f"\n{'='*60}")
    print("Ejecución del mini-SDK completada.")
    print('='*60)


if __name__ == "__main__":
    main()
