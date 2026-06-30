# TFI 2026 - Procesamiento de imágenes para daltonismo

El proyecto expone un Core reutilizable para simular deficiencias de visión del color, aplicar una corrección y agregar símbolos sobre zonas de color para facilitar su identificación.

## Alcance de esta versión

- API HTTP que recibe imágenes como `multipart/form-data`.
- Procesamiento en memoria, sin depender de rutas locales.
- Simulación de protanomalía, deuteranomalía y tritanomalía.
- Corrección por redistribución del error de color.
- Marcado de colores mediante figuras repetidas y una leyenda.
- Matrices Machado externas al código.
- Soporte para CSV y XLSX.
- Pipeline de pasos y orquestador para armar cada procesamiento.
- CLI separado de la API.

## Compatibilidad

El servidor Python puede ejecutarse en Windows, Linux y macOS. Una aplicación iOS puede enviar la imagen a la API y recibir el archivo procesado.

Si se necesitara ejecutar el procesamiento completamente dentro del iPhone, sin servidor, sería otra variante del proyecto y habría que portar el Core o empaquetarlo para iOS.

## Estructura

```text
api/
  main.py                 API FastAPI
cli/
  main.py                 Entrada por consola
core/
  color_marker.py         Figuras y leyenda por color
  daltonism_engine.py     Simulación y corrección
  image_codec.py          Decodificación y codificación en memoria
  matrix_repository.py    Lectura de matrices CSV/XLSX
  models.py               Opciones y contexto
  orchestrator.py         Decide qué pipeline ejecutar
  pipeline.py             Pasos de procesamiento
data/matrices/
  machado.csv             Todas las matrices en formato tabular
  machado.xlsx            Una hoja por tipo de daltonismo
tests/
```

## Matrices

El archivo CSV utiliza estas columnas:

```text
type,severity,m00,m01,m02,m10,m11,m12,m20,m21,m22
```

El XLSX contiene las hojas:

- `protanomaly`
- `deuteranomaly`
- `tritanomaly`

Cada hoja tiene una fila por severidad. Para usar otro archivo se puede definir la variable de entorno `MATRIX_FILE`.

## Instalación

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar la API

```bash
uvicorn api.main:app --reload
```

Documentación local:

```text
http://127.0.0.1:8000/docs
```

## Endpoint principal

```text
POST /v1/images/process
```

Campos:

- `file`: imagen de entrada.
- `result`: `simulated`, `corrected`, `marked`, `simulated_marked` o `corrected_marked`.
- `types`: uno o más tipos separados por coma, por ejemplo `protan,deutan`.
- `severity`: escala de `0` a `10`. También admite un valor normalizado escrito como `0.7`.
- `correction_intensity`: intensidad de corrección.
- `marker_spacing`: distancia entre figuras.
- `marker_size`: tamaño de cada figura.
- `include_legend`: agrega la referencia entre figura y color.
- `output_format`: `png`, `jpg` o `webp`.

Ejemplo:

```bash
curl -X POST "http://127.0.0.1:8000/v1/images/process" \
  -F "file=@input/imagen.jpg" \
  -F "result=corrected_marked" \
  -F "types=deutan" \
  -F "severity=8" \
  -F "output_format=png" \
  --output output/resultado.png
```

## Ejecutar por CLI

```bash
python -m cli.main input/imagen.jpg output/resultado.png \
  --result corrected_marked \
  --types deutan \
  --severity 8
```

## Marcadores de color

La imagen se convierte a HSV y se agrupan zonas de colores saturados. Sobre cada zona se repite una figura distinta, por ejemplo:

- rojo: triángulo;
- amarillo: rombo;
- verde: círculo;
- azul: cuadrado.

No se dibuja una figura literalmente en cada píxel porque volvería ilegible la imagen. Los símbolos se distribuyen en una cuadrícula y solo se agregan cuando una parte suficiente del área pertenece al mismo grupo de color.

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest
```

### CLI con menú interactivo

Para usar el proyecto con un menú simple por consola:

```bash
python -m cli.menu
```

El menú permite elegir la imagen, el tipo de daltonismo, el resultado, la severidad y la ruta de salida. Si se presiona Enter en la ruta de entrada, usa `input/imagen.jpg`.
