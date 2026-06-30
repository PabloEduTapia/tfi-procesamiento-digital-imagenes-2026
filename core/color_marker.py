from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class ColorRule:
    name: str
    shape: str
    ranges: tuple[tuple[int, int], ...]


COLOR_RULES = (
    ColorRule("Rojo", "triangle", ((0, 9), (170, 179))),
    ColorRule("Naranja", "x", ((10, 20),)),
    ColorRule("Amarillo", "diamond", ((21, 35),)),
    ColorRule("Verde", "circle", ((36, 85),)),
    ColorRule("Cian", "plus", ((86, 100),)),
    ColorRule("Azul", "square", ((101, 130),)),
    ColorRule("Violeta", "star", ((131, 155),)),
    ColorRule("Magenta", "bars", ((156, 169),)),
)


class ColorMarker:
    """Superpone símbolos repetidos sobre zonas de color para diferenciarlas."""

    def apply(
        self,
        image: np.ndarray,
        spacing: int = 42,
        size: int = 7,
        include_legend: bool = True,
    ) -> np.ndarray:
        if spacing < 12:
            raise ValueError("El espacio entre marcadores debe ser de al menos 12 píxeles.")
        if size < 3:
            raise ValueError("El tamaño del marcador debe ser de al menos 3 píxeles.")

        result = image.copy()
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        present_rules: list[ColorRule] = []

        for rule in COLOR_RULES:
            mask = self._create_mask(hsv, rule)

            if cv2.countNonZero(mask) == 0:
                continue

            present_rules.append(rule)
            self._draw_repeated_shapes(result, mask, rule.shape, spacing, size)

        if include_legend and present_rules:
            self._draw_legend(result, present_rules)

        return result

    @staticmethod
    def _create_mask(hsv: np.ndarray, rule: ColorRule) -> np.ndarray:
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)

        # Se descartan colores casi grises o demasiado oscuros.
        for lower_h, upper_h in rule.ranges:
            current = cv2.inRange(
                hsv,
                np.array([lower_h, 65, 45], dtype=np.uint8),
                np.array([upper_h, 255, 255], dtype=np.uint8),
            )
            mask = cv2.bitwise_or(mask, current)

        kernel = np.ones((3, 3), dtype=np.uint8)
        return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    def _draw_repeated_shapes(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        shape: str,
        spacing: int,
        size: int,
    ) -> None:
        height, width = mask.shape
        half = spacing // 2

        for y in range(half, height, spacing):
            for x in range(half, width, spacing):
                y1 = max(0, y - size)
                y2 = min(height, y + size + 1)
                x1 = max(0, x - size)
                x2 = min(width, x + size + 1)
                area = mask[y1:y2, x1:x2]

                if area.size == 0 or cv2.countNonZero(area) < area.size * 0.45:
                    continue

                color = self._contrast_color(image[y, x])
                border = (255, 255, 255) if color == (0, 0, 0) else (0, 0, 0)
                self._draw_shape(image, shape, (x, y), size + 1, border, 3)
                self._draw_shape(image, shape, (x, y), size, color, 1)

    @staticmethod
    def _contrast_color(pixel: np.ndarray) -> tuple[int, int, int]:
        b, g, r = [int(value) for value in pixel]
        luminance = (0.114 * b) + (0.587 * g) + (0.299 * r)
        return (0, 0, 0) if luminance > 145 else (255, 255, 255)

    @staticmethod
    def _draw_shape(
        image: np.ndarray,
        shape: str,
        center: tuple[int, int],
        size: int,
        color: tuple[int, int, int],
        thickness: int,
    ) -> None:
        x, y = center

        if shape == "triangle":
            points = np.array([[x, y - size], [x - size, y + size], [x + size, y + size]])
            cv2.polylines(image, [points], True, color, thickness, cv2.LINE_AA)
        elif shape == "diamond":
            points = np.array([[x, y - size], [x - size, y], [x, y + size], [x + size, y]])
            cv2.polylines(image, [points], True, color, thickness, cv2.LINE_AA)
        elif shape == "circle":
            cv2.circle(image, center, size, color, thickness, cv2.LINE_AA)
        elif shape == "square":
            cv2.rectangle(image, (x - size, y - size), (x + size, y + size), color, thickness, cv2.LINE_AA)
        elif shape == "plus":
            cv2.line(image, (x - size, y), (x + size, y), color, thickness, cv2.LINE_AA)
            cv2.line(image, (x, y - size), (x, y + size), color, thickness, cv2.LINE_AA)
        elif shape == "x":
            cv2.line(image, (x - size, y - size), (x + size, y + size), color, thickness, cv2.LINE_AA)
            cv2.line(image, (x - size, y + size), (x + size, y - size), color, thickness, cv2.LINE_AA)
        elif shape == "bars":
            cv2.line(image, (x - size // 2, y - size), (x - size // 2, y + size), color, thickness, cv2.LINE_AA)
            cv2.line(image, (x + size // 2, y - size), (x + size // 2, y + size), color, thickness, cv2.LINE_AA)
        else:
            points = []
            for index in range(8):
                radius = size if index % 2 == 0 else max(2, size // 2)
                angle = np.deg2rad(-90 + (index * 45))
                points.append([int(x + radius * np.cos(angle)), int(y + radius * np.sin(angle))])
            cv2.polylines(image, [np.array(points)], True, color, thickness, cv2.LINE_AA)

    def _draw_legend(self, image: np.ndarray, rules: list[ColorRule]) -> None:
        row_height = 25
        width = min(190, image.shape[1])
        height = min(12 + (row_height * len(rules)), image.shape[0])
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (width, height), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.72, image, 0.28, 0, image)

        for index, rule in enumerate(rules):
            y = 18 + (index * row_height)
            self._draw_shape(image, rule.shape, (14, y - 4), 6, (255, 255, 255), 1)
            cv2.putText(
                image,
                rule.name,
                (28, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )
