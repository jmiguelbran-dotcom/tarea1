import unittest
from unittest.mock import patch

from main import direction_from_swipe, game_swipe_direction, touch_position
from game.characters import STYLES
from game import game_manager as game_manager_module
from game.game_manager import GameManager
from game.obstacles import ObstacleField
from game.screens import (
    MENU_CREDITS,
    MENU_EXIT,
    MENU_INSTRUCTIONS,
    MENU_PLAY,
    INTRO_CONTINUE,
    INTRO_PAGE_COUNT,
    INTRO_SKIP,
    ScreenState,
    build_hud_text,
    draw_credits,
    draw_end_screen,
    draw_exit_info,
    draw_intro,
    style_card_rect,
    style_select_button_rect,
)
from game.snake import DOWN, LEFT, RIGHT, UP, Snake, StepResult
from settings import (
    INITIAL_LIVES,
    INVULNERABILITY_SECONDS,
    LEVEL_SCORE_THRESHOLDS,
    MAX_LIVES,
    OBSTACLES_BY_LEVEL,
)


class SnakeTests(unittest.TestCase):
    def test_starts_with_three_segments_and_rejects_reverse_turn(self) -> None:
        snake = Snake(12, 8)

        self.assertEqual(len(snake.segments), 3)
        self.assertFalse(snake.turn(LEFT))
        self.assertTrue(snake.turn(UP))
        self.assertFalse(snake.turn(DOWN))

    def test_buffers_two_legal_turns_in_order(self) -> None:
        snake = Snake(12, 8)

        self.assertTrue(snake.turn(UP))
        self.assertTrue(snake.turn(LEFT))
        self.assertEqual(snake.advance((0, 0), 12, 8), StepResult.MOVED)
        self.assertEqual(snake.segments[0], (6, 3))
        self.assertEqual(snake.advance((0, 0), 12, 8), StepResult.MOVED)
        self.assertEqual(snake.segments[0], (5, 3))

    def test_can_move_into_vacated_tail(self) -> None:
        snake = Snake(8, 8)
        snake.segments = [(2, 2), (2, 1), (3, 1), (3, 2)]
        snake.direction = RIGHT

        self.assertEqual(snake.advance((7, 7), 8, 8), StepResult.MOVED)
        self.assertEqual(snake.segments[0], (3, 2))
        self.assertEqual(len(snake.segments), 4)

    def test_cannot_move_into_body_while_growing(self) -> None:
        snake = Snake(8, 8)
        snake.segments = [(2, 2), (2, 1), (3, 1), (3, 2)]
        snake.direction = RIGHT

        self.assertEqual(snake.advance((3, 2), 8, 8), StepResult.COLLISION)

    def test_wall_collision_does_not_move_snake(self) -> None:
        snake = Snake(8, 8)
        snake.segments = [(0, 2), (1, 2), (2, 2)]
        snake.direction = LEFT

        self.assertEqual(snake.advance((7, 7), 8, 8), StepResult.COLLISION)
        self.assertEqual(snake.segments[0], (0, 2))


class GameManagerTests(unittest.TestCase):
    def test_board_too_narrow_for_initial_snake_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            GameManager(3, 8)

    def test_food_is_spawned_outside_snake(self) -> None:
        game = GameManager(12, 8)

        self.assertIsNotNone(game.food)
        self.assertNotIn(game.food, game.snake.segments)

    def test_eating_food_increases_score_and_length(self) -> None:
        game = GameManager(12, 8)
        game.food = (game.snake.segments[0][0] + 1, game.snake.segments[0][1])
        previous_length = len(game.snake.segments)

        result = game.step()

        self.assertEqual(result, StepResult.ATE)
        self.assertEqual(game.score, 1)
        self.assertEqual(len(game.snake.segments), previous_length + 1)
        self.assertNotIn(game.food, game.snake.segments)

    def test_collision_ends_game_and_reset_starts_new_round(self) -> None:
        game = GameManager(8, 8)
        game.snake.segments = [(7, 4), (6, 4), (5, 4)]
        game.snake.direction = RIGHT

        self.assertEqual(game.step(), StepResult.COLLISION)
        self.assertTrue(game.game_over)
        self.assertIsNone(game.step())

        game.reset()

        self.assertFalse(game.game_over)
        self.assertFalse(game.won)
        self.assertEqual(game.score, 0)
        self.assertEqual(len(game.snake.segments), 3)

    def test_filling_the_board_wins(self) -> None:
        game = GameManager(4, 1)
        game.food = (3, 0)

        self.assertEqual(game.step(), StepResult.ATE)
        self.assertTrue(game.won)
        self.assertEqual(len(game.snake.segments), 4)

    def test_configured_victory_score_wins_at_level_ten(self) -> None:
        game = GameManager(victory_score=30)
        game.score = 29
        head_x, head_y = game.snake.segments[0]
        game.food = (head_x + 1, head_y)

        self.assertEqual(game.step(), StepResult.ATE)
        self.assertEqual(game.score, 30)
        self.assertEqual(game.level, 10)
        self.assertTrue(game.won)

    def test_victory_waits_for_level_ten_and_accepts_custom_target(self) -> None:
        game = GameManager(victory_score=1)
        head_x, head_y = game.snake.segments[0]
        game.food = (head_x + 1, head_y)

        self.assertEqual(game.step(), StepResult.ATE)
        self.assertFalse(game.won)

        game.score = 26
        head_x, head_y = game.snake.segments[0]
        game.food = (head_x + 1, head_y)
        self.assertEqual(game.step(), StepResult.ATE)
        self.assertEqual(game.level, 10)
        self.assertTrue(game.won)

    def test_victory_score_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            GameManager(victory_score=0)

    def test_lives_and_speed_start_at_the_configured_values(self) -> None:
        game = GameManager()

        self.assertEqual(game.lives, INITIAL_LIVES)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.speed, 5)
        self.assertEqual(game.obstacles.positions, set())

    def test_level_thresholds_and_speed_are_capped_at_ten(self) -> None:
        game = GameManager()

        for index, threshold in enumerate(LEVEL_SCORE_THRESHOLDS):
            with self.subTest(threshold=threshold):
                game.score = threshold
                self.assertEqual(game.level, index + 1)
                self.assertEqual(game.speed, min(index + 5, 14))

        game.score = 100
        self.assertEqual(game.level, 10)
        self.assertEqual(game.speed, 14)

    def test_obstacles_increase_with_level_and_avoid_occupied_cells(self) -> None:
        field = ObstacleField()
        occupied = {(3, 3), (4, 3), (5, 3), (2, 2)}

        for level, expected_count in enumerate(OBSTACLES_BY_LEVEL, start=1):
            with self.subTest(level=level):
                field.grow_to_level(level, 36, 19, occupied, (3, 3))
                self.assertEqual(len(field.positions), expected_count)
                self.assertTrue(field.positions.isdisjoint(occupied))
                self.assertTrue(
                    all(abs(x - 3) + abs(y - 3) > 2 for x, y in field.positions)
                )

        self.assertEqual(len(field.positions), OBSTACLES_BY_LEVEL[9])

    def test_collecting_food_at_level_threshold_adds_obstacles(self) -> None:
        game = GameManager()
        game.score = 5
        head_x, head_y = game.snake.segments[0]
        game.food = (head_x + 1, head_y)

        self.assertEqual(game.step(), StepResult.ATE)

        self.assertEqual(game.score, 6)
        self.assertEqual(game.level, 3)
        self.assertEqual(len(game.obstacles.positions), OBSTACLES_BY_LEVEL[2])
        self.assertNotIn(game.food, game.obstacles.positions)

    def test_collision_costs_life_and_respawns_safely_with_protection(self) -> None:
        game = GameManager()
        game.lives = 2
        game.score = 5
        game.food = (0, 0)
        game.obstacles.positions = {(4, 3)}
        game.snake.segments = [(3, 3), (2, 3), (1, 3)]
        game.snake.direction = RIGHT
        previous_score = game.score
        previous_level = game.level
        previous_obstacles = game.obstacles.positions.copy()

        self.assertEqual(game.step(), StepResult.COLLISION)

        self.assertEqual(game.lives, 1)
        self.assertFalse(game.game_over)
        self.assertEqual(game.score, previous_score)
        self.assertEqual(game.level, previous_level)
        self.assertEqual(game.obstacles.positions, previous_obstacles)
        self.assertEqual(len(game.snake.segments), 3)
        self.assertTrue(set(game.snake.segments).isdisjoint(game.obstacles.positions))
        self.assertNotIn(game.food, game.snake.segments)
        self.assertEqual(game.invulnerability_remaining, INVULNERABILITY_SECONDS)

        head_x, head_y = game.snake.segments[0]
        game.obstacles.positions.add((head_x + game.snake.direction[0], head_y + game.snake.direction[1]))
        self.assertEqual(game.step(), StepResult.PROTECTED)
        self.assertEqual(game.lives, 1)

        game.advance_time(INVULNERABILITY_SECONDS)
        self.assertEqual(game.invulnerability_remaining, 0)

    def test_respawn_never_faces_an_obstacle_or_board_edge(self) -> None:
        game = GameManager(8, 5)
        game.lives = 2
        game.food = (0, 0)
        game.obstacles.positions = {(4, 1)}
        game.snake.segments = [(7, 4), (6, 4), (5, 4)]
        game.snake.direction = RIGHT

        unsafe_candidate = ([(3, 1), (2, 1), (1, 1)], RIGHT)

        def prefer_unsafe_if_available(candidates):
            return unsafe_candidate if unsafe_candidate in candidates else candidates[0]

        with patch.object(
            game_manager_module.random,
            "choice",
            side_effect=prefer_unsafe_if_available,
        ):
            self.assertEqual(game.step(), StepResult.COLLISION)

        head_x, head_y = game.snake.segments[0]
        next_cell = (head_x + game.snake.direction[0], head_y + game.snake.direction[1])
        self.assertNotEqual((game.snake.segments, game.snake.direction), unsafe_candidate)
        self.assertTrue(0 <= next_cell[0] < game.columns)
        self.assertTrue(0 <= next_cell[1] < game.rows)
        self.assertNotIn(next_cell, game.obstacles.positions)

    def test_respawn_does_not_face_outside_the_board(self) -> None:
        game = GameManager(8, 5)
        game.lives = 2
        game.food = (0, 0)
        game.snake.segments = [(7, 4), (6, 4), (5, 4)]
        game.snake.direction = RIGHT

        unsafe_candidate = ([(7, 2), (6, 2), (5, 2)], RIGHT)

        def prefer_unsafe_if_available(candidates):
            return unsafe_candidate if unsafe_candidate in candidates else candidates[0]

        with patch.object(
            game_manager_module.random,
            "choice",
            side_effect=prefer_unsafe_if_available,
        ):
            self.assertEqual(game.step(), StepResult.COLLISION)

        head_x, head_y = game.snake.segments[0]
        next_cell = (head_x + game.snake.direction[0], head_y + game.snake.direction[1])
        self.assertNotEqual((game.snake.segments, game.snake.direction), unsafe_candidate)
        self.assertTrue(0 <= next_cell[0] < game.columns)
        self.assertTrue(0 <= next_cell[1] < game.rows)

    def test_protection_redirects_away_from_a_blocked_spawn_without_losing_life(self) -> None:
        game = GameManager(8, 5)
        game.lives = 2
        game.food = (0, 0)
        game.obstacles.positions = {(4, 1)}
        game.snake.segments = [(3, 1), (2, 1), (1, 1)]
        game.snake.direction = RIGHT
        game.invulnerability_remaining = INVULNERABILITY_SECONDS

        self.assertEqual(game.step(), StepResult.PROTECTED)
        self.assertEqual(game.lives, 2)
        self.assertNotEqual(game.snake.direction, RIGHT)
        self.assertEqual(game.step(), StepResult.MOVED)
        self.assertEqual(game.lives, 2)

    def test_final_life_collision_ends_the_game(self) -> None:
        game = GameManager()
        edge = game.columns - 1
        game.snake.segments = [(edge, 0), (edge - 1, 0), (edge - 2, 0)]
        game.snake.direction = RIGHT

        self.assertEqual(game.step(), StepResult.COLLISION)
        self.assertEqual(game.lives, 0)
        self.assertTrue(game.game_over)

    def test_life_reward_at_five_points_is_collectible(self) -> None:
        game = GameManager()
        game.score = 4
        head_x, head_y = game.snake.segments[0]
        game.food = (head_x + 1, head_y)

        self.assertEqual(game.step(), StepResult.ATE)
        self.assertEqual(game.score, 5)
        self.assertIsNotNone(game.life_pickup)
        self.assertNotIn(game.life_pickup, game.snake.segments)
        self.assertNotIn(game.life_pickup, game.obstacles.positions)
        self.assertNotEqual(game.life_pickup, game.food)

        game.snake.segments[0] = (5, 5)
        game.snake.segments[1] = (4, 5)
        game.snake.segments[2] = (3, 5)
        game.snake.direction = RIGHT
        game.life_rewards.position = (6, 5)
        game.food = (10, 10)
        previous_length = len(game.snake.segments)

        self.assertEqual(game.step(), StepResult.LIFE_COLLECTED)
        self.assertEqual(game.lives, 2)
        self.assertEqual(len(game.snake.segments), previous_length)
        self.assertIsNone(game.life_pickup)
        self.assertEqual(game.pending_life_rewards, 0)

    def test_full_lives_keep_rewards_pending_until_a_life_is_lost(self) -> None:
        game = GameManager()
        game.lives = MAX_LIVES
        game.score = 4
        head_x, head_y = game.snake.segments[0]
        game.food = (head_x + 1, head_y)

        self.assertEqual(game.step(), StepResult.ATE)
        self.assertEqual(game.pending_life_rewards, 1)
        self.assertIsNone(game.life_pickup)

        game.snake.segments = [(game.columns - 1, 0), (game.columns - 2, 0), (game.columns - 3, 0)]
        game.snake.direction = RIGHT
        self.assertEqual(game.step(), StepResult.COLLISION)

        self.assertEqual(game.lives, MAX_LIVES - 1)
        self.assertEqual(game.pending_life_rewards, 1)
        self.assertIsNotNone(game.life_pickup)
        self.assertNotIn(game.life_pickup, game.snake.segments)

    def test_life_rewards_only_trigger_at_configured_scores(self) -> None:
        game = GameManager()
        for score in range(1, 5):
            game.life_rewards.update_score(score)
            self.assertEqual(game.pending_life_rewards, 0)
        game.life_rewards.update_score(5)
        self.assertEqual(game.pending_life_rewards, 1)
        game.life_rewards.update_score(15)
        self.assertEqual(game.pending_life_rewards, 2)

    def test_collecting_life_at_maximum_does_not_exceed_life_cap(self) -> None:
        game = GameManager()
        game.lives = MAX_LIVES
        game.snake.segments = [(5, 5), (4, 5), (3, 5)]
        game.snake.direction = RIGHT
        game.food = (20, 10)
        game.life_rewards.pending = 1
        game.life_rewards.position = (6, 5)

        self.assertEqual(game.step(), StepResult.LIFE_COLLECTED)

        self.assertEqual(game.lives, MAX_LIVES)
        self.assertEqual(game.pending_life_rewards, 0)
        self.assertIsNone(game.life_pickup)


class StyleTests(unittest.TestCase):
    def test_six_original_heroes_use_the_requested_distinct_colors(self) -> None:
        self.assertEqual(
            [style.name for style in STYLES],
            ["NEXO", "SOLARIA", "BRASA", "FULGOR", "GAIA", "VESPER"],
        )
        self.assertEqual(len({style.name for style in STYLES}), 6)
        self.assertEqual(
            [style.body_color for style in STYLES],
            [
                (48, 132, 220),
                (220, 180, 35),
                (205, 55, 72),
                (230, 118, 35),
                (70, 170, 104),
                (130, 75, 180),
            ],
        )

    def test_six_styles_have_distinct_palettes_and_clickable_cards(self) -> None:
        self.assertEqual(len(STYLES), 6)
        palettes = {
            (style.head_color, style.body_color, style.accent_color)
            for style in STYLES
        }
        self.assertEqual(len(palettes), len(STYLES))
        cards = [style_card_rect(index) for index in range(len(STYLES))]
        self.assertEqual(len({tuple(card) for card in cards}), len(STYLES))
        self.assertTrue(all(card.width > 0 and card.height > 0 for card in cards))
        self.assertTrue(all(0 <= card.left < card.right <= 960 for card in cards))
        self.assertTrue(all(0 <= card.top < card.bottom <= 640 for card in cards))
        self.assertFalse(any(first.colliderect(second) for first, second in (
            (cards[first], cards[second])
            for first in range(len(cards))
            for second in range(first + 1, len(cards))
        )))
        select_buttons = [
            style_select_button_rect(index) for index in range(len(STYLES))
        ]
        self.assertTrue(all(card.contains(button) for card, button in zip(cards, select_buttons)))
        self.assertFalse(any(first.colliderect(second) for first, second in (
            (select_buttons[first], select_buttons[second])
            for first in range(len(select_buttons))
            for second in range(first + 1, len(select_buttons))
        )))
        self.assertTrue(all(button.width > 0 and button.height > 0 for button in select_buttons))

    def test_style_card_rejects_out_of_range_index(self) -> None:
        with self.assertRaises(IndexError):
            style_card_rect(len(STYLES))


class HudTests(unittest.TestCase):
    def test_hud_includes_snake_length_and_game_stats(self) -> None:
        hud = build_hud_text(12, 5, 9, 2, 3, 8)

        self.assertIn("PUNTOS 012", hud)
        self.assertIn("NIVEL 5", hud)
        self.assertIn("VELOCIDAD 9", hud)
        self.assertIn("VIDAS 2/3", hud)
        self.assertIn("LONGITUD 8", hud)


class MenuScreenTests(unittest.TestCase):
    def test_menu_actions_fit_inside_the_game_surface(self) -> None:
        buttons = (MENU_PLAY, MENU_INSTRUCTIONS, MENU_CREDITS, MENU_EXIT)

        self.assertTrue(all(0 <= button.left < button.right <= 960 for button in buttons))
        self.assertTrue(all(0 <= button.top < button.bottom <= 640 for button in buttons))
        self.assertFalse(any(first.colliderect(second) for first, second in (
            (buttons[first], buttons[second])
            for first in range(len(buttons))
            for second in range(first + 1, len(buttons))
        )))

    def test_credits_and_browser_exit_screens_render(self) -> None:
        import pygame

        pygame.init()
        surface = pygame.Surface((960, 640))
        title_font = pygame.font.Font(None, 42)
        body_font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 22)
        button_font = pygame.font.Font(None, 30)

        draw_credits(surface, title_font, body_font, button_font)
        draw_exit_info(surface, title_font, body_font, small_font, button_font)

        pygame.quit()


class EndScreenTests(unittest.TestCase):
    def test_end_states_are_distinct_and_render(self) -> None:
        import pygame

        self.assertIsNot(ScreenState.GAME_OVER, ScreenState.VICTORY)
        pygame.init()
        surface = pygame.Surface((960, 640))
        fonts = {
            "title_font": pygame.font.Font(None, 42),
            "body_font": pygame.font.Font(None, 28),
            "small_font": pygame.font.Font(None, 22),
            "button_font": pygame.font.Font(None, 30),
        }

        draw_end_screen(surface, won=True, score=30, level=10, **fonts)
        draw_end_screen(surface, won=False, score=4, level=2, **fonts)

        pygame.quit()


class IntroScreenTests(unittest.TestCase):
    def test_intro_has_multiple_pages_and_buttons_fit_the_surface(self) -> None:
        self.assertGreater(INTRO_PAGE_COUNT, 1)
        for button in (INTRO_SKIP, INTRO_CONTINUE):
            self.assertTrue(0 <= button.left < button.right <= 960)
            self.assertTrue(0 <= button.top < button.bottom <= 640)
        self.assertFalse(INTRO_SKIP.colliderect(INTRO_CONTINUE))

    def test_every_intro_page_renders_and_invalid_page_is_rejected(self) -> None:
        import pygame

        pygame.init()
        surface = pygame.Surface((960, 640))
        fonts = (
            pygame.font.Font(None, 42),
            pygame.font.Font(None, 28),
            pygame.font.Font(None, 22),
            pygame.font.Font(None, 30),
        )
        for page in range(INTRO_PAGE_COUNT):
            draw_intro(surface, page, *fonts)
        with self.assertRaises(IndexError):
            draw_intro(surface, INTRO_PAGE_COUNT, *fonts)
        pygame.quit()


class TouchControlTests(unittest.TestCase):
    def test_normalized_touch_position_maps_to_game_coordinates(self) -> None:
        self.assertEqual(touch_position(0.5, 0.5), (480, 320))
        self.assertEqual(touch_position(1.0, 1.0), (960, 640))

    def test_swipe_maps_to_four_directions_and_ignores_short_taps(self) -> None:
        origin = (480, 320)

        self.assertEqual(direction_from_swipe(origin, (480, 260)), UP)
        self.assertEqual(direction_from_swipe(origin, (480, 380)), DOWN)
        self.assertEqual(direction_from_swipe(origin, (400, 320)), LEFT)
        self.assertEqual(direction_from_swipe(origin, (560, 320)), RIGHT)
        self.assertIsNone(direction_from_swipe(origin, (500, 330)))

    def test_swipes_only_change_direction_inside_the_active_board(self) -> None:
        start = (480, 342)
        end = (480, 260)

        self.assertEqual(
            game_swipe_direction(start, end, ScreenState.PLAYING),
            UP,
        )
        self.assertIsNone(
            game_swipe_direction(start, end, ScreenState.PAUSED),
        )
        self.assertIsNone(
            game_swipe_direction(start, (20, 342), ScreenState.PLAYING),
        )


if __name__ == "__main__":
    unittest.main()
