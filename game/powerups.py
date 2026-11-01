"""Recompensas de vida y apariciones de energía."""

import random
from collections.abc import Iterable

from settings import LIFE_REWARD_SCORES

from .snake import Position


class LifeRewards:
    """Mantiene las recompensas de puntuación pendientes hasta poder recogerlas."""

    def __init__(self) -> None:
        self._next_reward_index = 0
        self.pending = 0
        self.position: Position | None = None

    def reset(self) -> None:
        self._next_reward_index = 0
        self.pending = 0
        self.position = None

    def update_score(self, score: int) -> None:
        while (
            self._next_reward_index < len(LIFE_REWARD_SCORES)
            and score >= LIFE_REWARD_SCORES[self._next_reward_index]
        ):
            self.pending += 1
            self._next_reward_index += 1

    def try_spawn(
        self,
        lives: int,
        max_lives: int,
        columns: int,
        rows: int,
        occupied: Iterable[Position],
    ) -> None:
        if self.position is not None or self.pending == 0 or lives >= max_lives:
            return

        blocked = set(occupied)
        available = [
            (x, y)
            for y in range(rows)
            for x in range(columns)
            if (x, y) not in blocked
        ]
        self.position = random.choice(available) if available else None
