"""
Aplicación de Procesamiento Digital de Imágenes - Daltonismo

Tiene dos formas de ejecución:

1) Automática:
   Genera resultados para protanopia, deuteranopia y tritanopia.

2) Manual:
   Permite indicar parámetros por consola: tipo de daltonismo, acción,
   brillo, contraste, filtros, tamaño, etc.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2

from core.daltonismo import TIPOS_DALTONISMO
from core.demo import crear_imagen_demo
from core.pipeline import PipelineImagen, crear_comparativa


INPUT_DEMO = Path("input/demo_colores.jpg")
OUTPUT_DIR = Path("output")


def resolver_imagen_entrada(ruta: str | None) -> Path:
    """Devuelve la ruta de entrada. Si no existe, crea una imagen demo."""

    if ruta:
        entrada = Path(ruta)
        if not entrada.exists():
            raise FileNotFoundError(f"No existe la imagen indicada: {entrada}")
        return entrada

    if not INPUT_DEMO.exists():
        crear_imagen_demo(INPUT_DEMO)

    return INPUT_DEMO


def aplicar_parametros_comunes(pipeline: PipelineImagen, args: argparse.Namespace) -> PipelineImagen:
    """Aplica parámetros opcionales compartidos entre modo automático y manual."""

    if args.ancho or args.alto:
        pipeline.redimensionar(ancho=args.ancho, alto=args.alto)

    if args.brillo != 1.0:
        pipeline.brillo(args.brillo)

    if args.contraste != 1.0:
        pipeline.contraste(args.contraste)

    if args.saturacion != 1.0:
        pipeline.saturacion(args.saturacion)

    if args.gaussiano:
        pipeline.desenfoque_gaussiano(args.gaussiano)

    if args.nitidez:
        pipeline.nitidez(args.nitidez)

    return pipeline


def ejecutar_automatico(args: argparse.Namespace) -> None:
    """Ejecuta un flujo completo para todos los tipos de daltonismo."""

    entrada = resolver_imagen_entrada(args.input)
    OUTPUT_DIR.mkdir(exist_ok=True)

    tipos = args.tipos or list(TIPOS_DALTONISMO.keys())

    for tipo in tipos:
        original = aplicar_parametros_comunes(PipelineImagen(entrada), args)

        simulada = original.clonar().simular_daltonismo(tipo)
        corregida = original.clonar().corregir_daltonismo(tipo, intensidad=args.intensidad)

        ruta_simulada = OUTPUT_DIR / f"{tipo}_simulada.jpg"
        ruta_corregida = OUTPUT_DIR / f"{tipo}_corregida.jpg"
        ruta_comparativa = OUTPUT_DIR / f"{tipo}_comparativa.jpg"

        simulada.guardar(ruta_simulada)
        corregida.guardar(ruta_corregida)

        comparativa = crear_comparativa(
            [original.imagen, simulada.imagen, corregida.imagen],
            ["Original", f"Simulada {tipo}", f"Corregida {tipo}"],
        )
        cv2.imwrite(str(ruta_comparativa), comparativa)

        print(f"OK {tipo}: {ruta_comparativa}")

    print("Procesamiento automatico finalizado")


def ejecutar_manual(args: argparse.Namespace) -> None:
    """Ejecuta una única operación elegida por el usuario."""

    entrada = resolver_imagen_entrada(args.input)
    salida = Path(args.output or OUTPUT_DIR / "manual_resultado.jpg")

    pipeline = aplicar_parametros_comunes(PipelineImagen(entrada), args)

    if args.accion == "simular":
        pipeline.simular_daltonismo(args.tipo)
    elif args.accion == "corregir":
        pipeline.corregir_daltonismo(args.tipo, intensidad=args.intensidad)
    elif args.accion == "bordes":
        pipeline.bordes(args.umbral1, args.umbral2)
    elif args.accion == "grises":
        pipeline.escala_grises()
    elif args.accion == "umbral":
        pipeline.umbral(args.valor_umbral)
    elif args.accion == "contornos":
        pipeline.contornos(args.valor_umbral)
    elif args.accion == "emboss":
        pipeline.emboss()
    else:
        raise ValueError(f"Acción no soportada: {args.accion}")

    pipeline.guardar(salida)

    print(f"Imagen procesada: {salida}")
    print("Pasos aplicados:")
    for paso in pipeline.pasos:
        print(f"- {paso}")

    if args.mostrar:
        cv2.imshow("Resultado", pipeline.imagen)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Procesamiento de imágenes para simulación y corrección de daltonismo"
    )

    parser.add_argument("--modo", choices=["auto", "manual"], default="auto", help="Modo de ejecución")
    parser.add_argument("--input", help="Ruta de la imagen de entrada")
    parser.add_argument("--output", help="Ruta de salida para modo manual")

    parser.add_argument("--tipo", choices=list(TIPOS_DALTONISMO.keys()), default="protanopia")
    parser.add_argument("--tipos", nargs="+", choices=list(TIPOS_DALTONISMO.keys()), help="Tipos a procesar en modo auto")
    parser.add_argument(
        "--accion",
        choices=["simular", "corregir", "bordes", "grises", "umbral", "contornos", "emboss"],
        default="corregir",
        help="Acción a ejecutar en modo manual",
    )

    parser.add_argument("--intensidad", type=float, default=0.70, help="Intensidad de corrección entre 0 y 1")
    parser.add_argument("--ancho", type=int, help="Ancho final de la imagen")
    parser.add_argument("--alto", type=int, help="Alto final de la imagen")
    parser.add_argument("--brillo", type=float, default=1.0, help="Factor de brillo Pillow")
    parser.add_argument("--contraste", type=float, default=1.0, help="Factor de contraste Pillow")
    parser.add_argument("--saturacion", type=float, default=1.0, help="Factor de saturación Pillow")
    parser.add_argument("--gaussiano", type=int, help="Kernel para desenfoque gaussiano")
    parser.add_argument("--nitidez", type=float, help="Intensidad de nitidez")
    parser.add_argument("--umbral1", type=int, default=80, help="Umbral inferior de Canny")
    parser.add_argument("--umbral2", type=int, default=160, help="Umbral superior de Canny")
    parser.add_argument("--valor-umbral", type=int, default=127, help="Valor para umbralización")
    parser.add_argument("--mostrar", action="store_true", help="Muestra ventana con el resultado")

    return parser


def main() -> None:
    parser = crear_parser()
    args = parser.parse_args()

    if args.modo == "auto":
        ejecutar_automatico(args)
    else:
        ejecutar_manual(args)


if __name__ == "__main__":
    main()
