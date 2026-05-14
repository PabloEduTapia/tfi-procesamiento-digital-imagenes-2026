"""
Pipeline de procesamiento de imágenes.

La clase PipelineImagen sigue la misma idea vista en clase:

    PipelineImagen("input/imagen.jpg").brillo(1.1).contraste(1.2).guardar("salida.jpg")

Cada método modifica la imagen interna y devuelve self. Eso permite encadenar
operaciones de forma simple y legible.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from .daltonismo import Daltonismo


class PipelineImagen:
    """Pipeline reutilizable para aplicar operaciones con OpenCV y Pillow."""

    def __init__(self, ruta: str | Path | None = None, imagen: np.ndarray | None = None):
        if ruta is None and imagen is None:
            raise ValueError("Debe indicar una ruta de imagen o una imagen en memoria")

        self.ruta = Path(ruta) if ruta is not None else None
        self.pasos: list[str] = []

        if imagen is not None:
            self._imagen = imagen.copy()
        else:
            self._imagen = cv2.imread(str(self.ruta))
            if self._imagen is None:
                raise FileNotFoundError(f"No se pudo cargar la imagen: {self.ruta}")

    @property
    def imagen(self) -> np.ndarray:
        """Devuelve una copia de la imagen actual para evitar modificaciones externas."""

        return self._imagen.copy()

    def clonar(self) -> "PipelineImagen":
        """Crea otro pipeline con el estado actual de la imagen."""

        nuevo = PipelineImagen(imagen=self._imagen)
        nuevo.pasos = self.pasos.copy()
        return nuevo

    def guardar(self, ruta_salida: str | Path) -> "PipelineImagen":
        """Guarda la imagen actual en disco."""

        ruta = Path(ruta_salida)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ok = cv2.imwrite(str(ruta), self._imagen)
        if not ok:
            raise RuntimeError(f"No se pudo guardar la imagen en: {ruta}")
        return self

    # =========================================================
    # Transformaciones geométricas
    # =========================================================

    def redimensionar(self, ancho: int | None = None, alto: int | None = None) -> "PipelineImagen":
        """Redimensiona la imagen. Si falta una medida, conserva la proporción."""

        h, w = self._imagen.shape[:2]

        if ancho is None and alto is None:
            return self
        if ancho is None:
            escala = alto / h
            ancho = int(w * escala)
        if alto is None:
            escala = ancho / w
            alto = int(h * escala)

        self._imagen = cv2.resize(self._imagen, (int(ancho), int(alto)), interpolation=cv2.INTER_AREA)
        self.pasos.append(f"redimensionar(ancho={ancho}, alto={alto})")
        return self

    def rotar(self, grados: float) -> "PipelineImagen":
        """Rota la imagen alrededor de su centro."""

        h, w = self._imagen.shape[:2]
        centro = (w // 2, h // 2)
        matriz = cv2.getRotationMatrix2D(centro, grados, 1.0)
        self._imagen = cv2.warpAffine(self._imagen, matriz, (w, h))
        self.pasos.append(f"rotar({grados})")
        return self

    def flip_horizontal(self) -> "PipelineImagen":
        self._imagen = cv2.flip(self._imagen, 1)
        self.pasos.append("flip_horizontal()")
        return self

    def flip_vertical(self) -> "PipelineImagen":
        self._imagen = cv2.flip(self._imagen, 0)
        self.pasos.append("flip_vertical()")
        return self

    # =========================================================
    # Ajustes de tono y color con Pillow
    # =========================================================

    def brillo(self, factor: float = 1.0) -> "PipelineImagen":
        self._aplicar_pillow(lambda img: ImageEnhance.Brightness(img).enhance(factor))
        self.pasos.append(f"brillo({factor})")
        return self

    def contraste(self, factor: float = 1.0) -> "PipelineImagen":
        self._aplicar_pillow(lambda img: ImageEnhance.Contrast(img).enhance(factor))
        self.pasos.append(f"contraste({factor})")
        return self

    def saturacion(self, factor: float = 1.0) -> "PipelineImagen":
        self._aplicar_pillow(lambda img: ImageEnhance.Color(img).enhance(factor))
        self.pasos.append(f"saturacion({factor})")
        return self

    def escala_grises(self) -> "PipelineImagen":
        gris = cv2.cvtColor(self._imagen, cv2.COLOR_BGR2GRAY)
        self._imagen = cv2.cvtColor(gris, cv2.COLOR_GRAY2BGR)
        self.pasos.append("escala_grises()")
        return self

    # =========================================================
    # Filtros espaciales
    # =========================================================

    def desenfoque_gaussiano(self, kernel: int = 5) -> "PipelineImagen":
        kernel = self._normalizar_kernel(kernel)
        self._imagen = cv2.GaussianBlur(self._imagen, (kernel, kernel), 0)
        self.pasos.append(f"desenfoque_gaussiano({kernel})")
        return self

    def nitidez(self, intensidad: float = 1.0) -> "PipelineImagen":
        """Aumenta la nitidez usando una máscara de enfoque simple."""

        suavizada = cv2.GaussianBlur(self._imagen, (0, 0), 3)
        self._imagen = cv2.addWeighted(self._imagen, 1.0 + intensidad, suavizada, -intensidad, 0)
        self.pasos.append(f"nitidez({intensidad})")
        return self

    def bordes(self, umbral1: int = 80, umbral2: int = 160) -> "PipelineImagen":
        gris = cv2.cvtColor(self._imagen, cv2.COLOR_BGR2GRAY)
        bordes = cv2.Canny(gris, umbral1, umbral2)
        self._imagen = cv2.cvtColor(bordes, cv2.COLOR_GRAY2BGR)
        self.pasos.append(f"bordes({umbral1}, {umbral2})")
        return self

    def emboss(self) -> "PipelineImagen":
        self._aplicar_pillow(lambda img: img.filter(ImageFilter.EMBOSS))
        self.pasos.append("emboss()")
        return self

    # =========================================================
    # Segmentación básica
    # =========================================================

    def umbral(self, valor: int = 127) -> "PipelineImagen":
        gris = cv2.cvtColor(self._imagen, cv2.COLOR_BGR2GRAY)
        _, binaria = cv2.threshold(gris, valor, 255, cv2.THRESH_BINARY)
        self._imagen = cv2.cvtColor(binaria, cv2.COLOR_GRAY2BGR)
        self.pasos.append(f"umbral({valor})")
        return self

    def contornos(self, valor_umbral: int = 120) -> "PipelineImagen":
        gris = cv2.cvtColor(self._imagen, cv2.COLOR_BGR2GRAY)
        _, binaria = cv2.threshold(gris, valor_umbral, 255, cv2.THRESH_BINARY)
        contornos, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        imagen_contornos = self._imagen.copy()
        cv2.drawContours(imagen_contornos, contornos, -1, (0, 255, 0), 2)
        self._imagen = imagen_contornos
        self.pasos.append(f"contornos({valor_umbral})")
        return self

    # =========================================================
    # Operaciones propias del proyecto
    # =========================================================

    def simular_daltonismo(self, tipo: str = "protanopia") -> "PipelineImagen":
        self._imagen = Daltonismo(tipo).simular(self._imagen)
        self.pasos.append(f"simular_daltonismo('{tipo}')")
        return self

    def corregir_daltonismo(self, tipo: str = "protanopia", intensidad: float = 0.70) -> "PipelineImagen":
        self._imagen = Daltonismo(tipo).corregir(self._imagen, intensidad=intensidad)
        self.pasos.append(f"corregir_daltonismo('{tipo}', intensidad={intensidad})")
        return self

    # =========================================================
    # Métodos auxiliares privados
    # =========================================================

    def _aplicar_pillow(self, operacion) -> None:
        """Convierte OpenCV BGR a Pillow RGB, aplica la operación y vuelve a BGR."""

        rgb = cv2.cvtColor(self._imagen, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pil_procesada = operacion(pil)
        rgb_procesada = np.array(pil_procesada)
        self._imagen = cv2.cvtColor(rgb_procesada, cv2.COLOR_RGB2BGR)

    @staticmethod
    def _normalizar_kernel(kernel: int) -> int:
        """OpenCV necesita kernels impares y mayores o iguales a 3."""

        kernel = int(kernel)
        if kernel < 3:
            kernel = 3
        if kernel % 2 == 0:
            kernel += 1
        return kernel


def crear_comparativa(imagenes: Iterable[np.ndarray], titulos: Iterable[str]) -> np.ndarray:
    """
    Crea una imagen horizontal con varias versiones para comparar resultados.

    Se usa para cumplir la consigna de salida verificable: permite ver original,
    simulada y corregida en una sola imagen.
    """

    imagenes = list(imagenes)
    titulos = list(titulos)

    if len(imagenes) != len(titulos):
        raise ValueError("La cantidad de imágenes y títulos debe coincidir")

    alto_objetivo = min(img.shape[0] for img in imagenes)
    paneles = []

    for img, titulo in zip(imagenes, titulos):
        h, w = img.shape[:2]
        escala = alto_objetivo / h
        ancho = int(w * escala)
        panel = cv2.resize(img, (ancho, alto_objetivo), interpolation=cv2.INTER_AREA)

        # Banda superior blanca para escribir el título.
        banda = np.full((45, panel.shape[1], 3), 255, dtype=np.uint8)
        cv2.putText(banda, titulo, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)
        paneles.append(np.vstack([banda, panel]))

    return np.hstack(paneles)
