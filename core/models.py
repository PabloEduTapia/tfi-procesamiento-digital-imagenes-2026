from dataclasses import dataclass, field

import numpy as np


@dataclass
class ProcessingOptions:
    tipos: list[str]
    severidad: float = 1.0
    resultado: str = "corrected_marked"
    intensidad_correccion: float = 0.7
    espacio_marcadores: int = 42
    tamano_marcadores: int = 7
    incluir_leyenda: bool = True


@dataclass
class ProcessingContext:
    original: np.ndarray
    current: np.ndarray
    options: ProcessingOptions
    simulated: np.ndarray | None = None
    corrected: np.ndarray | None = None
    metadata: dict = field(default_factory=dict)
