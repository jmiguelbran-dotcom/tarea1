"""Modelo y movimiento de la serpiente."""

from collections import deque
from collections.abc import Collection
from enum import Enum, auto

Position = tuple[int, int]
Direction = tuple[int, int]

UP: Direction = (0, -1)
DOWN: Direction = (0, 1)
LEFT: Direction = (-1, 0)
RIGHT: Direction = (1, 0)


class StepResult(Enum):
    MOVED = auto()
    ATE = auto()
    LIFE_COLLECTED = auto()
    COLLISION = auto()
    PROTECTED = auto()


class Snake:
    """Serpiente basada en segmentos de una cuadrícula."""

    def __init__(self, columns: int, rows: int) -> None:
        if columns < 4 or rows < 1:
            raise ValueError("El tablero debe permitir una serpiente de tres segmentos.")

        center_x = columns // 2
        center_y = rows // 2
        self.segments: list[Position] = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y),
        ]
        self.direction = RIGHT
        self._turn_queue: deque[Direction] = deque()

    def turn(self, direction: Direction) -> bool:
        """Encola un giro válido sin permitir invertir el sentido."""
        last_direction = self._turn_queue[-1] if self._turn_queue else self.direction
        if len(self._turn_queue) >= 2:
            return False
        if direction == (0, 0):
            return False
        if direction == (-last_direction[0], -last_direction[1]):
            return False

        self._turn_queue.append(direction)
        return True

    def redirect(self, direction: Direction) -> bool:
        """Cambia inmediatamente a una dirección segura sin invertir el rumbo."""
        if direction == (0, 0) or direction == (-self.direction[0], -self.direction[1]):
            return False

        self.direction = direction
        self._turn_queue.clear()
        return True

    def advance(
        self,
        food: Position,
        columns: int,
        rows: int,
        obstacles: Collection[Position] = (),
        life_pickup: Position | None = None,
    ) -> StepResult:
        if self._turn_queue:
            self.direction = self._turn_queue.popleft()

        head_x, head_y = self.segments[0]
        next_head = (head_x + self.direction[0], head_y + self.direction[1])
        eating = next_head == food
        collecting_life = next_head == life_pickup

        if not (0 <= next_head[0] < columns and 0 <= next_head[1] < rows):
            return StepResult.COLLISION
        if next_head in obstacles:
            return StepResult.COLLISION

        body_to_check = self.segments if eating else self.segments[:-1]
        if next_head in body_to_check:
            return StepResult.COLLISION

        self.segments.insert(0, next_head)
        if not eating:
            self.segments.pop()
        if collecting_life:
            return StepResult.LIFE_COLLECTED
        if not eating:
            return StepResult.MOVED
        return StepResult.ATE
