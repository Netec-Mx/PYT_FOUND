"""
sdk.config
----------
Carga y validación de configuraciones del SDK desde archivos JSON o YAML.
Usa pathlib para manejar rutas de forma portable entre sistemas operativos.
"""

import json
from pathlib import Path
from typing import Any, Dict

import yaml

from sdk.logging_utils import configurar_logger

logger = configurar_logger()

# Claves que DEBEN existir en el archivo de configuración
CLAVES_OBLIGATORIAS = ["api", "procesamiento", "logging"]


class ConfiguracionInvalida(Exception):
    """Error de configuración: archivo no encontrado, formato incorrecto
    o claves obligatorias faltantes."""
    pass


def cargar_config(ruta: str) -> Dict[str, Any]:
    """
    Detecta automáticamente el formato del archivo de configuración
    (.json o .yaml/.yml) y lo carga como diccionario Python.

    Parámetros:
        ruta : Ruta al archivo de configuración (relativa o absoluta).

    Retorna:
        Diccionario con la configuración cargada.

    Lanza:
        ConfiguracionInvalida si el archivo no existe, tiene formato
        incorrecto o le faltan claves obligatorias.
    """
    ruta_obj = Path(ruta)

    if not ruta_obj.exists():
        logger.error(f"Archivo de configuración no encontrado: '{ruta_obj}'")
        raise ConfiguracionInvalida(
            f"No se encontró el archivo: '{ruta_obj.resolve()}'"
        )

    extension = ruta_obj.suffix.lower()

    try:
        # ------------------------------------------------------------------
        # COMPLETAR EL CODIGO ESCOGIDO DE Análisis de código — 3.1 Cargar un archivo de configuración
        # ------------------------------------------------------------------
        ______________________________

    except (json.JSONDecodeError, yaml.YAMLError) as e:
        logger.error(f"Error al parsear '{ruta_obj}': {e}")
        raise ConfiguracionInvalida(f"Archivo malformado '{ruta_obj}': {e}")

    _validar_claves(config, ruta_obj.name)
    logger.info(f"Configuración cargada desde '{ruta_obj.name}' ({extension}).")
    return config


def _validar_claves(config: Dict[str, Any], nombre_archivo: str) -> None:
    """
    Verifica que el diccionario de configuración contenga todas las
    claves obligatorias definidas en CLAVES_OBLIGATORIAS.
    (Función privada — uso interno del módulo.)
    """
    for clave in CLAVES_OBLIGATORIAS:
        if clave not in config:
            logger.error(
                f"Clave obligatoria '{clave}' faltante en '{nombre_archivo}'"
            )
            raise ConfiguracionInvalida(
                f"Falta la clave obligatoria '{clave}' en '{nombre_archivo}'"
            )
    logger.info("Todas las claves obligatorias de configuración están presentes.")
