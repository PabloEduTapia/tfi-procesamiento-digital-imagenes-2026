from __future__ import annotations

import cv2
import numpy as np


SUPPORTED_FORMATS = {
    "jpg": (".jpg", "image/jpeg"),
    "jpeg": (".jpg", "image/jpeg"),
    "png": (".png", "image/png"),
    "webp": (".webp", "image/webp"),
}


class ImageCodec:

    @staticmethod
    def decode(content: bytes) -> np.ndarray:
        if not content:
            raise ValueError("El archivo de imagen está vacío.")

        buffer = np.frombuffer(content, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("No se pudo interpretar el archivo como una imagen válida.")

        return image

    @staticmethod
    def encode(image: np.ndarray, output_format: str = "png") -> tuple[bytes, str]:
        format_key = output_format.strip().lower()

        if format_key not in SUPPORTED_FORMATS:
            raise ValueError("El formato de salida debe ser png, jpg o webp.")

        extension, media_type = SUPPORTED_FORMATS[format_key]
        success, buffer = cv2.imencode(extension, image)

        if not success:
            raise ValueError("No se pudo generar la imagen de salida.")

        return buffer.tobytes(), media_type
