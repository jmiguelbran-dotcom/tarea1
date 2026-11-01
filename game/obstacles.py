"""Generación y progresión de obstáculos en la cuadrícula."""

import random
from collections.abc import Iterable

from settings import OBSTACLES_BY_LEVEL

from .snake import Position


class ObstacleField:
    """Conserva los obstáculos colocados y los amplía al subir de nivel."""

    def __init__(self) -> None:
        self.positions: set[Position] = set()

    def reset(self) -> None:
        self.positions.clear()

    def grow_to_level(
        self,
        level: int,
        columns: int,
        rows: int,
        occupied: Iterable[Position],
        head: Position,
    ) -> None:
        target_count = OBSTACLES_BY_LEVEL[min(max(level, 1), len(OBSTACLES_BY_LEVEL)) - 1]
        missing = target_count - len(self.positions)
        if missing <= 0:
            return

        blocked = set(occupied) | self.positions
        candidates = [
            (x, y)
            for y in range(rows)
            for x in range(columns)
            if (x, y) not in blocked
            and abs(x - head[0]) + abs(y - head[1]) > 2
        ]
        random.shuffle(candidates)
        self.positions.update(candidates[:missing])
