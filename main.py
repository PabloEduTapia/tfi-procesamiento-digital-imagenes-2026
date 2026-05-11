import cv2

from core.protanopia import Protanopia

# =========================================
# CARGAR IMAGEN
# =========================================

imagen = cv2.imread("input/imagen.jpeg")

if imagen is None:
    print("Error al cargar la imagen")
    exit()

# =========================================
# REDIMENSIONAR
# =========================================

imagen = cv2.resize(imagen, (800, 600))

# =========================================
# CREAR OBJETO
# =========================================

daltonismo = Protanopia()

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