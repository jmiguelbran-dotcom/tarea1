"""Punto de entrada de Orbit Snake."""

import asyncio

import pygame

from game.characters import STYLES, SnakeStyle
from game.game_manager import GameManager
from game.screens import (
    GAME_ACTION_MENU,
    GAME_ACTION_RESTART,
    GAME_PAUSE_BUTTON,
    INFO_BACK,
    INTRO_CONTINUE,
    INTRO_PAGE_COUNT,
    INTRO_SKIP,
    INSTRUCTIONS_BACK,
    MENU_CREDITS,
    MENU_EXIT,
    MENU_INSTRUCTIONS,
    MENU_PLAY,
    PAUSE_MENU,
    PAUSE_RESTART,
    PAUSE_RESUME,
    STYLE_BACK,
    STYLE_START,
    ScreenState,
    build_hud_text,
    draw_intro,
    draw_credits,
    draw_end_screen,
    draw_exit_info,
    draw_instructions,
    draw_menu,
    draw_pause,
    draw_style_select,
    style_select_button_rect,
)
from game.snake import DOWN, LEFT, RIGHT, UP, StepResult
from settings import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    BOARD_BORDER_COLOR,
    BOARD_COLOR,
    BOARD_COLUMNS,
    BOARD_HEIGHT,
    BOARD_LEFT,
    BOARD_ROWS,
    BOARD_TOP,
    BOARD_WIDTH,
    CELL_SIZE,
    FPS,
    FOOD_COLOR,
    GRID_COLOR,
    LIFE_COLOR,
    MAX_LIVES,
    MUTED_TEXT_COLOR,
    OBSTACLE_COLOR,
    OBSTACLE_HIGHLIGHT_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TEXT_COLOR,
    WINDOW_TITLE,
)

DIRECTION_BY_KEY = {
    pygame.K_UP: UP,
    pygame.K_w: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_s: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_a: LEFT,
    pygame.K_RIGHT: RIGHT,
    pygame.K_d: RIGHT,
}


def cell_rect(position: tuple[int, int], inset: int = 3) -> pygame.Rect:
    x, y = position
    return pygame.Rect(
        BOARD_LEFT + x * CELL_SIZE + inset,
        BOARD_TOP + y * CELL_SIZE + inset,
        CELL_SIZE - inset * 2,
        CELL_SIZE - inset * 2,
    )


def touch_position(x: float, y: float) -> tuple[int, int]:
    return round(x * SCREEN_WIDTH), round(y * SCREEN_HEIGHT)


def direction_from_swipe(
    start: tuple[int, int],
    end: tuple[int, int],
    minimum_distance: int = 36,
) -> tuple[int, int] | None:
    delta_x = end[0] - start[0]
    delta_y = end[1] - start[1]
    if max(abs(delta_x), abs(delta_y)) < minimum_distance:
        return None
    if abs(delta_x) > abs(delta_y):
        return RIGHT if delta_x > 0 else LEFT
    return DOWN if delta_y > 0 else UP


def game_swipe_direction(
    start: tuple[int, int],
    end: tuple[int, int],
    state: ScreenState,
) -> tuple[int, int] | None:
    if state is not ScreenState.PLAYING:
        return None

    board_rect = pygame.Rect(BOARD_LEFT, BOARD_TOP, BOARD_WIDTH, BOARD_HEIGHT)
    if not board_rect.collidepoint(start) or not board_rect.collidepoint(end):
        return None
    return direction_from_swipe(start, end)


def draw_game(
    screen: pygame.Surface,
    game: GameManager,
    style: SnakeStyle,
    title_font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> None:
    screen.fill(BACKGROUND_COLOR)

    title = title_font.render("ORBIT SNAKE", True, TEXT_COLOR)
    screen.blit(title, (BOARD_LEFT, 34))
    style_label = small_font.render(style.name, True, style.accent_color)
    screen.blit(style_label, (BOARD_LEFT + 4, 82))
    hud = small_font.render(
        build_hud_text(
            game.score,
            game.level,
            game.speed,
            game.lives,
            MAX_LIVES,
            len(game.snake.segments),
        ),
        True,
        ACCENT_COLOR,
    )
    screen.blit(hud, hud.get_rect(topright=(GAME_PAUSE_BUTTON.left - 14, 48)))
    pygame.draw.rect(screen, BOARD_COLOR, GAME_PAUSE_BUTTON, border_radius=8)
    pygame.draw.rect(screen, BOARD_BORDER_COLOR, GAME_PAUSE_BUTTON, width=2, border_radius=8)
    pause_label = small_font.render("II", True, TEXT_COLOR)
    screen.blit(pause_label, pause_label.get_rect(center=GAME_PAUSE_BUTTON.center))

    board_rect = pygame.Rect(BOARD_LEFT, BOARD_TOP, BOARD_WIDTH, BOARD_HEIGHT)
    pygame.draw.rect(screen, BOARD_COLOR, board_rect, border_radius=8)
    for column in range(1, BOARD_COLUMNS):
        x = BOARD_LEFT + column * CELL_SIZE
        pygame.draw.line(screen, GRID_COLOR, (x, BOARD_TOP), (x, BOARD_TOP + BOARD_HEIGHT))
    for row in range(1, BOARD_ROWS):
        y = BOARD_TOP + row * CELL_SIZE
        pygame.draw.line(screen, GRID_COLOR, (BOARD_LEFT, y), (BOARD_LEFT + BOARD_WIDTH, y))
    pygame.draw.rect(screen, BOARD_BORDER_COLOR, board_rect, width=2, border_radius=8)

    for obstacle in game.obstacles.positions:
        obstacle_rect = cell_rect(obstacle, inset=2)
        pygame.draw.rect(screen, OBSTACLE_COLOR, obstacle_rect, border_radius=5)
        pygame.draw.line(
            screen,
            OBSTACLE_HIGHLIGHT_COLOR,
            (obstacle_rect.left + 4, obstacle_rect.top + 4),
            (obstacle_rect.right - 4, obstacle_rect.top + 4),
            2,
        )

    if game.food is not None:
        food_center = cell_rect(game.food).center
        pygame.draw.circle(screen, FOOD_COLOR, food_center, CELL_SIZE // 3)
        pygame.draw.circle(screen, (255, 232, 186), food_center, CELL_SIZE // 7)

    if game.life_pickup is not None:
        life_rect = cell_rect(game.life_pickup)
        heart_y = life_rect.centery + 2
        pygame.draw.circle(screen, LIFE_COLOR, (life_rect.centerx - 4, heart_y - 3), 5)
        pygame.draw.circle(screen, LIFE_COLOR, (life_rect.centerx + 4, heart_y - 3), 5)
        pygame.draw.polygon(
            screen,
            LIFE_COLOR,
            (
                (life_rect.centerx - 9, heart_y - 1),
                (life_rect.centerx + 9, heart_y - 1),
                (life_rect.centerx, heart_y + 9),
            ),
        )

    for index, segment in enumerate(game.snake.segments):
        segment_rect = cell_rect(segment)
        color = style.head_color if index == 0 else style.body_color
        if index == 0 and game.invulnerability_remaining > 0:
            color = LIFE_COLOR
        pygame.draw.rect(screen, color, segment_rect, border_radius=7)

    if game.snake.segments:
        head_rect = cell_rect(game.snake.segments[0])
        head_x, head_y = head_rect.center
        dx, dy = game.snake.direction
        forward_x, forward_y = dx * 3, dy * 3
        side_x, side_y = -dy * 4, dx * 4
        eye_color = (14, 37, 43)
        pygame.draw.circle(
            screen,
            eye_color,
            (head_x + forward_x + side_x, head_y + forward_y + side_y),
            2,
        )
        pygame.draw.circle(
            screen,
            eye_color,
            (head_x + forward_x - side_x, head_y + forward_y - side_y),
            2,
        )

    controls = small_font.render(
        "MOVER: DESLIZA / FLECHAS / WASD",
        True,
        MUTED_TEXT_COLOR,
    )
    restart = small_font.render("R: REINICIAR", True, MUTED_TEXT_COLOR)
    screen.blit(controls, (BOARD_LEFT, BOARD_TOP + BOARD_HEIGHT + 17))
    screen.blit(
        restart,
        restart.get_rect(topright=(BOARD_LEFT + BOARD_WIDTH, BOARD_TOP + BOARD_HEIGHT + 17)),
    )

async def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    game = GameManager()
    state = ScreenState.INTRO
    intro_page = 0
    selected_style_index = 0

    title_font = pygame.font.Font(None, 42)
    body_font = pygame.font.Font(None, 28)
    small_font = pygame.font.Font(None, 22)
    button_font = pygame.font.Font(None, 30)
    accumulator = 0.0
    touch_starts: dict[int, tuple[int, int]] = {}
    previous_time = pygame.time.get_ticks() / 1000
    running = True

    try:
        while running:
            current_time = pygame.time.get_ticks() / 1000
            elapsed = min(current_time - previous_time, 0.1)
            previous_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue

                if event.type == pygame.FINGERDOWN:
                    touch_starts[event.finger_id] = touch_position(event.x, event.y)
                    continue

                if event.type == pygame.FINGERUP:
                    start = touch_starts.pop(event.finger_id, None)
                    if start is None:
                        continue
                    position = touch_position(event.x, event.y)
                    swipe = direction_from_swipe(start, position)
                    direction = game_swipe_direction(start, position, state)
                    if direction is not None:
                        game.snake.turn(direction)
                    elif swipe is None:
                        pygame.event.post(
                            pygame.event.Event(
                                pygame.MOUSEBUTTONDOWN,
                                {"pos": position, "button": 1},
                            )
                        )
                    continue

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    position = event.pos
                    if state is ScreenState.INTRO:
                        if INTRO_SKIP.collidepoint(position):
                            intro_page = 0
                            state = ScreenState.MENU
                        elif INTRO_CONTINUE.collidepoint(position):
                            if intro_page + 1 == INTRO_PAGE_COUNT:
                                intro_page = 0
                                state = ScreenState.MENU
                            else:
                                intro_page += 1
                    elif state is ScreenState.MENU:
                        if MENU_PLAY.collidepoint(position):
                            state = ScreenState.STYLE_SELECT
                        elif MENU_INSTRUCTIONS.collidepoint(position):
                            state = ScreenState.INSTRUCTIONS
                        elif MENU_CREDITS.collidepoint(position):
                            state = ScreenState.CREDITS
                        elif MENU_EXIT.collidepoint(position):
                            state = ScreenState.EXIT_INFO
                    elif state is ScreenState.INSTRUCTIONS:
                        if INSTRUCTIONS_BACK.collidepoint(position):
                            state = ScreenState.MENU
                    elif state in (ScreenState.CREDITS, ScreenState.EXIT_INFO):
                        if INFO_BACK.collidepoint(position):
                            state = ScreenState.MENU
                    elif state is ScreenState.STYLE_SELECT:
                        if STYLE_BACK.collidepoint(position):
                            state = ScreenState.MENU
                        elif STYLE_START.collidepoint(position):
                            game.reset()
                            accumulator = 0.0
                            state = ScreenState.PLAYING
                        else:
                            for index in range(len(STYLES)):
                                if style_select_button_rect(index).collidepoint(position):
                                    selected_style_index = index
                                    break
                    elif state in (ScreenState.PLAYING, ScreenState.GAME_OVER, ScreenState.VICTORY):
                        if state in (ScreenState.GAME_OVER, ScreenState.VICTORY):
                            if GAME_ACTION_RESTART.collidepoint(position):
                                game.reset()
                                accumulator = 0.0
                                state = ScreenState.PLAYING
                            elif GAME_ACTION_MENU.collidepoint(position):
                                state = ScreenState.MENU
                        elif GAME_PAUSE_BUTTON.collidepoint(position):
                            state = ScreenState.PAUSED
                    elif state is ScreenState.PAUSED:
                        if PAUSE_RESUME.collidepoint(position):
                            state = ScreenState.PLAYING
                        elif PAUSE_RESTART.collidepoint(position):
                            game.reset()
                            accumulator = 0.0
                            state = ScreenState.PLAYING
                        elif PAUSE_MENU.collidepoint(position):
                            state = ScreenState.MENU
                    continue

                if event.type != pygame.KEYDOWN:
                    continue

                if state is ScreenState.MENU:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_j):
                        state = ScreenState.STYLE_SELECT
                    elif event.key == pygame.K_i:
                        state = ScreenState.INSTRUCTIONS
                    elif event.key == pygame.K_c:
                        state = ScreenState.CREDITS
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        state = ScreenState.EXIT_INFO
                elif state is ScreenState.INSTRUCTIONS:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        state = ScreenState.MENU
                elif state is ScreenState.INTRO:
                    if event.key in (pygame.K_ESCAPE, pygame.K_s):
                        intro_page = 0
                        state = ScreenState.MENU
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if intro_page + 1 == INTRO_PAGE_COUNT:
                            intro_page = 0
                            state = ScreenState.MENU
                        else:
                            intro_page += 1
                elif state in (ScreenState.CREDITS, ScreenState.EXIT_INFO):
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        state = ScreenState.MENU
                elif state is ScreenState.STYLE_SELECT:
                    if event.key == pygame.K_ESCAPE:
                        state = ScreenState.MENU
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        selected_style_index = (selected_style_index - 1) % len(STYLES)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        selected_style_index = (selected_style_index + 1) % len(STYLES)
                    elif pygame.K_1 <= event.key <= pygame.K_6:
                        selected_style_index = event.key - pygame.K_1
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game.reset()
                        accumulator = 0.0
                        state = ScreenState.PLAYING
                elif state is ScreenState.PAUSED:
                    if event.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_RETURN, pygame.K_SPACE):
                        state = ScreenState.PLAYING
                    elif event.key == pygame.K_r:
                        game.reset()
                        accumulator = 0.0
                        state = ScreenState.PLAYING
                    elif event.key == pygame.K_m:
                        state = ScreenState.MENU
                elif state in (ScreenState.GAME_OVER, ScreenState.VICTORY):
                    if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                        game.reset()
                        accumulator = 0.0
                        state = ScreenState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        state = ScreenState.MENU
                elif state is ScreenState.PLAYING:
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        state = ScreenState.PAUSED
                    elif event.key == pygame.K_r:
                        game.reset()
                        accumulator = 0.0
                    else:
                        direction = DIRECTION_BY_KEY.get(event.key)
                        if direction is not None:
                            game.snake.turn(direction)

            if state is ScreenState.PLAYING and not game.game_over and not game.won:
                game.advance_time(elapsed)
                accumulator += elapsed
                while accumulator >= 1 / game.speed:
                    move_interval = 1 / game.speed
                    result = game.step()
                    accumulator -= move_interval
                    if result is StepResult.COLLISION:
                        accumulator = 0.0
                        if game.game_over:
                            state = ScreenState.GAME_OVER
                        break
                    if game.won:
                        accumulator = 0.0
                        state = ScreenState.VICTORY
                        break
                    if result is None:
                        break

            if state is ScreenState.INTRO:
                draw_intro(
                    screen,
                    intro_page,
                    title_font,
                    body_font,
                    small_font,
                    button_font,
                )
            elif state is ScreenState.MENU:
                draw_menu(screen, title_font, body_font, button_font, small_font)
            elif state is ScreenState.INSTRUCTIONS:
                draw_instructions(screen, title_font, body_font, button_font, small_font)
            elif state is ScreenState.CREDITS:
                draw_credits(screen, title_font, body_font, button_font)
            elif state is ScreenState.EXIT_INFO:
                draw_exit_info(screen, title_font, body_font, small_font, button_font)
            elif state is ScreenState.STYLE_SELECT:
                draw_style_select(
                    screen,
                    selected_style_index,
                    title_font,
                    body_font,
                    button_font,
                    small_font,
                )
            elif state in (ScreenState.GAME_OVER, ScreenState.VICTORY):
                draw_end_screen(
                    screen,
                    won=state is ScreenState.VICTORY,
                    score=game.score,
                    level=game.level,
                    title_font=title_font,
                    body_font=body_font,
                    small_font=small_font,
                    button_font=button_font,
                )
            else:
                draw_game(
                    screen,
                    game,
                    STYLES[selected_style_index],
                    title_font,
                    small_font,
                )
                if state is ScreenState.PAUSED:
                    draw_pause(screen, title_font, button_font)
            pygame.display.flip()
            await asyncio.sleep(1 / FPS)
    finally:
        pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
