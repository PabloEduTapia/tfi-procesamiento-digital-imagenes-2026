"""Core reusable del proyecto de procesamiento de imágenes."""

from .daltonismo import Daltonismo, TIPOS_DALTONISMO
from .pipeline import PipelineImagen, crear_comparativa

__all__ = ["Daltonismo", "TIPOS_DALTONISMO", "PipelineImagen", "crear_comparativa"]
