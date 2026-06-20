
from core.combinado import Combinado


def simular_daltonismo(imagen, tipo, severidad=1.0):
    tipo = tipo.strip().lower()

    if tipo in ("protan", "protanopia", "protanomalia", "protanomalía"):
        return Protanopia(severidad).simular(imagen)

    if tipo in ("deutan", "deuteranopia", "deuteranomalia", "deuteranomalía"):
        return Deuteranopia(severidad).simular(imagen)

    if tipo in ("tritan", "tritanopia", "tritanomalia", "tritanomalía"):
        return Tritanopia(severidad).simular(imagen)

    print("Tipo de daltonismo no válido")
    return imagen


def simular_daltonismo_combinado(imagen, tipos, severidad=1.0):
    return Combinado(tipos, severidad).simular(imagen)
