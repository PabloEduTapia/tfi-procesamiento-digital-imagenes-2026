import numpy as np

from core.daltonismo import Daltonismo
from core.matrices_machado import obtener_matriz, NOMBRES_LEGIBLES


class Combinado(Daltonismo):

    def __init__(self, tipos, severidad):
        if not tipos:
            raise ValueError("Debe indicar al menos un tipo de deficiencia.")

        matriz_combinada = np.eye(3, dtype=np.float32)
        tipos_normalizados = []
        severidad_normalizada = None

        for tipo in tipos:
            matriz, tipo_normalizado, severidad_normalizada = obtener_matriz(tipo, severidad)
            tipos_normalizados.append(tipo_normalizado)

            # Si hay mas de un tipo seleccionado, se aplican las matrices en el
            # orden ingresado. M2 @ M1 equivale a aplicar M1 y luego M2.
            matriz_combinada = matriz @ matriz_combinada

        # Evita repetir el mismo tipo si el usuario ingreso duplicados.
        tipos_normalizados = list(dict.fromkeys(tipos_normalizados))

        super().__init__(
            matriz_combinada,
            "combinado",
            severidad_normalizada,
            tipos_correccion=tipos_normalizados,
        )

        print("\nTipos seleccionados:")
        for tipo in tipos_normalizados:
            print(f"- {NOMBRES_LEGIBLES[tipo]}")

        print(f"\nSeveridad normalizada: {severidad_normalizada:.1f}")
        print("\nMatriz usada:")
        print(self.matriz.round(6))
