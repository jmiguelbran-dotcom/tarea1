"""Pantallas de navegacion para Orbit Snake."""

from enum import Enum, auto

import pygame

from game.characters import STYLES
from settings import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    BOARD_BORDER_COLOR,
    BOARD_COLOR,
    GRID_COLOR,
    MUTED_TEXT_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TEXT_COLOR,
)


class ScreenState(Enum):
    INTRO = auto()
    MENU = auto()
    INSTRUCTIONS = auto()
    CREDITS = auto()
    EXIT_INFO = auto()
    STYLE_SELECT = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()


MENU_PLAY = pygame.Rect(350, 300, 260, 54)
MENU_INSTRUCTIONS = pygame.Rect(350, 368, 260, 54)
MENU_CREDITS = pygame.Rect(350, 436, 260, 54)
MENU_EXIT = pygame.Rect(350, 504, 260, 54)
INTRO_SKIP = pygame.Rect(250, 520, 210, 54)
INTRO_CONTINUE = pygame.Rect(500, 520, 210, 54)
INSTRUCTIONS_BACK = pygame.Rect(350, 520, 260, 54)
INFO_BACK = pygame.Rect(350, 520, 260, 54)
STYLE_BACK = pygame.Rect(250, 530, 210, 54)
STYLE_START = pygame.Rect(500, 530, 210, 54)
STYLE_CARD_WIDTH = 270
STYLE_CARD_GAP = 18
STYLE_CARD_TOP = 190
STYLE_CARD_HEIGHT = 140
STYLE_CARD_COLUMNS = 3
STYLE_CARD_ROW_GAP = 12
STYLE_SELECT_BUTTON_WIDTH = 156
STYLE_SELECT_BUTTON_HEIGHT = 28
PAUSE_RESUME = pygame.Rect(350, 310, 260, 56)
PAUSE_RESTART = pygame.Rect(350, 382, 260, 56)
PAUSE_MENU = pygame.Rect(350, 454, 260, 56)
GAME_ACTION_RESTART = pygame.Rect(230, 410, 230, 52)
GAME_ACTION_MENU = pygame.Rect(500, 410, 230, 52)
GAME_PAUSE_BUTTON = pygame.Rect(856, 38, 56, 38)
INTRO_STORY = (
    (
        "ALERTA EN NUEVA AURORA",
        (
            "Una grieta luminosa se abre sobre la ciudad y libera",
            "drones que avanzan por sus calles.",
        ),
    ),
    (
        "SE FORMA EL EQUIPO",
        (
            "Seis heroes originales unen sus talentos para",
            "proteger a la gente y cerrar la brecha.",
        ),
    ),
    (
        "RECUPERA LA ENERGIA",
        (
            "Recoge los nucleos dispersos, esquiva obstaculos",
            "y ayuda a los Guardianes de Aurora a resistir.",
        ),
    ),
)
INTRO_PAGE_COUNT = len(INTRO_STORY)


def style_card_rect(index: int) -> pygame.Rect:
    if not 0 <= index < len(STYLES):
        raise IndexError("El indice de estilo esta fuera de rango.")
    total_width = (
        STYLE_CARD_COLUMNS * STYLE_CARD_WIDTH
        + (STYLE_CARD_COLUMNS - 1) * STYLE_CARD_GAP
    )
    left = (SCREEN_WIDTH - total_width) // 2
    column = index % STYLE_CARD_COLUMNS
    row = index // STYLE_CARD_COLUMNS
    return pygame.Rect(
        left + column * (STYLE_CARD_WIDTH + STYLE_CARD_GAP),
        STYLE_CARD_TOP + row * (STYLE_CARD_HEIGHT + STYLE_CARD_ROW_GAP),
        STYLE_CARD_WIDTH,
        STYLE_CARD_HEIGHT,
    )


def style_select_button_rect(index: int) -> pygame.Rect:
    card = style_card_rect(index)
    return pygame.Rect(
        card.centerx - STYLE_SELECT_BUTTON_WIDTH // 2,
        card.bottom - STYLE_SELECT_BUTTON_HEIGHT - 8,
        STYLE_SELECT_BUTTON_WIDTH,
        STYLE_SELECT_BUTTON_HEIGHT,
    )


def draw_background(screen: pygame.Surface) -> None:
    screen.fill(BACKGROUND_COLOR)
    for x, y, radius in (
        (58, 72, 2),
        (154, 126, 2),
        (257, 51, 2),
        (341, 167, 1),
        (451, 71, 2),
        (539, 130, 1),
        (627, 48, 2),
        (737, 104, 2),
        (827, 62, 1),
        (902, 151, 2),
        (99, 231, 1),
        (855, 248, 1),
    ):
        pygame.draw.circle(screen, (80, 119, 145), (x, y), radius)

    for x in range(0, SCREEN_WIDTH, 40):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, 40):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

    portal_center = (SCREEN_WIDTH // 2, 190)
    pygame.draw.ellipse(
        screen,
        (17, 47, 69),
        pygame.Rect(portal_center[0] - 102, portal_center[1] - 92, 204, 184),
        3,
    )
    pygame.draw.ellipse(
        screen,
        (23, 67, 87),
        pygame.Rect(portal_center[0] - 77, portal_center[1] - 69, 154, 138),
        2,
    )
    pygame.draw.ellipse(
        screen,
        (18, 37, 58),
        pygame.Rect(portal_center[0] - 46, portal_center[1] - 43, 92, 86),
        1,
    )
    pygame.draw.line(
        screen,
        (30, 101, 122),
        (portal_center[0] - 68, portal_center[1] + 30),
        (portal_center[0] - 30, portal_center[1] - 53),
        2,
    )
    pygame.draw.line(
        screen,
        (42, 79, 132),
        (portal_center[0] + 52, portal_center[1] - 46),
        (portal_center[0] + 73, portal_center[1] + 24),
        2,
    )

    skyline = (
        (0, 546, 74, 54),
        (67, 526, 61, 74),
        (123, 540, 82, 60),
        (202, 510, 68, 90),
        (266, 532, 76, 68),
        (339, 496, 82, 104),
        (418, 525, 66, 75),
        (481, 516, 94, 84),
        (572, 535, 69, 65),
        (638, 506, 83, 94),
        (718, 528, 72, 72),
        (787, 489, 79, 111),
        (863, 520, 97, 80),
    )
    for x, top, width, height in skyline:
        building = pygame.Rect(x, top, width, height)
        pygame.draw.rect(screen, (12, 24, 39), building)
        pygame.draw.line(screen, (24, 46, 65), building.topleft, (building.right, top), 2)
        for window_y in range(top + 13, SCREEN_HEIGHT - 8, 17):
            for window_x in range(x + 9, x + width - 5, 15):
                if (window_x + window_y) % 4:
                    pygame.draw.rect(
                        screen,
                        (25, 48, 62),
                        pygame.Rect(window_x, window_y, 4, 6),
                    )

    pygame.draw.line(
        screen,
        (37, 71, 87),
        (0, SCREEN_HEIGHT - 39),
        (SCREEN_WIDTH, SCREEN_HEIGHT - 39),
        2,
    )


def draw_button(
    screen: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    font: pygame.font.Font,
    *,
    selected: bool = False,
) -> None:
    fill_color = (25, 50, 67) if selected else BOARD_COLOR
    border_color = ACCENT_COLOR if selected else (55, 81, 101)
    pygame.draw.rect(screen, fill_color, rect, border_radius=10)
    pygame.draw.rect(screen, border_color, rect, width=2, border_radius=10)
    text = font.render(label, True, TEXT_COLOR)
    screen.blit(text, text.get_rect(center=rect.center))


def build_hud_text(
    score: int,
    level: int,
    speed: int,
    lives: int,
    max_lives: int,
    length: int,
) -> str:
    return (
        f"PUNTOS {score:03d}   NIVEL {level}   VELOCIDAD {speed}   "
        f"VIDAS {lives}/{max_lives}   LONGITUD {length}"
    )


def draw_intro(
    screen: pygame.Surface,
    page: int,
    title_font: pygame.font.Font,
    body_font: pygame.font.Font,
    small_font: pygame.font.Font,
    button_font: pygame.font.Font,
) -> None:
    if not 0 <= page < len(INTRO_STORY):
        raise IndexError("La pagina de introduccion esta fuera de rango.")

    draw_background(screen)
    title = title_font.render("ORBIT SNAKE", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 112)))
    heading_text, lines = INTRO_STORY[page]
    heading = body_font.render(heading_text, True, ACCENT_COLOR)
    screen.blit(heading, heading.get_rect(center=(SCREEN_WIDTH // 2, 183)))

    panel = pygame.Rect(120, 236, SCREEN_WIDTH - 240, 178)
    pygame.draw.rect(screen, BOARD_COLOR, panel, border_radius=14)
    pygame.draw.rect(screen, BOARD_BORDER_COLOR, panel, width=2, border_radius=14)
    for index, line in enumerate(lines):
        text = body_font.render(line, True, TEXT_COLOR)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, 300 + index * 42)))

    progress = small_font.render(
        f"{page + 1} / {len(INTRO_STORY)}",
        True,
        MUTED_TEXT_COLOR,
    )
    screen.blit(progress, progress.get_rect(center=(SCREEN_WIDTH // 2, 462)))
    draw_button(screen, INTRO_SKIP, "OMITIR INTRO", button_font)
    draw_button(screen, INTRO_CONTINUE, "CONTINUAR", button_font, selected=True)


def draw_menu(
    screen: pygame.Surface,
    title_font: pygame.font.Font,
    subtitle_font: pygame.font.Font,
    button_font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> None:
    draw_background(screen)
    title = title_font.render("ORBIT SNAKE", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 156)))
    subtitle = subtitle_font.render("LOS GUARDIANES DE NUEVA AURORA", True, ACCENT_COLOR)
    screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 214)))
    draw_button(screen, MENU_PLAY, "JUGAR", button_font, selected=True)
    draw_button(screen, MENU_INSTRUCTIONS, "COMO JUGAR", button_font)
    draw_button(screen, MENU_CREDITS, "CREDITOS", button_font)
    draw_button(screen, MENU_EXIT, "SALIR", button_font)
    hint = small_font.render(
        "ENTER: jugar     I: instrucciones     C: creditos",
        True,
        MUTED_TEXT_COLOR,
    )
    screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, 590)))


def draw_instructions(
    screen: pygame.Surface,
    title_font: pygame.font.Font,
    body_font: pygame.font.Font,
    button_font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> None:
    draw_background(screen)
    title = title_font.render("COMO JUGAR", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 112)))

    instructions = (
        ("MUEVETE", "Usa flechas, WASD o desliza dentro del tablero al tocar."),
        ("REUNE ENERGIA", "Recoge los nucleos naranjas para sumar puntos y crecer."),
        ("PROGRESA", "Cada 3 puntos subes de nivel; llega a 30 puntos en nivel 10."),
        ("SOBREVIVE", "Gana vidas en 5 y 15 puntos; evita obstaculos y bordes."),
        ("CONTROLES", "Pulsa P o ESC para pausar. Pulsa R para reiniciar."),
    )
    for index, (heading, detail) in enumerate(instructions):
        y = 174 + index * 62
        heading_surface = body_font.render(heading, True, ACCENT_COLOR)
        detail_surface = small_font.render(detail, True, TEXT_COLOR)
        screen.blit(heading_surface, (190, y))
        screen.blit(detail_surface, (190, y + 29))

    draw_button(screen, INSTRUCTIONS_BACK, "VOLVER AL MENU", button_font)


def draw_credits(
    screen: pygame.Surface,
    title_font: pygame.font.Font,
    body_font: pygame.font.Font,
    button_font: pygame.font.Font,
) -> None:
    draw_background(screen)
    title = title_font.render("CREDITOS", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 150)))
    lines = (
        "Orbit Snake: aventura original de heroes y ciencia ficcion.",
        "Desarrollado con Python, Pygame y Pygbag.",
        "Seis heroes y graficos originales creados con formas geometricas.",
        "Sin imagenes ni musica externas.",
    )
    for index, line in enumerate(lines):
        rendered = body_font.render(line, True, ACCENT_COLOR if index == 0 else TEXT_COLOR)
        screen.blit(rendered, rendered.get_rect(center=(SCREEN_WIDTH // 2, 250 + index * 46)))
    draw_button(screen, INFO_BACK, "VOLVER AL MENU", button_font)


def draw_exit_info(
    screen: pygame.Surface,
    title_font: pygame.font.Font,
    body_font: pygame.font.Font,
    small_font: pygame.font.Font,
    button_font: pygame.font.Font,
) -> None:
    draw_background(screen)
    title = title_font.render("HASTA PRONTO", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 190)))
    message = body_font.render("Puedes cerrar esta pestana para salir del juego.", True, ACCENT_COLOR)
    screen.blit(message, message.get_rect(center=(SCREEN_WIDTH // 2, 290)))
    note = small_font.render(
        "El navegador no permite que el juego cierre la pestana por ti.",
        True,
        MUTED_TEXT_COLOR,
    )
    screen.blit(note, note.get_rect(center=(SCREEN_WIDTH // 2, 338)))
    draw_button(screen, INFO_BACK, "VOLVER AL MENU", button_font)


def draw_style_select(
    screen: pygame.Surface,
    selected_style: int,
    title_font: pygame.font.Font,
    body_font: pygame.font.Font,
    button_font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> None:
    draw_background(screen)
    title = title_font.render("ELIGE A TU HEROE", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 104)))
    hint = small_font.render(
        "Selecciona un heroe o usa las teclas 1 - 6",
        True,
        MUTED_TEXT_COLOR,
    )
    screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, 157)))

    for index, style in enumerate(STYLES):
        card = style_card_rect(index)
        is_selected = index == selected_style
        border_color = style.accent_color if is_selected else (55, 81, 101)
        pygame.draw.rect(screen, BOARD_COLOR, card, border_radius=12)
        pygame.draw.rect(
            screen,
            border_color,
            card,
            width=3 if is_selected else 1,
            border_radius=12,
        )

        head = pygame.Rect(card.centerx - 12, card.top + 10, 22, 22)
        body = pygame.Rect(card.centerx - 40, card.top + 12, 21, 17)
        tail = pygame.Rect(card.centerx - 65, card.top + 12, 18, 17)
        pygame.draw.rect(screen, style.body_color, tail, border_radius=6)
        pygame.draw.rect(screen, style.body_color, body, border_radius=6)
        pygame.draw.rect(screen, style.head_color, head, border_radius=7)
        pygame.draw.circle(screen, (14, 37, 43), (head.centerx + 5, head.centery - 3), 2)

        name = body_font.render(style.name, True, TEXT_COLOR)
        screen.blit(name, name.get_rect(center=(card.centerx, card.top + 47)))
        description = small_font.render(style.description, True, MUTED_TEXT_COLOR)
        screen.blit(description, description.get_rect(center=(card.centerx, card.top + 78)))
        draw_button(
            screen,
            style_select_button_rect(index),
            "SELECCIONAR",
            small_font,
            selected=is_selected,
        )

    draw_button(screen, STYLE_BACK, "VOLVER", button_font)
    draw_button(screen, STYLE_START, "EMPEZAR", button_font, selected=True)


def draw_pause(
    screen: pygame.Surface,
    title_font: pygame.font.Font,
    button_font: pygame.font.Font,
) -> None:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 9, 18, 210))
    screen.blit(overlay, (0, 0))

    title = title_font.render("JUEGO EN PAUSA", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 230)))
    draw_button(screen, PAUSE_RESUME, "CONTINUAR", button_font, selected=True)
    draw_button(screen, PAUSE_RESTART, "REINICIAR", button_font)
    draw_button(screen, PAUSE_MENU, "VOLVER AL MENU", button_font)


def draw_end_actions(
    screen: pygame.Surface,
    button_font: pygame.font.Font,
) -> None:
    draw_button(screen, GAME_ACTION_RESTART, "VOLVER A JUGAR", button_font, selected=True)
    draw_button(screen, GAME_ACTION_MENU, "MENU PRINCIPAL", button_font)


def draw_end_screen(
    screen: pygame.Surface,
    *,
    won: bool,
    score: int,
    level: int,
    title_font: pygame.font.Font,
    body_font: pygame.font.Font,
    small_font: pygame.font.Font,
    button_font: pygame.font.Font,
) -> None:
    draw_background(screen)
    heading_text = "MISION COMPLETADA" if won else "MISION FALLIDA"
    heading_color = ACCENT_COLOR if won else TEXT_COLOR
    heading = title_font.render(heading_text, True, heading_color)
    screen.blit(heading, heading.get_rect(center=(SCREEN_WIDTH // 2, 220)))

    message_text = (
        "SECTOR ESTABLE. OBJETIVO ALCANZADO."
        if won
        else "Se agotaron tus vidas. Intenta de nuevo."
    )
    message = body_font.render(message_text, True, TEXT_COLOR)
    screen.blit(message, message.get_rect(center=(SCREEN_WIDTH // 2, 286)))

    stats = body_font.render(
        f"Puntos: {score}    Nivel maximo: {level}",
        True,
        ACCENT_COLOR,
    )
    screen.blit(stats, stats.get_rect(center=(SCREEN_WIDTH // 2, 350)))
    hint = small_font.render("Elige una opcion para continuar.", True, MUTED_TEXT_COLOR)
    screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, 390)))
    draw_end_actions(screen, button_font)
