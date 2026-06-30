from __future__ import annotations

import cv2
import numpy as np

from core.matrix_repository import MatrixRepository


class DaltonismEngine:

    def __init__(self, matrix_repository: MatrixRepository):
        self.matrix_repository = matrix_repository

    def simulate(self, image: np.ndarray, tipos: list[str], severity: float) -> np.ndarray:
        matrix = self.matrix_repository.get_combined_matrix(tipos, severity)
        return self._apply_matrix(image, matrix)

    def correct(
        self,
        image: np.ndarray,
        tipos: list[str],
        severity: float,
        intensity: float = 0.7,
    ) -> np.ndarray:
        simulated = self.simulate(image, tipos, severity)
        original_float = image.astype(np.float32)
        simulated_float = simulated.astype(np.float32)
        error = original_float - simulated_float

        b, g, r = cv2.split(original_float.copy())
        error_b, error_g, error_r = cv2.split(error)

        normalized_types = {
            self.matrix_repository.normalize_type(tipo)
            for tipo in tipos
        }

        for tipo in normalized_types:
            if tipo == "protanomaly":
                g += error_r * intensity
                b += error_r * intensity
            elif tipo == "deuteranomaly":
                r += error_g * intensity
                b += error_g * intensity
            elif tipo == "tritanomaly":
                r += error_b * intensity
                g += error_b * intensity

        corrected = cv2.merge((b, g, r))
        return np.clip(corrected, 0, 255).astype(np.uint8)

    @staticmethod
    def _apply_matrix(image: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        # OpenCV trabaja en BGR y las matrices de Machado están expresadas en RGB.
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        normalized = rgb.astype(np.float32) / 255.0
        pixels = normalized.reshape(-1, 3)
        transformed = (matrix @ pixels.T).T
        transformed = np.clip(transformed, 0, 1)
        result = (transformed.reshape(rgb.shape) * 255).astype(np.uint8)
        return cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
