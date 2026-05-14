# Aplicación de Procesamiento Digital de Imágenes - Daltonismo

Proyecto para el Trabajo Final Integrador 2026 de **Técnicas de Procesamiento Digital de Imágenes**.

La aplicación recibe una imagen real, aplica técnicas de procesamiento digital de imágenes y genera nuevas imágenes procesadas. El caso elegido es la **simulación y corrección visual para distintos tipos de daltonismo**.

## Problema elegido

Algunas combinaciones de colores pueden ser difíciles de distinguir para personas con daltonismo. El proyecto permite:

- Simular cómo se vería una imagen con protanopía, deuteranopía o tritanopía.
- Generar una versión corregida donde se refuerzan canales de color para mejorar la diferenciación.
- Comparar la imagen original, simulada y corregida.

## Estructura del proyecto

```text
proyecto_daltonismo/
├── core/
│   ├── daltonismo.py      # Lógica específica de simulación y corrección
│   ├── pipeline.py        # Pipeline reutilizable con OpenCV y Pillow
│   └── demo.py            # Generador de imagen demo
├── docs/
│   └── informe.md         # Documentación técnica del proyecto
├── input/
│   └── demo_colores.jpg   # Se genera automáticamente si no existe
├── output/
│   └── resultados generados
├── tests/
│   └── test_core.py       # Tests básicos del Core
├── main.py                # Entrada por consola: modo automático y manual
├── requirements.txt
└── README.md
```

## Instalación

```bash
python -m venv .venv
.venv\Scriptsctivate
pip install -r requirements.txt
```

En Linux/Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución automática

Genera resultados para los tres tipos de daltonismo:

```bash
python main.py --modo auto
```

También se puede indicar una imagen propia:

```bash
python main.py --modo auto --input input/mi_imagen.jpg
```

Ejemplo con parámetros adicionales:

```bash
python main.py --modo auto --input input/mi_imagen.jpg --ancho 900 --contraste 1.15 --intensidad 0.8
```

Salida esperada en `output/`:

```text
protanopia_simulada.jpg
protanopia_corregida.jpg
protanopia_comparativa.jpg
deuteranopia_simulada.jpg
deuteranopia_corregida.jpg
deuteranopia_comparativa.jpg
tritanopia_simulada.jpg
tritanopia_corregida.jpg
tritanopia_comparativa.jpg
```

## Ejecución manual con parámetros

Simular protanopía:

```bash
python main.py --modo manual --accion simular --tipo protanopia --input input/mi_imagen.jpg --output output/simulada.jpg
```

Corregir deuteranopía con intensidad personalizada:

```bash
python main.py --modo manual --accion corregir --tipo deuteranopia --intensidad 0.75 --input input/mi_imagen.jpg --output output/corregida.jpg
```

Aplicar bordes:

```bash
python main.py --modo manual --accion bordes --umbral1 60 --umbral2 180 --input input/mi_imagen.jpg --output output/bordes.jpg
```

Aplicar escala de grises:

```bash
python main.py --modo manual --accion grises --input input/mi_imagen.jpg --output output/grises.jpg
```

## Uso del pipeline en código

La clase `PipelineImagen` mantiene la lógica trabajada en clase: cada método devuelve `self`, por eso se pueden encadenar operaciones.

```python
from core.pipeline import PipelineImagen

(
    PipelineImagen("input/mi_imagen.jpg")
    .redimensionar(ancho=900)
    .brillo(1.05)
    .contraste(1.20)
    .simular_daltonismo("protanopia")
    .guardar("output/resultado.jpg")
)
```

## Técnicas utilizadas

- Lectura y escritura de imágenes con OpenCV.
- Conversión de espacios de color BGR/RGB.
- Aplicación de matrices de transformación de color.
- Corrección basada en diferencia entre imagen original e imagen simulada.
- Ajuste de brillo, contraste y saturación con Pillow.
- Filtros espaciales: desenfoque, nitidez, bordes y emboss.
- Segmentación básica: umbralización y detección de contornos.
- Pipeline orientado a objetos y reutilizable.

## Tests

```bash
pytest
```

## Recomendación para el repositorio

No subir la carpeta `.venv` al repositorio. Cada integrante puede crear su propio entorno virtual usando `requirements.txt`.
