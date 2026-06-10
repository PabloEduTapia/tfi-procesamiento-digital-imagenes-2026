from core.daltonismo import Daltonismo
from core.matrices_machado import obtener_matriz


class Deuteranopia(Daltonismo):

    def __init__(self, severidad=1.0):
        matriz, tipo, severidad = obtener_matriz("deutan", severidad)
        super().__init__(matriz, tipo, severidad)
