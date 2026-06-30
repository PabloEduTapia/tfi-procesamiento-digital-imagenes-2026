from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from core.color_marker import ColorMarker
from core.daltonism_engine import DaltonismEngine
from core.matrix_repository import MatrixRepository
from core.models import ProcessingOptions
from core.orchestrator import ProcessingOrchestrator


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT_DIR / "input" / "imagen.jpg"
DEFAULT_OUTPUT = ROOT_DIR / "output" / "comparativa.png"
MATRIX_FILE = ROOT_DIR / "data" / "matrices" / "machado.xlsx"

TIPOS = {
    "1": ("Protanomalia", ["protan"]),
    "2": ("Deuteranomalia", ["deutan"]),
    "3": ("Tritanomalia", ["tritan"]),
    "4": ("Combinado", ["protan", "deutan", "tritan"]),
}


def mostrar_menu(titulo: str, opciones: dict[str, tuple]) -> None:
    print(f"\n{titulo}")
    print("-" * len(titulo))

    for numero, opcion in opciones.items():
        print(f"{numero}. {opcion[0]}")


def pedir_opcion(mensaje: str, opciones: dict[str, tuple]) -> str:
    while True:
        valor = input(mensaje).strip()

        if valor in opciones:
            return valor

        print("Opcion no valida. Intente nuevamente.")


def pedir_severidad() -> float:
    while True:
        valor = input("Severidad de 0 a 10 [10]: ").strip() or "10"

        try:
            severidad = float(valor.replace(",", "."))
        except ValueError:
            print("La severidad debe ser numerica.")
            continue

        if 0 <= severidad <= 10:
            return severidad

        print("La severidad debe estar entre 0 y 10.")


def pedir_ruta_imagen() -> Path:
    valor = input(f"Ruta de la imagen [{DEFAULT_INPUT}]: ").strip()
    return Path(valor) if valor else DEFAULT_INPUT


def pedir_ruta_salida() -> Path:
    valor = input(f"Ruta de salida [{DEFAULT_OUTPUT}]: ").strip()
    return Path(valor) if valor else DEFAULT_OUTPUT


def crear_orquestador() -> ProcessingOrchestrator:
    repository = MatrixRepository(MATRIX_FILE)
    engine = DaltonismEngine(repository)
    return ProcessingOrchestrator(engine, ColorMarker())


def procesar_resultado(
    orchestrator: ProcessingOrchestrator,
    image: np.ndarray,
    tipos: list[str],
    severidad: float,
    resultado: str,
) -> np.ndarray:
    options = ProcessingOptions(
        tipos=tipos,
        severidad=severidad,
        resultado=resultado,
    )

    context = orchestrator.process(image, options)
    return context.current


def redimensionar(image: np.ndarray, ancho_final: int = 480) -> np.ndarray:
    alto, ancho = image.shape[:2]
    escala = ancho_final / ancho
    nuevo_alto = int(alto * escala)
    return cv2.resize(image, (ancho_final, nuevo_alto), interpolation=cv2.INTER_AREA)


def agregar_titulo(image: np.ndarray, titulo: str) -> np.ndarray:
    alto_barra = 42
    alto, ancho = image.shape[:2]

    result = np.zeros((alto + alto_barra, ancho, 3), dtype=np.uint8)
    result[alto_barra:, :] = image

    cv2.putText(
        result,
        titulo,
        (14, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    return result


def armar_comparativa(
    original: np.ndarray,
    simulada: np.ndarray,
    corregida: np.ndarray,
    marcada: np.ndarray,
) -> np.ndarray:
    original = agregar_titulo(redimensionar(original), "Original")
    simulada = agregar_titulo(redimensionar(simulada), "Simulada")
    corregida = agregar_titulo(redimensionar(corregida), "Corregida")
    marcada = agregar_titulo(redimensionar(marcada), "Marcada")

    fila_1 = np.hstack([original, simulada])
    fila_2 = np.hstack([corregida, marcada])

    return np.vstack([fila_1, fila_2])


def procesar_comparativa(orchestrator: ProcessingOrchestrator) -> None:
    ruta_imagen = pedir_ruta_imagen()
    image = cv2.imread(str(ruta_imagen))

    if image is None:
        print(f"No se pudo cargar la imagen: {ruta_imagen}")
        return

    mostrar_menu("Tipo de daltonismo", TIPOS)
    tipo_elegido = pedir_opcion("Seleccione una opcion: ", TIPOS)

    tipos = TIPOS[tipo_elegido][1]
    severidad = pedir_severidad()
    ruta_salida = pedir_ruta_salida()

    simulada = procesar_resultado(orchestrator, image, tipos, severidad, "simulated")
    corregida = procesar_resultado(orchestrator, image, tipos, severidad, "corrected")
    marcada = procesar_resultado(orchestrator, image, tipos, severidad, "marked")

    comparativa = armar_comparativa(
        original=image,
        simulada=simulada,
        corregida=corregida,
        marcada=marcada,
    )

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    if not cv2.imwrite(str(ruta_salida), comparativa):
        print("No se pudo guardar la imagen de salida.")
        return

    print(f"\nComparativa generada: {ruta_salida}")


def main() -> None:
    print("Procesamiento de imagenes para daltonismo")
    orchestrator = crear_orquestador()

    while True:
        print("\n1. Generar comparativa completa")
        print("0. Salir")
        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "0":
            print("Programa finalizado.")
            break

        if opcion == "1":
            try:
                procesar_comparativa(orchestrator)
            except (ValueError, FileNotFoundError) as error:
                print(f"Error: {error}")
        else:
            print("Opcion no valida.")


if __name__ == "__main__":
    main()
