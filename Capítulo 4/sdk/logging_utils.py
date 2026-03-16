"""
sdk.logging_utils
-----------------
Configuración centralizada del sistema de logging para el mini-SDK.
Todos los demás módulos importan el logger desde aquí para garantizar
un formato y destino consistentes en toda la aplicación.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def configurar_logger(
    nombre: str = "sdk_nube",
    nivel: str = "INFO",
    archivo_log: Optional[str] = None
) -> logging.Logger:
    """
    Crea y configura un logger con salida a consola y, opcionalmente,
    a un archivo de log.

    Parámetros:
        nombre      : Nombre del logger (aparece en cada línea de log).
        nivel       : Nivel mínimo de logging ('DEBUG', 'INFO', 'WARNING', 'ERROR').
        archivo_log : Ruta al archivo .log. Si es None, solo escribe en consola.

    Retorna:
        logging.Logger configurado y listo para usar.
    """
    logger = logging.getLogger(nombre)

    # Evitar agregar handlers duplicados si la función se llama más de una vez
    if logger.handlers:
        return logger

    nivel_numerico = getattr(logging, nivel.upper(), logging.INFO)
    logger.setLevel(nivel_numerico)

    formato = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler de consola (siempre activo)
    handler_consola = logging.StreamHandler(sys.stdout)
    handler_consola.setFormatter(formato)
    logger.addHandler(handler_consola)

    # Handler de archivo (opcional)
    if archivo_log:
        ruta_log = Path(archivo_log)
        ruta_log.parent.mkdir(parents=True, exist_ok=True)
        handler_archivo = logging.FileHandler(ruta_log, encoding="utf-8")
        handler_archivo.setFormatter(formato)
        logger.addHandler(handler_archivo)
        logger.info(f"Log también guardado en: '{ruta_log}'")

    return logger
