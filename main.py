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

imagen = cv2.resize(imagen, (800, 600)) 

# =========================================
# ELEGIR TIPO DE DALTONISMO
# =========================================

print("\nSeleccione una opción:")

print("1 - Protanopia")
print("2 - Deuteranopia")
print("3 - Tritanopia")
print("4 - Deficiencia cromática combinada (experimental)")

opcion = input("Opción: ")


if opcion == "1":

    # =====================================
    # SEVERIDAD
    # =====================================

    print("\n¿Qué tan severa es la protanopia?")

    print("1  - Muy leve   (0.1)")
    print("2  - Leve       (0.2)")
    print("3  - Moderada   (0.3)")
    print("4  - Media      (0.4)")
    print("5  - Notable    (0.5)")
    print("6  - Marcada    (0.6)")
    print("7  - Severa     (0.7)")
    print("8  - Muy severa (0.8)")
    print("9  - Casi total (0.9)")
    print("10 - Total      (1.0)")

    sev = input("Opción: ")

    opciones_severidad = {
        "1": 0.1, "2": 0.2, "3": 0.3,  "4": 0.4,
        "5": 0.5, "6": 0.6, "7": 0.7,  "8": 0.8,
        "9": 0.9, "10": 1.0
    }

    if sev not in opciones_severidad:
        print("Severidad inválida")
        exit()

    severidad = opciones_severidad[sev]

    daltonismo = Protanopia(severidad)


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