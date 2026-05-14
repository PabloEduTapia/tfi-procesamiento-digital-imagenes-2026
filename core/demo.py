"""Utilidades para generar una imagen de prueba controlada."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def crear_imagen_demo(ruta_salida: str | Path) -> Path:
    """
    Genera una imagen simple con colores y formas.

    Sirve para ejecutar el proyecto aunque todavía no se haya cargado una foto
    propia en la carpeta input.
    """

    ruta = Path(ruta_salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    ancho, alto = 900, 520
    img = Image.new("RGB", (ancho, alto), "white")
    draw = ImageDraw.Draw(img)

    colores = [
        (220, 40, 40),
        (40, 160, 70),
        (40, 90, 220),
        (240, 190, 40),
        (180, 60, 180),
        (40, 190, 190),
    ]

    margen = 45
    celda_w = (ancho - margen * 2) // 3
    celda_h = 150

    for i, color in enumerate(colores):
        fila = i // 3
        col = i % 3
        x1 = margen + col * celda_w
        y1 = 80 + fila * 190
        x2 = x1 + celda_w - 20
        y2 = y1 + celda_h
        draw.rounded_rectangle((x1, y1, x2, y2), radius=20, fill=color, outline=(30, 30, 30), width=3)
        draw.text((x1 + 20, y2 + 12), f"Color {i + 1}", fill=(0, 0, 0))

    draw.text((margen, 25), "Imagen demo para simulacion y correccion de daltonismo", fill=(0, 0, 0))
    draw.line((margen, 55, ancho - margen, 55), fill=(80, 80, 80), width=2)

    img.save(ruta)
    return ruta
