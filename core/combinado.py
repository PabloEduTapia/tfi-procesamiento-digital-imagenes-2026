import cv2
import numpy as np
import pandas as pd
from scipy.integrate import trapezoid


class Combinado:

    def __init__(self, tipos, delta_nm):

        # ==========================
        # CARGAR CURVAS
        # ==========================

        data = pd.read_csv(
            "SmithPokorny2deg.csv",
            sep=";",
            decimal=","
        )

        wavelengths = data["Wavelength"].values.astype(float)

        L_curve = data["L_cone"].values.astype(float)
        M_curve = data["M_cone"].values.astype(float)
        S_curve = data["S_cone"].values.astype(float)

        # ==========================
        # DESPLAZAMIENTO
        # ==========================

        def shift_curve(curve, delta):

            return np.interp(
                wavelengths,
                wavelengths + delta,
                curve,
                left=0,
                right=0
            )

        La = L_curve.copy()
        Ma = M_curve.copy()
        Sa = S_curve.copy()

        if "protan" in tipos:
            La = shift_curve(L_curve, delta_nm)

        if "deutan" in tipos:
            Ma = shift_curve(M_curve, delta_nm)

        if "tritan" in tipos:
            Sa = shift_curve(S_curve, delta_nm)

        # ==========================
        # LMS → OPONENTE
        # ==========================

        T = np.array([
            [0.600,  0.400,  0.000],
            [0.240,  0.105, -0.700],
            [1.200, -1.600,  0.400]
        ])

        Opp = T @ np.vstack([La, Ma, Sa])

        # ==========================
        # PRIMARIOS RGB
        # ==========================

        QR = np.exp(-0.5 * ((wavelengths - 610) / 20) ** 2)
        QG = np.exp(-0.5 * ((wavelengths - 540) / 30) ** 2)
        QB = np.exp(-0.5 * ((wavelengths - 450) / 20) ** 2)

        def integrate(primary, opponent):
            return trapezoid(primary * opponent, wavelengths)

        WS, YB, RG = Opp

        G_CVD = np.array([
            [integrate(QR, WS), integrate(QG, WS), integrate(QB, WS)],
            [integrate(QR, YB), integrate(QG, YB), integrate(QB, YB)],
            [integrate(QR, RG), integrate(QG, RG), integrate(QB, RG)]
        ])

        # Normalizar cada fila para que sume 1 (Ecuación 9 de Machado et al.)
        for i in range(3):
            total = G_CVD[i].sum()
            if total != 0:
                G_CVD[i] = G_CVD[i] / total

        # ==========================
        # MATRIZ NORMAL
        # ==========================

        Opp_n = T @ np.vstack([L_curve, M_curve, S_curve])

        WS_n, YB_n, RG_n = Opp_n

        G_normal = np.array([
            [integrate(QR, WS_n), integrate(QG, WS_n), integrate(QB, WS_n)],
            [integrate(QR, YB_n), integrate(QG, YB_n), integrate(QB, YB_n)],
            [integrate(QR, RG_n), integrate(QG, RG_n), integrate(QB, RG_n)]
        ])

        # Normalizar cada fila para que sume 1 (Ecuación 9 de Machado et al.)
        for i in range(3):
            total = G_normal[i].sum()
            if total != 0:
                G_normal[i] = G_normal[i] / total

        # ==========================
        # MATRIZ FINAL (Ec. 24)
        # ==========================

        self.M_combo = np.linalg.inv(G_normal) @ G_CVD

        print("\nMatriz combinada:")
        print(self.M_combo)
        

        # ==========================
        # DIAGNÓSTICO
        # ==========================

        print("\nMatriz generada por combinado.py:")
        print(self.M_combo.round(6))

        print("\nMatriz fija de protanopia (referencia):")
        ref = np.array([
            [0.152286, 1.052583, -0.204868],
            [0.114503, 0.786281,  0.099216],
            [0.000000, 0.000000,  1.000000]
        ])
        print(ref)

        print("\nDiferencia:")
        print((self.M_combo - ref).round(6))

    # ==========================
    # SIMULAR
    # ==========================

    def simular(self, imagen):

        # Convertir BGR a RGB
        imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

        img = imagen_rgb.astype(np.float32) / 255.0

        # Aplanar todos los píxeles: (alto, ancho, 3) → (alto×ancho, 3)
        h, w, _ = img.shape
        pixeles = img.reshape(-1, 3)

        # Multiplicar igual que daltonismo.py
        pixeles_sim = (self.M_combo @ pixeles.T).T

        # Reconstruir imagen
        salida = pixeles_sim.reshape(h, w, 3)
        salida = np.clip(salida, 0, 1)
        salida = (salida * 255).astype(np.uint8)

        # Convertir RGB de vuelta a BGR
        return cv2.cvtColor(salida, cv2.COLOR_RGB2BGR)

    # ==========================
    # CORREGIR
    # ==========================

    def corregir(self, imagen):

        # Temporal: devuelve la imagen sin cambios
        # hasta que se valide simular()
        return imagen