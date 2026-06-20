import os
import cv2

from core.combinado import Combinado
from core.matrices_machado import normalizar_severidad


# =========================================
# CARGAR IMAGEN
# =========================================

imagen = cv2.imread("input/imagen.jpg")

if imagen is None:
    print("Error al cargar la imagen")
    exit()

# =========================================
# REDIMENSIONAR
# =========================================

# imagen = cv2.resize(imagen, (800, 600))

# =========================================
# FUNCIONES AUXILIARES
# =========================================


def pedir_tipos():
    print("\n¿Qué tipo de deficiencia tiene?")
    print("Puede elegir varias separadas por coma.\n")
    print("1 - Protanomalía / Protanopia")
    print("2 - Deuteranomalía / Deuteranopia")
    print("3 - Tritanomalía / Tritanopia")

    seleccion = input("\nEjemplo: 1,2\nOpción: ")
    tipos = []

    for t in seleccion.split(","):
        t = t.strip()

        if t == "1":
            tipos.append("protan")
        elif t == "2":
            tipos.append("deutan")
        elif t == "3":
            tipos.append("tritan")

    if len(tipos) == 0:
        print("Selección inválida")
        exit()

    return tipos


def pedir_severidad():
    print("\n¿Qué tan severo?")
    print("Ingrese un valor de 0 a 10:")
    print("0 = sin deficiencia")
    print("10 = máxima severidad / dicromacia")
    print("También puede ingresar 0.0, 0.1, 0.2 ... 1.0")

    valor = input("Severidad: ")

    try:
        return normalizar_severidad(valor)
    except ValueError as ex:
        print(f"Severidad inválida: {ex}")
        exit()


# =========================================
# ELEGIR TIPO DE DALTONISMO
# =========================================

print("\nSeleccione una opción:")

print("1 - Elegir tipo y severidad")
print("2 - Combinado")

opcion = input("Opción: ")

try:
    if opcion == "1":
        tipos = pedir_tipos()

        if len(tipos) > 1:
            print("Para elegir varios tipos use la opción 5 - Combinado.")
            exit()

        severidad = pedir_severidad()
        daltonismo = Combinado(tipos, severidad)

    elif opcion == "2":
        tipos = pedir_tipos()
        severidad = pedir_severidad()
        daltonismo = Combinado(tipos, severidad)

    else:
        print("Opción inválida")
        exit()

except ValueError as ex:
    print(f"Error de configuración: {ex}")
    exit()

# =========================================
# PROCESAMIENTO
# =========================================

simulada = daltonismo.simular(imagen)
corregida = daltonismo.corregir(imagen)

# =========================================
# GUARDAR RESULTADOS
# =========================================

os.makedirs("output", exist_ok=True)
cv2.imwrite("output/simulada.jpg", simulada)
cv2.imwrite("output/corregida.jpg", corregida)

# =========================================
# MOSTRAR RESULTADOS
# =========================================

cv2.imshow("Original", imagen)
cv2.imshow("Simulada", simulada)
cv2.imshow("Corregida", corregida)

cv2.waitKey(0)
cv2.destroyAllWindows()

print("Procesamiento finalizado")
