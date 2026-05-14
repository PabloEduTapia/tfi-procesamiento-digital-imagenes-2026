"""
Procesamiento específico para simulación y corrección de daltonismo.

Este módulo pertenece al Core del proyecto. No lee archivos, no guarda archivos
ni muestra ventanas. Solo recibe una imagen en memoria, la procesa y devuelve
otra imagen. Eso permite reutilizarlo desde consola, una app web, tests u otra UI.

Convención importante:
- OpenCV carga imágenes en formato BGR.
- Las matrices de simulación se expresan en RGB.
Por eso la clase convierte BGR -> RGB antes de aplicar la matriz y luego vuelve
a BGR para mantener compatibilidad con OpenCV.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


TIPOS_DALTONISMO: dict[str, np.ndarray] = {
    # Dificultad para percibir tonos rojos.
    "protanopia": np.array(
        [
            [0.567, 0.433, 0.000],
            [0.558, 0.442, 0.000],
            [0.000, 0.242, 0.758],
        ],
        dtype=np.float32,
    ),
    # Dificultad para percibir tonos verdes.
    "deuteranopia": np.array(
        [
            [0.625, 0.375, 0.000],
            [0.700, 0.300, 0.000],
            [0.000, 0.300, 0.700],
        ],
        dtype=np.float32,
    ),
    # Dificultad para percibir tonos azules.
    "tritanopia": np.array(
        [
            [0.950, 0.050, 0.000],
            [0.000, 0.433, 0.567],
            [0.000, 0.475, 0.525],
        ],
        dtype=np.float32,
    ),
}


@dataclass
class Daltonismo:
    """
    Procesador de daltonismo.

    Parameters
    ----------
    tipo:
        Tipo de daltonismo a aplicar: protanopia, deuteranopia o tritanopia.
    """

    tipo: str = "protanopia"

    def __post_init__(self) -> None:
        tipo_normalizado = self.tipo.lower().strip()
        if tipo_normalizado not in TIPOS_DALTONISMO:
            tipos = ", ".join(TIPOS_DALTONISMO.keys())
            raise ValueError(f"Tipo de daltonismo no válido: {self.tipo}. Opciones: {tipos}")

        self.tipo = tipo_normalizado
        self.matriz = TIPOS_DALTONISMO[self.tipo]

    def simular(self, imagen_bgr: np.ndarray) -> np.ndarray:
        """
        Simula cómo podría percibirse una imagen según el tipo de daltonismo.

        Recibe una imagen BGR de OpenCV y devuelve una nueva imagen BGR.
        """

        self._validar_imagen(imagen_bgr)

        imagen_rgb = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2RGB).astype(np.float32)

        # Para cada píxel RGB aplicamos la matriz de transformación.
        simulada_rgb = imagen_rgb @ self.matriz.T
        simulada_rgb = np.clip(simulada_rgb, 0, 255).astype(np.uint8)

        return cv2.cvtColor(simulada_rgb, cv2.COLOR_RGB2BGR)

    def corregir(self, imagen_bgr: np.ndarray, intensidad: float = 0.70) -> np.ndarray:
        """
        Genera una imagen corregida o daltonizada.

        La idea es comparar la imagen original con la simulada. Esa diferencia
        indica información cromática que se pierde con el tipo de daltonismo.
        Luego se redistribuye parte de esa diferencia hacia canales más visibles.

        intensidad:
            Valor entre 0 y 1. A mayor intensidad, más fuerte es la corrección.
        """

        self._validar_imagen(imagen_bgr)
        intensidad = float(np.clip(intensidad, 0.0, 1.0))

        simulada = self.simular(imagen_bgr)

        original = imagen_bgr.astype(np.float32)
        simulada_float = simulada.astype(np.float32)
        error = original - simulada_float

        # OpenCV trabaja BGR. Separamos canales para poder reforzar selectivamente.
        b, g, r = cv2.split(original)
        error_b, error_g, error_r = cv2.split(error)

        if self.tipo in ("protanopia", "deuteranopia"):
            # En protanopia/deuteranopia se pierde mucha información rojo-verde.
            # Reubicamos parte del error rojo hacia verde y azul.
            g = g + error_r * intensidad
            b = b + error_r * intensidad * 0.60
        elif self.tipo == "tritanopia":
            # En tritanopia el problema principal está en azules/amarillos.
            r = r + error_b * intensidad * 0.60
            g = g + error_b * intensidad

        corregida = cv2.merge((b, g, r))
        return np.clip(corregida, 0, 255).astype(np.uint8)

    @staticmethod
    def _validar_imagen(imagen: np.ndarray) -> None:
        if imagen is None:
            raise ValueError("La imagen recibida es None")
        if not isinstance(imagen, np.ndarray):
            raise TypeError("La imagen debe ser un numpy.ndarray")
        if imagen.ndim != 3 or imagen.shape[2] != 3:
            raise ValueError("La imagen debe tener 3 canales de color")
