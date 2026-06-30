from __future__ import annotations

import argparse
from pathlib import Path

import cv2

from core.color_marker import ColorMarker
from core.daltonism_engine import DaltonismEngine
from core.matrix_repository import MatrixRepository
from core.models import ProcessingOptions
from core.orchestrator import ProcessingOrchestrator, VALID_RESULTS


ROOT_DIR = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Procesa una imagen para simular o asistir daltonismo.")
    parser.add_argument("input", help="Ruta de la imagen de entrada.")
    parser.add_argument("output", help="Ruta de la imagen de salida.")
    parser.add_argument("--result", choices=sorted(VALID_RESULTS), default="corrected_marked")
    parser.add_argument("--types", default="protan", help="Tipos separados por coma.")
    parser.add_argument("--severity", default="10")
    parser.add_argument("--correction-intensity", type=float, default=0.7)
    parser.add_argument("--marker-spacing", type=int, default=42)
    parser.add_argument("--marker-size", type=int, default=7)
    parser.add_argument("--without-legend", action="store_true")
    parser.add_argument(
        "--matrix-file",
        default=str(ROOT_DIR / "data" / "matrices" / "machado.xlsx"),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    image = cv2.imread(args.input)

    if image is None:
        raise SystemExit(f"No se pudo cargar la imagen: {args.input}")

    repository = MatrixRepository(args.matrix_file)
    engine = DaltonismEngine(repository)
    orchestrator = ProcessingOrchestrator(engine, ColorMarker())
    options = ProcessingOptions(
        tipos=[value.strip() for value in args.types.split(",") if value.strip()],
        severidad=args.severity,
        resultado=args.result,
        intensidad_correccion=args.correction_intensity,
        espacio_marcadores=args.marker_spacing,
        tamano_marcadores=args.marker_size,
        incluir_leyenda=not args.without_legend,
    )

    result = orchestrator.process(image, options)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not cv2.imwrite(str(output_path), result.current):
        raise SystemExit("No se pudo guardar la imagen de salida.")

    print(f"Imagen generada: {output_path}")


if __name__ == "__main__":
    main()
