# Informe técnico - Simulación y corrección de daltonismo

## 1. Problema

El proyecto aborda una problemática vinculada a la accesibilidad visual: algunas personas con daltonismo pueden tener dificultad para distinguir ciertos colores dentro de una imagen. Esto puede afectar la interpretación de gráficos, señalética, interfaces, mapas, imágenes educativas o piezas visuales donde el color comunica información importante.

La aplicación permite recibir una imagen real, simular cómo podría percibirse bajo distintos tipos de daltonismo y generar una versión corregida donde se refuerzan ciertos canales de color para facilitar la diferenciación.

## 2. Enfoque

Se eligió una solución basada en procesamiento digital de imágenes con Python, OpenCV, Pillow y NumPy.

El enfoque general es:

1. Recibir una imagen de entrada.
2. Aplicar una matriz de transformación de color para simular daltonismo.
3. Comparar la imagen original con la imagen simulada.
4. Calcular la diferencia cromática perdida.
5. Redistribuir parte de esa diferencia en otros canales de color.
6. Guardar una imagen resultante y una comparativa visual.

Esto permite que el resultado sea verificable porque se pueden observar en una misma salida la imagen original, la simulada y la corregida.

## 3. Técnicas utilizadas

### 3.1 Lectura y escritura de imágenes

Se utiliza OpenCV para leer imágenes desde disco con `cv2.imread` y guardar resultados con `cv2.imwrite`.

OpenCV trabaja internamente con imágenes en formato BGR, por eso cuando se aplican operaciones basadas en RGB se realiza la conversión correspondiente.

### 3.2 Transformación mediante matrices de color

Para simular daltonismo se aplica una matriz 3x3 a cada píxel de la imagen. Cada tipo de daltonismo usa una matriz diferente:

- Protanopía: dificultad con tonos rojos.
- Deuteranopía: dificultad con tonos verdes.
- Tritanopía: dificultad con tonos azules.

La operación principal es:

```python
simulada_rgb = imagen_rgb @ matriz.T
```

Esto transforma cada píxel RGB en un nuevo píxel que representa una aproximación visual del tipo de daltonismo seleccionado.

### 3.3 Corrección o daltonización

La corrección compara la imagen original contra la simulada:

```python
error = original - simulada
```

Ese error representa información cromática que se pierde en la simulación. Luego se toma parte de esa diferencia y se redistribuye en otros canales de color con una intensidad configurable.

Ejemplo para protanopía y deuteranopía:

```python
g = g + error_r * intensidad
b = b + error_r * intensidad * 0.60
```

El objetivo no es recuperar la visión original, sino generar una imagen donde las diferencias entre colores sean más fáciles de distinguir.

### 3.4 Ajustes con Pillow

La clase `PipelineImagen` incorpora operaciones de Pillow para brillo, contraste y saturación. Esto permite combinar técnicas de distintas librerías dentro de un mismo flujo.

### 3.5 Filtros y segmentación

También se agregan operaciones complementarias para cumplir con contenidos de la materia:

- Escala de grises.
- Desenfoque gaussiano.
- Nitidez.
- Detección de bordes con Canny.
- Emboss.
- Umbralización.
- Detección de contornos.

## 4. Implementación

El proyecto separa responsabilidades en distintos módulos:

| Archivo | Responsabilidad |
|---|---|
| `main.py` | Entrada de ejecución por consola. Define modo automático y manual. |
| `core/daltonismo.py` | Lógica de simulación y corrección. No lee ni guarda archivos. |
| `core/pipeline.py` | Pipeline encadenable de procesamiento de imágenes. |
| `core/demo.py` | Generación de imagen demo para pruebas. |
| `tests/test_core.py` | Tests básicos del Core. |

Esta separación permite que el Core sea reutilizable y no dependa de la forma de ejecución.

## 5. Flujo de datos

```text
Imagen de entrada
      ↓
Carga con OpenCV
      ↓
PipelineImagen
      ↓
Ajustes opcionales: tamaño, brillo, contraste, filtros
      ↓
Simulación o corrección de daltonismo
      ↓
Imagen resultante
      ↓
Guardado en output/
```

## 6. Modos de ejecución

### 6.1 Modo automático

Procesa la imagen para protanopía, deuteranopía y tritanopía. Para cada tipo genera:

- Imagen simulada.
- Imagen corregida.
- Imagen comparativa.

Comando:

```bash
python main.py --modo auto
```

### 6.2 Modo manual

Permite pasar parámetros desde consola.

Ejemplo:

```bash
python main.py --modo manual --accion corregir --tipo protanopia --intensidad 0.8 --input input/mi_imagen.jpg --output output/corregida.jpg
```

## 7. Pruebas y resultados

El proyecto incluye una imagen demo que se genera automáticamente si no se indica una imagen de entrada. Esta imagen contiene colores variados para verificar si la transformación produce cambios visibles.

Para validar técnicamente el Core se incluyen tests básicos:

```bash
pytest
```

Estos tests comprueban que la simulación devuelve una imagen con la misma forma y tipo de datos que la imagen original, y que el pipeline encadenado funciona correctamente.

## 8. Decisiones técnicas

- Se mantuvo una lógica de pipeline encadenable porque fue la idea trabajada en clase y facilita leer el proceso paso a paso.
- Se separó el Core de `main.py` para cumplir con reutilización y separación de responsabilidades.
- Se usó OpenCV para operaciones matriciales, filtros, lectura y escritura.
- Se usó Pillow para ajustes simples de tono y color, aprovechando su API clara.
- Se agregó modo automático para generar resultados rápidos y modo manual para experimentar con parámetros.

## 9. Limitaciones

- Las matrices utilizadas son aproximaciones y no reemplazan una evaluación médica o perceptual real.
- La corrección puede mejorar la diferenciación en algunos casos, pero también puede alterar la estética original de la imagen.
- La efectividad depende mucho del tipo de imagen, sus colores y el nivel de intensidad elegido.

## 10. Mejoras futuras

- Agregar una interfaz visual simple con Streamlit o Flask.
- Permitir comparar varias intensidades de corrección en una sola salida.
- Agregar métricas cuantitativas sobre cambios de color.
- Incorporar más modelos de simulación.
- Permitir procesamiento por lotes de varias imágenes.
- Crear una vista web para cargar imagen, seleccionar parámetros y descargar resultados.

## 11. Aprendizajes

Durante el desarrollo se aplicaron conceptos de procesamiento digital de imágenes, programación orientada a objetos, separación de responsabilidades, uso de pipelines y combinación de librerías. También se reforzó la importancia de documentar las decisiones técnicas y de generar salidas verificables para poder explicar el proceso completo.
