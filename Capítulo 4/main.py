"""
main.py — Script principal del mini-SDK modular.

Coordina el flujo completo del SDK:
  1. Configurar el sistema de logging.
  2. Cargar la configuración desde el archivo JSON.
  3. Cargar y procesar las métricas de sensores.
  4. Simular el envío de los resultados a la API REST.
  5. Mostrar el reporte final en consola.

Usa pathlib y sys para gestión de rutas portable.
"""

import json
import sys
from pathlib import Path

# Asegurar que Python encuentra el paquete 'sdk' cuando se ejecuta desde
# cualquier directorio, resolviendo la raíz del proyecto dinámicamente.
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sdk.logging_utils import configurar_logger
from sdk.config        import cargar_config, ConfiguracionInvalida
from sdk.processing    import cargar_metricas, procesar_metricas, DatosFaltantes
from sdk.client        import enviar_metricas, APIResponseInvalida

# ---------------------------------------------------------------------------
# Rutas de archivos (relativas a la raíz del proyecto)
# ---------------------------------------------------------------------------
RUTA_CONFIG   = ROOT / "data" / "config.json"
RUTA_METRICAS = ROOT / "data" / "metricas.json"


def main() -> None:
    # -----------------------------------------------------------------------
    # 1. Inicializar logger
    # -----------------------------------------------------------------------
    logger = configurar_logger(
        nombre      = "sdk_nube",
        nivel       = "INFO",
        archivo_log = str(ROOT / "sdk_eventos.log")
    )
    logger.info("=" * 55)
    logger.info("Iniciando mini-SDK modular de métricas de nube")
    logger.info("=" * 55)

    # -----------------------------------------------------------------------
    # 2. Cargar configuración
    # -----------------------------------------------------------------------
    print(f"\n{'='*55}")
    print("PASO 1 — CARGA DE CONFIGURACIÓN")
    print('='*55)
    try:
        config = cargar_config(str(RUTA_CONFIG))
        print(f"  Endpoint   : {config['api']['endpoint']}")
        print(f"  Región     : {config['procesamiento']['region']}")
        print(f"  Umbral CPU : {config['procesamiento']['umbral_cpu_alerta']}%")
        print(f"  Umbral lat.: {config['procesamiento']['umbral_latencia_ms']} ms")
    except ConfiguracionInvalida as e:
        logger.error(f"Error crítico de configuración: {e}")
        sys.exit(1)   # Detener ejecución si no hay configuración válida

    # -----------------------------------------------------------------------
    # 3. Cargar y procesar métricas
    # -----------------------------------------------------------------------
    print(f"\n{'='*55}")
    print("PASO 2 — CARGA Y PROCESAMIENTO DE MÉTRICAS")
    print('='*55)
    try:
        registros = cargar_metricas(str(RUTA_METRICAS))
    except DatosFaltantes as e:
        logger.error(f"No se pudieron cargar las métricas: {e}")
        sys.exit(1)

    resultado = procesar_metricas(registros, config)

    print(f"\n  Status          : {resultado['status']}")
    print(f"  Total registros : {len(registros)}")
    print(f"  Válidos         : {len(registros) - len(resultado['errores'])}")
    print(f"  Inválidos       : {len(resultado['errores'])}")
    print(f"  Alertas         : {len(resultado['alertas'])}")

    if resultado["resultado"]:
        print(f"\n  Estadísticas por campo:")
        for campo, stats in resultado["resultado"].items():
            print(f"    [{campo.upper()}]")
            print(f"      Promedio   : {stats['promedio']}")
            print(f"      Máximo     : {stats['maximo']}")
            print(f"      Mínimo     : {stats['minimo']}")
            print(f"      Desv. std  : {stats['desv_std']}")
            print(f"      Muestras   : {stats['muestras']}")

    if resultado["errores"]:
        print(f"\n  Registros con errores:")
        for err in resultado["errores"]:
            print(f"    → sensor_id: {err['sensor_id']} | "
                  f"campo inválido: '{err['campo_invalido']}'")

    if resultado["alertas"]:
        print(f"\n  Alertas generadas:")
        for alerta in resultado["alertas"]:
            print(f"    ⚠  {alerta}")

    # -----------------------------------------------------------------------
    # 4. Simular envío a la API
    # -----------------------------------------------------------------------
    print(f"\n{'='*55}")
    print("PASO 3 — SIMULACIÓN DE ENVÍO A LA API")
    print('='*55)

    payload = {
        "total_procesados"  : len(registros),
        "registros_validos" : len(registros) - len(resultado["errores"]),
        "estadisticas"      : resultado["resultado"],
        "alertas_generadas" : len(resultado["alertas"])
    }

    for intento in range(1, 4):          # hasta 3 intentos
        print(f"\n  [Intento {intento}/3]")
        try:
            respuesta = enviar_metricas(payload, config)
            print(f"    Status code       : {respuesta['status_code']}")
            print(f"    Éxito             : {respuesta['exito']}")
            print(f"    Endpoint          : {respuesta['endpoint']}")
            print(f"    Región            : {respuesta['region']}")
            print(f"    Registros enviados: {respuesta['registros_enviados']}")
            print(f"    Timestamp         : {respuesta['timestamp_envio']}")
            print(f"    Mensaje           : {respuesta['mensaje']}")
            break   # Si el envío fue exitoso, no reintentar
        except APIResponseInvalida as e:
            print(f"    Error capturado (HTTP {e.status_code}): {e}")
            if intento == 3:
                logger.error("Se agotaron los 3 intentos de envío a la API.")

    # -----------------------------------------------------------------------
    # 5. Reporte final consolidado
    # -----------------------------------------------------------------------
    print(f"\n{'='*55}")
    print("REPORTE FINAL CONSOLIDADO")
    print('='*55)
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    logger.info("Ejecución del SDK finalizada.")
    logger.info("=" * 55)


if __name__ == "__main__":
    main()
