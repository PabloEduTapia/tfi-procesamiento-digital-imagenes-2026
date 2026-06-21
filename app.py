"""
app.py — Servidor web para el editor de imágenes para daltónicos.

Este archivo es la capa de interfaz web. No contiene lógica de procesamiento
de imágenes: toda la transformación de píxeles sigue viviendo en core/.

Arquitectura:
    Frontend (templates/index.html + static/)
        --> POST /procesar
            --> app.py: valida la subida, decodifica la imagen
                --> core.combinado.Combinado: simula y corrige (sin cambios)
            <-- devuelve las 3 imágenes (original, simulada, corregida) en base64
        <-- el navegador las muestra lado a lado, sin recargar la página

Ejecución local:
    pip install -r requirements.txt
    python app.py
    abrir http://127.0.0.1:5000
"""

import base64
import logging

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request
from PIL import Image

from core.combinado import Combinado
from core.matrices_machado import NOMBRES_LEGIBLES, normalizar_severidad

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Tamaño máximo de subida: 8 MB. Evita que una imagen enorme cuelgue el server.
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "bmp", "webp"}

# Ancho máximo de trabajo. Las imágenes más grandes se reducen antes de
# procesar: la transformación matricial es por píxel, así que el costo
# crece con la cantidad de píxeles, no con el tipo de operación.
ANCHO_MAXIMO = 900


def extension_permitida(nombre_archivo: str) -> bool:
    """Verifica que el archivo subido tenga una extensión de imagen soportada."""
    return (
        "." in nombre_archivo
        and nombre_archivo.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS
    )


def archivo_a_imagen_bgr(archivo) -> np.ndarray:
    """Convierte un archivo subido (FileStorage) a un array BGR para OpenCV.

    Reusa el mismo criterio que main.py: Pillow abre y normaliza a RGB,
    luego se convierte a BGR porque el Core (core/daltonismo.py) espera
    ese formato.

    Args:
        archivo: objeto FileStorage de Flask (request.files[...]).

    Returns:
        Array NumPy uint8 en formato BGR, shape (alto, ancho, 3).

    Raises:
        ValueError: si el archivo no puede abrirse como imagen.
    """
    try:
        imagen_pil = Image.open(archivo.stream).convert("RGB")
    except Exception as ex:
        raise ValueError(f"No se pudo leer la imagen: {ex}")

    imagen_rgb = np.array(imagen_pil)
    return cv2.cvtColor(imagen_rgb, cv2.COLOR_RGB2BGR)


def redimensionar_si_corresponde(imagen_bgr: np.ndarray) -> np.ndarray:
    """Reduce la imagen si excede el ancho máximo de trabajo.

    Mantiene la relación de aspecto. No agranda imágenes pequeñas.
    """
    alto, ancho = imagen_bgr.shape[:2]
    if ancho <= ANCHO_MAXIMO:
        return imagen_bgr

    factor = ANCHO_MAXIMO / ancho
    nuevo_alto = int(alto * factor)
    return cv2.resize(imagen_bgr, (ANCHO_MAXIMO, nuevo_alto))


def imagen_bgr_a_base64(imagen_bgr: np.ndarray) -> str:
    """Codifica un array BGR como PNG en base64, listo para un <img src>.

    PNG en vez de JPG para no perder calidad por compresión con pérdida
    en una imagen que ya fue transformada matemáticamente.
    """
    ok, buffer = cv2.imencode(".png", imagen_bgr)
    if not ok:
        raise ValueError("No se pudo codificar la imagen de salida.")
    texto_base64 = base64.b64encode(buffer).decode("ascii")
    return f"data:image/png;base64,{texto_base64}"


@app.route("/")
def index():
    """Sirve la página principal con el formulario de carga."""
    tipos_para_template = [
        {"valor": "protan", "etiqueta": NOMBRES_LEGIBLES["protanomaly"]},
        {"valor": "deutan", "etiqueta": NOMBRES_LEGIBLES["deuteranomaly"]},
        {"valor": "tritan", "etiqueta": NOMBRES_LEGIBLES["tritanomaly"]},
    ]
    return render_template("index.html", tipos=tipos_para_template)


@app.route("/procesar", methods=["POST"])
def procesar():
    """Recibe imagen + tipo + severidad, devuelve las 3 imágenes resultantes.

    Request (multipart/form-data):
        imagen: archivo de imagen.
        tipo: uno de 'protan', 'deutan', 'tritan'.
        severidad: entero de 0 a 10 (texto).

    Response (JSON):
        { "original": "data:image/png;base64,...",
          "simulada": "data:image/png;base64,...",
          "corregida": "data:image/png;base64,..." }
        o { "error": "mensaje" } con status 400.
    """
    archivo = request.files.get("imagen")
    if archivo is None or archivo.filename == "":
        return jsonify({"error": "No se recibió ninguna imagen."}), 400

    if not extension_permitida(archivo.filename):
        return jsonify({
            "error": f"Formato no soportado. Use: {', '.join(sorted(EXTENSIONES_PERMITIDAS))}."
        }), 400

    tipo = request.form.get("tipo", "")
    severidad_texto = request.form.get("severidad", "")

    try:
        imagen_bgr = archivo_a_imagen_bgr(archivo)
        imagen_bgr = redimensionar_si_corresponde(imagen_bgr)

        severidad = normalizar_severidad(severidad_texto)
        # Combinado acepta una lista de tipos: aquí siempre llega uno solo,
        # porque el formulario usa radio buttons (un tipo por vez).
        procesador = Combinado([tipo], severidad)

        simulada_bgr = procesador.simular(imagen_bgr)
        corregida_bgr = procesador.corregir(imagen_bgr)

    except ValueError as ex:
        logger.warning("Solicitud inválida: %s", ex)
        return jsonify({"error": str(ex)}), 400
    except Exception:
        logger.exception("Error inesperado al procesar la imagen")
        return jsonify({"error": "Ocurrió un error inesperado al procesar la imagen."}), 500

    return jsonify({
        "original": imagen_bgr_a_base64(imagen_bgr),
        "simulada": imagen_bgr_a_base64(simulada_bgr),
        "corregida": imagen_bgr_a_base64(corregida_bgr),
    })


@app.errorhandler(413)
def archivo_demasiado_grande(_error):
    """Mensaje claro cuando la imagen supera MAX_CONTENT_LENGTH."""
    return jsonify({"error": "La imagen es demasiado grande. Máximo 8 MB."}), 413


if __name__ == "__main__":
    app.run(debug=True, port=5000)
