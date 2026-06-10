import cv2
import numpy as np


class Daltonismo:

    def __init__(self, matriz, tipo, severidad=1.0, tipos_correccion=None):
        self.matriz = np.array(matriz, dtype=np.float32)
        self.tipo = tipo
        self.severidad = severidad
        self.tipos_correccion = tipos_correccion or [tipo]

    # =========================================
    # SIMULAR DALTONISMO
    # =========================================

    def simular(self, imagen):
        return self._aplicar_matriz(imagen, self.matriz)

    def _aplicar_matriz(self, imagen, matriz):
        # OpenCV carga en BGR, pero las matrices de Machado trabajan sobre RGB.
        imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        imagen_float = imagen_rgb.astype(np.float32) / 255.0

        h, w, _ = imagen_float.shape
        pixeles = imagen_float.reshape(-1, 3)

        pixeles_sim = (matriz @ pixeles.T).T

        salida = pixeles_sim.reshape(h, w, 3)
        salida = np.clip(salida, 0, 1)
        salida = (salida * 255).astype(np.uint8)

        return cv2.cvtColor(salida, cv2.COLOR_RGB2BGR)

    # =========================================
    # CORREGIR DALTONISMO
    # =========================================

    def corregir(self, imagen, intensidad=0.7):
        """
        Correccion simple por redistribucion del error.

        La simulacion se hace con la matriz del tipo/severidad elegidos. Luego se
        calcula el error contra la imagen original y se redistribuye el canal mas
        afectado hacia los otros canales para hacerlo mas distinguible.
        """
        simulada = self.simular(imagen)

        imagen_float = imagen.astype(np.float32)
        simulada_float = simulada.astype(np.float32)

        error = imagen_float - simulada_float
        corregida = imagen_float.copy()

        b, g, r = cv2.split(corregida)
        error_b, error_g, error_r = cv2.split(error)

        for tipo in self.tipos_correccion:
            if tipo == "protanomaly":
                # Cono L afectado -> redistribuir error del rojo.
                g = g + (error_r * intensidad)
                b = b + (error_r * intensidad)

            elif tipo == "deuteranomaly":
                # Cono M afectado -> redistribuir error del verde.
                r = r + (error_g * intensidad)
                b = b + (error_g * intensidad)

            elif tipo == "tritanomaly":
                # Cono S afectado -> redistribuir error del azul.
                r = r + (error_b * intensidad)
                g = g + (error_b * intensidad)

        corregida = cv2.merge((b, g, r))
        corregida = np.clip(corregida, 0, 255)

        return corregida.astype(np.uint8)
