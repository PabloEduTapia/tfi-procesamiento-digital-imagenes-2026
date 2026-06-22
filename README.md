# Proyecto de Procesamiento Digital de Imágenes: Simulación y Corrección de Daltonismo

## 1. Descripción general

Este proyecto desarrolla una aplicación en Python orientada al procesamiento digital de imágenes. Su objetivo es recibir una imagen real, aplicar transformaciones cromáticas relacionadas con distintos tipos de daltonismo y generar nuevas imágenes procesadas que permitan comparar el resultado con la imagen original.

El proyecto puede usarse de dos formas: por consola (`main.py`, modo original) o mediante una interfaz web (`app.py`) que permite subir una imagen desde el navegador, elegir el tipo de daltonismo con un clic y ver la comparación original / simulada / corregida sin instalar nada adicional fuera de las dependencias de Python.

La aplicación permite simular cómo podría percibirse una imagen bajo ciertas deficiencias de visión del color y luego aplicar una corrección cromática para mejorar la diferenciación visual entre colores.

El proyecto trabaja con tres tipos principales de deficiencia cromática:

* Protanomalía / Protanopía
* Deuteranomalía / Deuteranopía
* Tritanomalía / Tritanopía

También incluye un modo combinado experimental que permite aplicar más de un tipo de deficiencia cromática.

## 2. Objetivo del proyecto

El objetivo del proyecto es construir una aplicación capaz de:

1. Recibir una imagen real como entrada.
2. Procesarla mediante técnicas de procesamiento digital de imágenes.
3. Aplicar transformaciones cromáticas basadas en matrices.
4. Generar una imagen simulada.
5. Generar una imagen corregida.
6. Guardar los resultados para permitir la comparación visual.

El propósito no es “curar” el daltonismo ni reemplazar una evaluación médica, sino mostrar cómo las operaciones sobre los canales de color de una imagen pueden modificar la percepción visual y mejorar la diferenciación de ciertos colores.

## 3. Enfoque técnico

El proyecto utiliza un enfoque determinístico basado en matrices de transformación cromática. En lugar de entrenar un modelo de inteligencia artificial, se aplican operaciones matemáticas sobre los valores de los píxeles de la imagen.

Cada imagen digital se representa como una matriz de píxeles con tres canales de color. La transformación se aplica sobre esos canales para simular o corregir la percepción cromática.

El procesamiento principal se encuentra separado en un Core reutilizable ubicado en la carpeta `core/`.

## 4. Estructura del proyecto

```text
tfi-procesamiento-digital-imagenes-2026/
│
├── core/
│   ├── __init__.py
│   ├── combinado.py
│   ├── daltonismo.py
│   └── matrices_machado.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── estilos.css
│   └── js/
│       └── app.js
│
├── docs/
│   ├── informe_tecnico.md
│   ├── imagenes/
│   │   ├── original.jpg
│   │   ├── simulada.jpg
│   │   └── corregida.jpg
│   ├── Paper_Daltonismo.docx
│   └── A Physiologically-based Model...
│
├── input/
│   └── imagen.jpg
│
├── output/
│   ├── simulada.jpg
│   └── corregida.jpg
│
├── main.py
├── app.py
├── README.md
├── requirements.txt
└── .gitignore
```

## 5. Archivos principales

### `main.py`

Es el punto de entrada del programa por consola. Se encarga de:

* cargar la imagen de entrada;
* pedir al usuario el tipo de daltonismo;
* pedir la severidad;
* llamar al Core de procesamiento;
* guardar las imágenes resultantes;
* mostrar la comparación visual.

### `app.py`

Es el punto de entrada del programa por interfaz web (Flask). Se encarga de:

* servir la página principal (`templates/index.html`);
* recibir la imagen subida desde el navegador junto con el tipo y la severidad elegidos;
* convertir el archivo subido al formato que espera el Core;
* llamar al mismo Core de procesamiento que usa `main.py`;
* devolver las tres imágenes (original, simulada, corregida) codificadas para mostrarlas en la página sin recargarla.

No contiene ninguna lógica de transformación de píxeles: esa responsabilidad sigue exclusivamente en `core/`.

### `templates/index.html` y `static/`

Contienen el formulario de carga, los controles de tipo y severidad, y los estilos y el JavaScript que comunican el navegador con `app.py`.

### `core/daltonismo.py`

Define la estructura base para los procesamientos relacionados con daltonismo.

### `core/combinado.py`

Implementa la lógica para aplicar uno o varios tipos de deficiencia cromática sobre la imagen.

### `core/matrices_machado.py`

Contiene las matrices utilizadas para simular las deficiencias de visión del color y la función de normalización de severidad.

### `input/`

Carpeta donde se coloca la imagen original que será procesada (usada por `main.py`; la versión web recibe la imagen directamente desde el navegador).

### `output/`

Carpeta donde se guardan las imágenes generadas por `main.py`.

## 6. Requisitos

El proyecto utiliza Python 3 y las siguientes bibliotecas:

* NumPy
* OpenCV
* Pillow
* Flask
* pytest

NumPy se utiliza para operar sobre arrays de imagen. OpenCV se utiliza para procesamiento, guardado y visualización de imágenes. Pillow se utiliza para carga y validación inicial. Flask se utiliza para la interfaz web. pytest se utiliza para ejecutar la prueba automatizada del Core.

Estas dependencias están indicadas en el archivo `requirements.txt`.

## 7. Instalación

Desde la carpeta raíz del proyecto, instalar las dependencias con:

```bash
pip install -r requirements.txt
```

## 8. Ejecución

Para ejecutar el programa, usar:

```bash
python main.py
```

El programa utiliza por defecto la imagen ubicada en:

```text
input/imagen.jpg
```

Por lo tanto, antes de ejecutar el programa se debe colocar allí la imagen que se desea procesar, o reemplazar la imagen existente por otra con el mismo nombre.

### 8.1. Ejecución con interfaz web

Como alternativa a la consola, el proyecto incluye una interfaz web construida con Flask. Permite subir cualquier imagen desde el navegador, elegir el tipo de daltonismo y la severidad con un control deslizante, y ver la comparación original / simulada / corregida sin pasar por la terminal en cada uso.

Para levantar el servidor:

```bash
python app.py
```

Luego abrir en el navegador:

```text
http://127.0.0.1:5000
```

La interfaz web reutiliza exactamente el mismo `Core` (`core/daltonismo.py`, `core/combinado.py`, `core/matrices_machado.py`) que usa `main.py`. No hay lógica de procesamiento de imágenes duplicada entre la versión de consola y la versión web: `app.py` solo recibe el archivo subido, lo convierte a un array compatible con OpenCV, llama a `Combinado` y devuelve las tres imágenes resultantes codificadas en base64 para mostrarlas en la página, sin necesidad de recargarla.

El modo combinado (más de un tipo de daltonismo a la vez) sigue disponible únicamente desde `main.py`; el formulario web trabaja con un tipo por vez mediante botones de selección única, priorizando la simplicidad de uso.

## 9. Uso del programa

Al ejecutar el programa, se muestra un menú principal:

```text
1 - Elegir tipo y severidad
2 - Combinado (experimental)
```

La opción 1 permite elegir un solo tipo de deficiencia cromática.

La opción 2 permite elegir más de un tipo, separados por coma.

Luego el sistema solicita el tipo de deficiencia:

```text
1 - Protanomalía / Protanopía
2 - Deuteranomalía / Deuteranopía
3 - Tritanomalía / Tritanopía
```

Después solicita la severidad. Se puede ingresar un valor entero de 0 a 10:

```text
0 = sin deficiencia
10 = máxima severidad / dicromacia
```

También se pueden ingresar valores decimales entre 0.0 y 1.0.

Ejemplos:

```text
7
10
0.7
1.0
```

## 10. Resultados generados

Luego del procesamiento, el programa genera dos imágenes:

```text
output/simulada.jpg
output/corregida.jpg
```

La imagen `simulada.jpg` representa una aproximación visual de cómo podría percibirse la imagen original bajo el tipo de daltonismo seleccionado.

La imagen `corregida.jpg` aplica una transformación cromática orientada a mejorar la diferenciación entre colores.

## 11. Verificación del resultado

Para comprobar el funcionamiento del proyecto se deben comparar:

1. La imagen original ubicada en `input/imagen.jpg`.
2. La imagen simulada ubicada en `output/simulada.jpg`.
3. La imagen corregida ubicada en `output/corregida.jpg`.

La transformación es verificable porque las imágenes de salida presentan cambios visibles respecto de la imagen original.

## 12. Pruebas automatizadas

El proyecto incluye una prueba básica del Core ubicada en:

```text
tests/test_core_basico.py
```

Para ejecutarla, desde la carpeta raíz del proyecto se debe usar:

```bash
python -m pytest
```

La prueba verifica que el Core pueda recibir una imagen, generar una imagen simulada y una imagen corregida, conservando el tamaño, el tipo de dato `uint8` y produciendo una transformación verificable respecto de la imagen original.

El resultado obtenido fue:

```text
1 passed
```

## 13. Decisiones técnicas

Se eligió trabajar con matrices de transformación porque permiten modificar los canales de color de manera explícita, controlada y explicable.

Este enfoque resulta adecuado para el proyecto porque:

* está directamente relacionado con procesamiento digital de imágenes;
* permite trabajar con píxeles y canales de color;
* no requiere entrenamiento de un modelo;
* es más interpretable que una solución basada en machine learning;
* permite justificar matemáticamente la transformación aplicada.

OpenCV se utiliza para el procesamiento y guardado de imágenes. Pillow se utiliza para la carga inicial y validación de la imagen.

## 14. Limitaciones

El proyecto tiene algunas limitaciones:

* La corrección no reproduce una visión normal del color.
* El resultado puede variar según la imagen utilizada.
* Algunas combinaciones de colores pueden seguir siendo difíciles de distinguir.
* El modo combinado es experimental.
* La visualización por ventanas de OpenCV puede depender del entorno donde se ejecute el programa.

## 15. Posibles mejoras futuras

Algunas mejoras posibles son:

* Permitir elegir la ruta de la imagen desde la terminal.
* Agregar argumentos por línea de comandos.
* Guardar resultados en formato PNG para evitar pérdida por compresión.
* Agregar pruebas automatizadas para validar el Core.
* Comparar varias severidades sobre una misma imagen.
* Generar una imagen comparativa con original, simulada y corregida en una sola salida.
* Permitir el modo combinado también desde la interfaz web (actualmente solo en `main.py`).
* Agregar más casos de prueba con imágenes de distintos colores y contrastes.
* Agregar pruebas automatizadas para `app.py` (los endpoints Flask).

## 16. Uso responsable de inteligencia artificial

La inteligencia artificial se utilizó como apoyo para comprender conceptos, revisar decisiones técnicas, ordenar la estructura del proyecto y mejorar la documentación. No se utilizó para reemplazar la comprensión del código ni para presentar una solución sin análisis propio.

Las decisiones técnicas fueron revisadas y adaptadas al funcionamiento real del proyecto.
