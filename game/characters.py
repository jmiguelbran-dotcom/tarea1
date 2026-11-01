"""Apariencias originales para personalizar la serpiente."""

from dataclasses import dataclass

Color = tuple[int, int, int]


@dataclass(frozen=True)
class SnakeStyle:
    name: str
    description: str
    head_color: Color
    body_color: Color
    accent_color: Color


STYLES = (
    SnakeStyle(
        "NEXO",
        "Campo protector",
        (195, 228, 255),
        (48, 132, 220),
        (95, 183, 255),
    ),
    SnakeStyle(
        "SOLARIA",
        "Pulso luminoso",
        (255, 242, 170),
        (220, 180, 35),
        (255, 220, 70),
    ),
    SnakeStyle(
        "BRASA",
        "Energia de impacto",
        (255, 190, 192),
        (205, 55, 72),
        (245, 100, 115),
    ),
    SnakeStyle(
        "FULGOR",
        "Destellos de energia",
        (255, 215, 165),
        (230, 118, 35),
        (255, 160, 65),
    ),
    SnakeStyle(
        "GAIA",
        "Vinculo natural",
        (190, 245, 195),
        (70, 170, 104),
        (110, 225, 140),
    ),
    SnakeStyle(
        "VESPER",
        "Control de sombras",
        (225, 195, 250),
        (130, 75, 180),
        (190, 120, 235),
    ),
)
