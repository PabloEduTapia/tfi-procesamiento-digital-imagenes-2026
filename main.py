import cv2

from core.protanopia import Protanopia
#from core.deuteranopia import Deuteranopia # Lo agrega despues D'annunzio
#from core.tritanopia import Tritanopia # Lo agrega despues Tapia
from core.combinado import Combinado

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

#imagen = cv2.resize(imagen, (800, 600)) 

# =========================================
# ELEGIR TIPO DE DALTONISMO
# =========================================

print("\nSeleccione una opción:")

print("1 - Protanopia total")
print("2 - Deuteranopia total")
print("3 - Tritanopia total")
print("4 - Combinado o severidad")

opcion = input("Opción: ")


if opcion == "1":

    daltonismo = Protanopia()


elif opcion == "2":

    daltonismo = Deuteranopia()


elif opcion == "3":

    daltonismo = Tritanopia()


elif opcion == "4":

    # =====================================
    # ELEGIR DEFICIENCIAS
    # =====================================

    print("\n¿Qué tipo de deficiencia tiene?")
    print("(Puede elegir varias separadas por coma)\n")

    print("1 - Protanomalía")
    print("2 - Deuteranomalía")
    print("3 - Tritanomalía")

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


    # =====================================
    # SEVERIDAD
    # =====================================

    print("\n¿Qué tan severo?")

    print("1 - Leve")
    print("2 - Moderado")
    print("3 - Severo")

    severidad = input("Opción: ")


    if severidad == "1":

        delta_nm = 6

    elif severidad == "2":

        delta_nm = 14

    elif severidad == "3":

        delta_nm = 20

    else:

        print("Severidad inválida")
        exit()


    daltonismo = Combinado(
        tipos,
        delta_nm
    )


else:

    print("Opción inválida")
    exit()


# =========================================
# PROCESAMIENTO
# =========================================

simulada = daltonismo.simular(imagen)

corregida = daltonismo.corregir(imagen)

# =========================================
# GUARDAR RESULTADOS
# =========================================

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