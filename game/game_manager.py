"""Estado y reglas de una partida de Orbit Snake."""

import random

from settings import (
    BOARD_COLUMNS,
    BOARD_ROWS,
    INITIAL_LIVES,
    INVULNERABILITY_SECONDS,
    LEVEL_SCORE_THRESHOLDS,
    MAX_LIVES,
    VICTORY_SCORE,
)

from .obstacles import ObstacleField
from .powerups import LifeRewards
from .snake import Position, Snake, StepResult


class GameManager:
    """Administra la serpiente, la comida, la puntuación y el fin de partida."""

    def __init__(
        self,
        columns: int = BOARD_COLUMNS,
        rows: int = BOARD_ROWS,
        victory_score: int = VICTORY_SCORE,
    ) -> None:
        if columns < 4 or rows < 1:
            raise ValueError("El tablero debe permitir una serpiente de tres segmentos.")
        if victory_score < 1:
            raise ValueError("La puntuacion objetivo debe ser mayor que cero.")

        self.columns = columns
        self.rows = rows
        self.victory_score = victory_score
        self.reset()

    def reset(self) -> None:
        self.snake = Snake(self.columns, self.rows)
        self.score = 0
        self.lives = INITIAL_LIVES
        self.game_over = False
        self.won = False
        self.invulnerability_remaining = 0.0
        self.obstacles = ObstacleField()
        self.life_rewards = LifeRewards()
        self.food: Position | None = self._spawn_food()

    @property
    def level(self) -> int:
        for index in range(len(LEVEL_SCORE_THRESHOLDS) - 1, -1, -1):
            if self.score >= LEVEL_SCORE_THRESHOLDS[index]:
                return index + 1
        return 1

    @property
    def speed(self) -> int:
        return self.level + 4

    @property
    def life_pickup(self) -> Position | None:
        return self.life_rewards.position

    @property
    def pending_life_rewards(self) -> int:
        return self.life_rewards.pending

    def advance_time(self, elapsed: float) -> None:
        self.invulnerability_remaining = max(
            0.0,
            self.invulnerability_remaining - max(0.0, elapsed),
        )

    def step(self) -> StepResult | None:
        if self.game_over or self.won:
            return None

        if self.food is None:
            self.won = True
            return None

        result = self.snake.advance(
            self.food,
            self.columns,
            self.rows,
            obstacles=self.obstacles.positions,
            life_pickup=self.life_pickup,
        )
        if result is StepResult.COLLISION:
            if self.invulnerability_remaining > 0:
                if not self._redirect_to_safe_path():
                    self._respawn_snake(set(self.snake.segments))
                return StepResult.PROTECTED
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                return result
            self._respawn_snake(set(self.snake.segments))
            self.invulnerability_remaining = INVULNERABILITY_SECONDS
            self._try_spawn_life_reward()
            return result

        if result is StepResult.ATE:
            self.score += 1
            self.life_rewards.update_score(self.score)
            self.obstacles.grow_to_level(
                self.level,
                self.columns,
                self.rows,
                self.snake.segments
                + ([self.food] if self.food is not None else [])
                + ([self.life_pickup] if self.life_pickup is not None else []),
                self.snake.segments[0],
            )
            self.food = self._spawn_food()
            if self.food is None or (
                self.level == 10 and self.score >= self.victory_score
            ):
                self.won = True
            self._try_spawn_life_reward()
        elif result is StepResult.LIFE_COLLECTED:
            self.lives = min(MAX_LIVES, self.lives + 1)
            self.life_rewards.position = None
            self.life_rewards.pending -= 1
            self._try_spawn_life_reward()

        return result

    def _respawn_snake(self, excluded: set[Position] | None = None) -> None:
        unavailable = self.obstacles.positions | {
            position
            for position in (self.food, self.life_pickup)
            if position is not None
        }
        unavailable.update(excluded or ())
        candidates: list[tuple[list[Position], tuple[int, int]]] = []
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))

        for y in range(self.rows):
            for x in range(self.columns):
                for direction in directions:
                    next_head = (x + direction[0], y + direction[1])
                    segments = [
                        (x - index * direction[0], y - index * direction[1])
                        for index in range(3)
                    ]
                    if all(
                        0 <= segment_x < self.columns
                        and 0 <= segment_y < self.rows
                        and (segment_x, segment_y) not in unavailable
                        for segment_x, segment_y in segments
                    ) and (
                        0 <= next_head[0] < self.columns
                        and 0 <= next_head[1] < self.rows
                        and next_head not in unavailable
                    ):
                        candidates.append((segments, direction))

        if not candidates:
            raise RuntimeError("No hay espacio seguro para reaparecer en el tablero.")

        segments, direction = random.choice(candidates)
        self.snake = Snake(self.columns, self.rows)
        self.snake.segments = segments
        self.snake.direction = direction
        self._try_spawn_life_reward()

    def _redirect_to_safe_path(self) -> bool:
        head_x, head_y = self.snake.segments[0]
        dx, dy = self.snake.direction
        for direction in ((-dy, dx), (dy, -dx)):
            next_head = (head_x + direction[0], head_y + direction[1])
            if not (0 <= next_head[0] < self.columns and 0 <= next_head[1] < self.rows):
                continue
            if next_head in self.obstacles.positions:
                continue

            body_to_check = (
                self.snake.segments
                if next_head == self.food
                else self.snake.segments[:-1]
            )
            if next_head in body_to_check:
                continue
            return self.snake.redirect(direction)

        return False

    def _try_spawn_life_reward(self) -> None:
        occupied = (
            self.snake.segments
            + list(self.obstacles.positions)
            + ([self.food] if self.food is not None else [])
        )
        self.life_rewards.try_spawn(
            self.lives,
            MAX_LIVES,
            self.columns,
            self.rows,
            occupied,
        )

    def _spawn_food(self) -> Position | None:
        occupied = set(self.snake.segments) | self.obstacles.positions
        if self.life_pickup is not None:
            occupied.add(self.life_pickup)
        available = [
            (x, y)
            for y in range(self.rows)
            for x in range(self.columns)
            if (x, y) not in occupied
        ]
        return random.choice(available) if available else None
