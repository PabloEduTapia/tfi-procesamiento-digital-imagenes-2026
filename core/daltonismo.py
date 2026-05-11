import cv2
import numpy as np


class Daltonismo:

    def __init__(self, matriz):
        self.matriz = matriz

    # =========================================
    # SIMULAR DALTONISMO
    # =========================================

    def simular(self, imagen):

        imagen_float = imagen.astype(np.float32)

        b, g, r = cv2.split(imagen_float)

        r_nuevo = (
            self.matriz[0, 0] * r +
            self.matriz[0, 1] * g +
            self.matriz[0, 2] * b
        )

        g_nuevo = (
            self.matriz[1, 0] * r +
            self.matriz[1, 1] * g +
            self.matriz[1, 2] * b
        )

        b_nuevo = (
            self.matriz[2, 0] * r +
            self.matriz[2, 1] * g +
            self.matriz[2, 2] * b
        )

        imagen_simulada = cv2.merge((
            b_nuevo,
            g_nuevo,
            r_nuevo
        ))

        imagen_simulada = np.clip(
            imagen_simulada,
            0,
            255
        )

        return imagen_simulada.astype(np.uint8)

    # =========================================
    # CORREGIR DALTONISMO
    # =========================================

    def corregir(self, imagen, intensidad=0.7):

        simulada = self.simular(imagen)

        imagen_float = imagen.astype(np.float32)
        simulada_float = simulada.astype(np.float32)

        error = imagen_float - simulada_float

        corregida = imagen_float.copy()

        b, g, r = cv2.split(corregida)

        error_b, error_g, error_r = cv2.split(error)

        # Reforzar azul y verde
        g = g + (error_r * intensidad)
        b = b + (error_r * intensidad)

        corregida = cv2.merge((b, g, r))

        corregida = np.clip(
            corregida,
            0,
            255
        )

        return corregida.astype(np.uint8)