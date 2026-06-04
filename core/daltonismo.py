import cv2
import numpy as np


class Daltonismo:

    def __init__(self, matriz, tipo):
        self.matriz = matriz
        self.tipo = tipo

    # =========================================
    # SIMULAR DALTONISMO
    # =========================================

    def simular(self, imagen):

        # Convertir BGR a RGB
        imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

        imagen_float = imagen_rgb.astype(np.float32) / 255.0

        h, w, _ = imagen_float.shape
        pixeles = imagen_float.reshape(-1, 3)

        pixeles_sim = (self.matriz @ pixeles.T).T

        salida = pixeles_sim.reshape(h, w, 3)
        salida = np.clip(salida, 0, 1)
        salida = (salida * 255).astype(np.uint8)

        # Convertir RGB de vuelta a BGR
        return cv2.cvtColor(salida, cv2.COLOR_RGB2BGR)

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

        if self.tipo == "protanopia":
            # Cono L afectado → redistribuir error del rojo
            g = g + (error_r * intensidad)
            b = b + (error_r * intensidad)

        elif self.tipo == "deuteranopia":
            # Cono M afectado → redistribuir error del verde
            r = r + (error_g * intensidad)
            b = b + (error_g * intensidad)

        elif self.tipo == "tritanopia":
            # Cono S afectado → redistribuir error del azul
            r = r + (error_b * intensidad)
            g = g + (error_b * intensidad)

        corregida = cv2.merge((b, g, r))

        corregida = np.clip(corregida, 0, 255)

        return corregida.astype(np.uint8)