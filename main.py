import asyncio
import json
import logging
import math
import random
from pathlib import Path

import pygame


WINDOW_WIDTH = 720
WINDOW_HEIGHT = 800
CELL_SIZE = 24
BOARD_COLUMNS = 25
BOARD_ROWS = 20
BOARD_WIDTH = CELL_SIZE * BOARD_COLUMNS
BOARD_HEIGHT = CELL_SIZE * BOARD_ROWS
BOARD_LEFT = (WINDOW_WIDTH - BOARD_WIDTH) // 2
BOARD_TOP = 154
BOARD_RECT = pygame.Rect(BOARD_LEFT, BOARD_TOP, BOARD_WIDTH, BOARD_HEIGHT)
PAUSE_BUTTON = pygame.Rect(WINDOW_WIDTH - 118, 21, 86, 42)

BACKGROUND = (10, 17, 25)
PANEL = (18, 29, 40)
PANEL_LIGHT = (24, 38, 51)
BOARD_COLOR = (13, 23, 31)
GRID_COLOR = (20, 33, 42)
GREEN = (105, 231, 151)
GREEN_LIGHT = (174, 255, 194)
GREEN_DARK = (46, 164, 105)
PINK = (255, 111, 145)
GOLD = (255, 204, 112)
WHITE = (239, 246, 250)
MUTED = (145, 164, 177)
OUTLINE = (43, 62, 76)

DIFFICULTIES = (
    ("ZEN", 7),
    ("CLASSIQUE", 10),
    ("RAPIDE", 14),
)
TOUCH_DIRECTIONS = {
    "up": pygame.Vector2(0, -1),
    "down": pygame.Vector2(0, 1),
    "left": pygame.Vector2(-1, 0),
    "right": pygame.Vector2(1, 0),
}

HOME = "home"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"
WON = "won"

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def load_best_score(save_path):
    try:
        data = json.loads(save_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return 0
    except (OSError, json.JSONDecodeError) as error:
        logging.warning("Impossible de lire la sauvegarde du jeu : %s", error)
        return 0

    if isinstance(data, dict):
        score = data.get("best_score", 0)
        if isinstance(score, int) and not isinstance(score, bool) and score >= 0:
            return score
    logging.warning("La sauvegarde du jeu contient un meilleur score invalide.")
    return 0


def save_best_score(save_path, score):
    try:
        save_path.write_text(
            json.dumps({"best_score": score}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError as error:
        logging.warning("Impossible d'enregistrer le meilleur score : %s", error)


def draw_text(screen, text, font, color, center):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=center))


def draw_button(screen, rect, label, font, mouse_pos, selected=False, accent=GREEN):
    hovered = rect.collidepoint(mouse_pos)
    fill = PANEL_LIGHT if not hovered and not selected else (33, 60, 52)
    if selected:
        fill = (34, 74, 58)
    pygame.draw.rect(screen, fill, rect, border_radius=13)
    pygame.draw.rect(
        screen,
        accent if hovered or selected else OUTLINE,
        rect,
        2,
        border_radius=13,
    )
    draw_text(screen, label, font, WHITE if hovered or selected else MUTED, rect.center)


def draw_panel(screen, rect, fill=PANEL, border=OUTLINE, radius=18):
    pygame.draw.rect(screen, fill, rect, border_radius=radius)
    pygame.draw.rect(screen, border, rect, 1, border_radius=radius)


def random_food(snake):
    occupied = {(int(segment.x), int(segment.y)) for segment in snake}
    empty_cells = [
        (x, y)
        for y in range(BOARD_ROWS)
        for x in range(BOARD_COLUMNS)
        if (x, y) not in occupied
    ]
    if not empty_cells:
        return None
    return pygame.Vector2(random.choice(empty_cells))


def new_game():
    start = pygame.Vector2(BOARD_COLUMNS // 2, BOARD_ROWS // 2)
    snake = [
        start,
        start - pygame.Vector2(1, 0),
        start - pygame.Vector2(2, 0),
    ]
    direction = pygame.Vector2(1, 0)
    return snake, direction, random_food(snake)


def draw_background(screen, stars, elapsed):
    screen.fill(BACKGROUND)
    for x, y, radius, phase in stars:
        glow = 0.5 + 0.5 * math.sin(elapsed * 1.4 + phase)
        color = tuple(int(channel * glow) for channel in (38, 67, 75))
        pygame.draw.circle(screen, color, (x, y), radius)


def draw_header(screen, small_font, medium_font, state, mouse_pos):
    draw_text(screen, "SNAKE", medium_font, GREEN_LIGHT, (80, 42))
    draw_text(screen, "ARCADE", small_font, MUTED, (155, 43))
    if state == PLAYING:
        draw_button(
            screen,
            PAUSE_BUTTON,
            "PAUSE",
            small_font,
            mouse_pos,
        )
    else:
        status = "EN PAUSE" if state == PAUSED else "À TOI DE JOUER"
        draw_text(screen, status, small_font, MUTED, (WINDOW_WIDTH - 104, 43))
    pygame.draw.line(screen, OUTLINE, (32, 74), (WINDOW_WIDTH - 32, 74), 1)


def draw_home(screen, fonts, mouse_pos, selected_difficulty, best_score, stars, elapsed):
    title_font, medium_font, small_font, tiny_font = fonts
    draw_background(screen, stars, elapsed)
    draw_header(screen, small_font, medium_font, HOME, mouse_pos)

    draw_panel(screen, pygame.Rect(60, 106, 600, 560), fill=(14, 24, 32))
    draw_text(screen, "LE CLASSIQUE, EN MIEUX.", small_font, GREEN, (360, 165))
    draw_text(screen, "SNAKE", title_font, WHITE, (360, 237))
    draw_text(
        screen,
        "Mange, grandis et bats ton meilleur score.",
        small_font,
        MUTED,
        (360, 285),
    )

    for index in range(7):
        segment = pygame.Rect(276 + index * 25, 328, 21, 21)
        pygame.draw.rect(
            screen,
            GREEN_LIGHT if index == 0 else GREEN_DARK,
            segment,
            border_radius=7,
        )
    pygame.draw.circle(screen, PINK, (484, 338), 10)

    draw_text(screen, "CHOISIS TA DIFFICULTÉ", tiny_font, MUTED, (360, 395))
    difficulty_rects = []
    button_width = 166
    gap = 12
    start_x = (WINDOW_WIDTH - (button_width * 3 + gap * 2)) // 2
    for index, (name, _) in enumerate(DIFFICULTIES):
        rect = pygame.Rect(start_x + index * (button_width + gap), 416, button_width, 52)
        difficulty_rects.append(rect) 
        draw_button(
            screen,
            rect,
            name,
            small_font,
            mouse_pos,
            selected=index == selected_difficulty,
        )

    play_rect = pygame.Rect(218, 500, 284, 64)
    draw_button(screen, play_rect, "JOUER", medium_font, mouse_pos, selected=True)
    draw_text(screen, f"RECORD PERSONNEL  {best_score:04d}", tiny_font, GOLD, (360, 604))

    draw_text(
        screen,
        "ORDINATEUR : FLÈCHES / ZQSD     •     TÉLÉPHONE : GLISSE SUR LE JEU",
        tiny_font,
        MUTED,
        (360, 716),
    )
    draw_text(screen, "RECORD SAUVEGARDÉ AUTOMATIQUEMENT", tiny_font, MUTED, (360, 744))
    return play_rect, difficulty_rects


def draw_hud(screen, fonts, score, best_score, level, elapsed):
    _, medium_font, small_font, tiny_font = fonts
    items = (
        (pygame.Rect(40, 88, 150, 58), "SCORE", f"{score:04d}", GREEN_LIGHT),
        (pygame.Rect(202, 88, 150, 58), "RECORD", f"{best_score:04d}", GOLD),
        (pygame.Rect(364, 88, 150, 58), "NIVEAU", f"{level:02d}", WHITE),
        (
            pygame.Rect(526, 88, 154, 58),
            "TEMPS",
            f"{int(elapsed) // 60:02d}:{int(elapsed) % 60:02d}",
            WHITE,
        ),
    )
    for rect, label, value, color in items:
        draw_panel(screen, rect, fill=PANEL)
        draw_text(screen, label, tiny_font, MUTED, (rect.centerx, rect.y + 16))
        draw_text(screen, value, small_font, color, (rect.centerx, rect.y + 39))


def draw_board(screen, snake, food, elapsed):
    pygame.draw.rect(screen, BOARD_COLOR, BOARD_RECT, border_radius=14)
    for x in range(BOARD_COLUMNS + 1):
        line_x = BOARD_LEFT + x * CELL_SIZE
        pygame.draw.line(
            screen,
            GRID_COLOR,
            (line_x, BOARD_TOP),
            (line_x, BOARD_TOP + BOARD_HEIGHT),
        )
    for y in range(BOARD_ROWS + 1):
        line_y = BOARD_TOP + y * CELL_SIZE
        pygame.draw.line(
            screen,
            GRID_COLOR,
            (BOARD_LEFT, line_y),
            (BOARD_LEFT + BOARD_WIDTH, line_y),
        )
    pygame.draw.rect(screen, OUTLINE, BOARD_RECT, 2, border_radius=14)

    if food is not None:
        center = (
            int(BOARD_LEFT + food.x * CELL_SIZE + CELL_SIZE / 2),
            int(BOARD_TOP + food.y * CELL_SIZE + CELL_SIZE / 2),
        )
        pulse = 1 + int((math.sin(elapsed * 6) + 1) * 1.5)
        pygame.draw.circle(screen, (104, 40, 62), center, 10 + pulse)
        pygame.draw.circle(screen, PINK, center, 8 + pulse // 2)
        pygame.draw.circle(screen, (255, 216, 221), (center[0] - 2, center[1] - 3), 2)

    for index in range(len(snake) - 1, -1, -1):
        segment = snake[index]
        rect = pygame.Rect(
            int(BOARD_LEFT + segment.x * CELL_SIZE + 2),
            int(BOARD_TOP + segment.y * CELL_SIZE + 2),
            CELL_SIZE - 4,
            CELL_SIZE - 4,
        )
        color = GREEN_LIGHT if index == 0 else (
            GREEN_DARK if index % 2 else GREEN
        )
        pygame.draw.rect(screen, color, rect, border_radius=8)

    if snake:
        head = snake[0]
        center_x = int(BOARD_LEFT + head.x * CELL_SIZE + CELL_SIZE / 2)
        center_y = int(BOARD_TOP + head.y * CELL_SIZE + CELL_SIZE / 2)
        eye_offset = 5
        if len(snake) > 1:
            delta = snake[0] - snake[1]
            if delta.x:
                eyes = ((center_x, center_y - eye_offset), (center_x, center_y + eye_offset))
            else:
                eyes = ((center_x - eye_offset, center_y), (center_x + eye_offset, center_y))
            for eye in eyes:
                pygame.draw.circle(screen, BACKGROUND, eye, 2)


def draw_touch_controls(screen, fonts, mouse_pos):
    _, _, small_font, tiny_font = fonts
    draw_text(screen, "SUR MOBILE", tiny_font, MUTED, (128, 707))
    draw_text(screen, "GLISSE POUR TOURNER", small_font, WHITE, (144, 738))
    draw_text(screen, "OU UTILISE LES FLÈCHES", tiny_font, MUTED, (144, 764))
    center_x = 575
    button_size = 56
    gap = 8
    buttons = {
        "up": pygame.Rect(center_x - button_size // 2, 662, button_size, button_size),
        "left": pygame.Rect(center_x - button_size - gap, 726, button_size, button_size),
        "down": pygame.Rect(center_x - button_size // 2, 726, button_size, button_size),
        "right": pygame.Rect(center_x + gap, 726, button_size, button_size),
    }
    labels = {"up": "↑", "left": "←", "down": "↓", "right": "→"}
    for name, rect in buttons.items():
        draw_button(screen, rect, labels[name], small_font, mouse_pos)
    return buttons


def draw_overlay(screen, fonts, mouse_pos, state, score):
    _, medium_font, small_font, tiny_font = fonts
    shade = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    shade.fill((5, 11, 16, 205))
    screen.blit(shade, (0, 0))

    card = pygame.Rect(120, 260, 480, 280)
    draw_panel(screen, card, fill=(19, 31, 41), border=OUTLINE, radius=22)
    if state == PAUSED:
        title, subtitle = "PAUSE", "La partie est en pause."
        primary_label, secondary_label = "REPRENDRE", "MENU"
    elif state == WON:
        title, subtitle = "BRAVO !", "Tu as rempli tout le plateau."
        primary_label, secondary_label = "REJOUER", "MENU"
    else:
        title, subtitle = "PARTIE TERMINÉE", f"Score final : {score:04d}"
        primary_label, secondary_label = "REJOUER", "MENU"

    draw_text(screen, title, medium_font, GREEN_LIGHT, (360, 322))
    draw_text(screen, subtitle, small_font, MUTED, (360, 366))
    primary_rect = pygame.Rect(163, 416, 240, 58)
    menu_rect = pygame.Rect(420, 416, 137, 58)
    draw_button(
        screen,
        primary_rect,
        primary_label,
        small_font,
        mouse_pos,
        selected=True,
    )
    draw_button(screen, menu_rect, secondary_label, small_font, mouse_pos)
    draw_text(
        screen,
        "P / ESPACE POUR CONTINUER" if state == PAUSED else "ENTRÉE POUR REJOUER",
        tiny_font,
        MUTED,
        (360, 504),
    )
    return primary_rect, menu_rect


def direction_from_key(key):
    directions = {
        pygame.K_UP: pygame.Vector2(0, -1),
        pygame.K_z: pygame.Vector2(0, -1),
        pygame.K_DOWN: pygame.Vector2(0, 1),
        pygame.K_s: pygame.Vector2(0, 1),
        pygame.K_LEFT: pygame.Vector2(-1, 0),
        pygame.K_q: pygame.Vector2(-1, 0),
        pygame.K_a: pygame.Vector2(-1, 0),
        pygame.K_RIGHT: pygame.Vector2(1, 0),
        pygame.K_d: pygame.Vector2(1, 0),
    }
    return directions.get(key)


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake Arcade")
    clock = pygame.time.Clock()

    fonts = (
        pygame.font.Font(None, 62),
        pygame.font.Font(None, 34),
        pygame.font.Font(None, 25),
        pygame.font.Font(None, 19),
    )
    _, medium_font, small_font, _ = fonts
    save_path = Path(__file__).with_name("snake_save.json")
    best_score = load_best_score(save_path)

    random.seed()
    stars = [
        (
            random.randrange(WINDOW_WIDTH),
            random.randrange(WINDOW_HEIGHT),
            random.choice((1, 1, 2)),
            random.random() * math.tau,
        )
        for _ in range(34)
    ]

    selected_difficulty = 1
    state = HOME
    snake, direction, food = new_game()
    next_direction = direction
    score = 0
    elapsed = 0.0
    move_timer = 0.0
    turn_locked = False
    gesture_start = None
    running = True
    animation_time = 0.0
    touch_buttons = {}
    play_rect = pygame.Rect(218, 500, 284, 64)
    difficulty_rects = []
    primary_rect = pygame.Rect(163, 416, 240, 58)
    menu_rect = pygame.Rect(420, 416, 137, 58)

    def start_game():
        nonlocal snake, direction, next_direction, food, score, elapsed
        nonlocal move_timer, turn_locked, state
        snake, direction, food = new_game()
        next_direction = direction
        score = 0
        elapsed = 0.0
        move_timer = 0.0
        turn_locked = False
        state = PLAYING

    def set_direction(candidate):
        nonlocal next_direction, turn_locked
        if turn_locked:
            return
        if candidate.x == -direction.x and candidate.y == -direction.y:
            return
        if candidate == direction:
            return
        next_direction = candidate
        turn_locked = True

    def handle_swipe(start, end):
        delta_x = end[0] - start[0]
        delta_y = end[1] - start[1]
        if max(abs(delta_x), abs(delta_y)) < 32:
            return
        if abs(delta_x) > abs(delta_y):
            set_direction(pygame.Vector2(1 if delta_x > 0 else -1, 0))
        else:
            set_direction(pygame.Vector2(0, 1 if delta_y > 0 else -1))

    while running:
        delta_seconds = min(clock.tick(60) / 1000, 0.1)
        animation_time += delta_seconds
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == HOME:
                    for index, rect in enumerate(difficulty_rects):
                        if rect.collidepoint(event.pos):
                            selected_difficulty = index
                    if play_rect.collidepoint(event.pos):
                        start_game()
                elif state == PLAYING:
                    if PAUSE_BUTTON.collidepoint(event.pos):
                        state = PAUSED
                        move_timer = 0.0
                        gesture_start = None
                    else:
                        gesture_start = event.pos if BOARD_RECT.collidepoint(event.pos) else None
                        for name, rect in touch_buttons.items():
                            if rect.collidepoint(event.pos):
                                set_direction(TOUCH_DIRECTIONS[name])
                elif state in (PAUSED, GAME_OVER, WON):
                    if primary_rect.collidepoint(event.pos):
                        if state == PAUSED:
                            state = PLAYING
                            move_timer = 0.0
                            turn_locked = False
                        else:
                            start_game()
                    elif menu_rect.collidepoint(event.pos):
                        state = HOME
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if state == PLAYING and gesture_start is not None:
                    handle_swipe(gesture_start, event.pos)
                gesture_start = None
            elif event.type == pygame.FINGERDOWN:
                position = (int(event.x * WINDOW_WIDTH), int(event.y * WINDOW_HEIGHT))
                if state == PLAYING:
                    if PAUSE_BUTTON.collidepoint(position):
                        state = PAUSED
                        move_timer = 0.0
                        gesture_start = None
                    else:
                        gesture_start = (
                            position if BOARD_RECT.collidepoint(position) else None
                        )
                        for name, rect in touch_buttons.items():
                            if rect.collidepoint(position):
                                set_direction(TOUCH_DIRECTIONS[name])
                elif state == HOME and play_rect.collidepoint(position):
                    start_game()
                elif state == HOME:
                    for index, rect in enumerate(difficulty_rects):
                        if rect.collidepoint(position):
                            selected_difficulty = index
                elif state in (PAUSED, GAME_OVER, WON):
                    if primary_rect.collidepoint(position):
                        if state == PAUSED:
                            state = PLAYING
                            move_timer = 0.0
                            turn_locked = False
                        else:
                            start_game()
                    elif menu_rect.collidepoint(position):
                        state = HOME
            elif event.type == pygame.FINGERUP:
                position = (int(event.x * WINDOW_WIDTH), int(event.y * WINDOW_HEIGHT))
                if state == PLAYING and gesture_start is not None:
                    handle_swipe(gesture_start, position)
                gesture_start = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == PLAYING:
                        state = PAUSED
                        move_timer = 0.0
                    elif state == PAUSED:
                        state = HOME
                    elif state in (GAME_OVER, WON):
                        state = HOME
                elif state == HOME and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    start_game()
                elif state == PLAYING:
                    if event.key in (pygame.K_p, pygame.K_SPACE):
                        state = PAUSED
                        move_timer = 0.0
                    else:
                        candidate = direction_from_key(event.key)
                        if candidate is not None:
                            set_direction(candidate)
                elif state == PAUSED and event.key in (pygame.K_p, pygame.K_SPACE, pygame.K_RETURN):
                    state = PLAYING
                    move_timer = 0.0
                    turn_locked = False
                elif state in (GAME_OVER, WON) and event.key in (
                    pygame.K_RETURN,
                    pygame.K_r,
                ):
                    start_game()

        if state == PLAYING:
            elapsed += delta_seconds
            move_timer += delta_seconds * 1000
            apples_eaten = score // 10
            move_interval = max(
                42,
                1000 / (DIFFICULTIES[selected_difficulty][1] + apples_eaten // 5),
            )
            if move_timer >= move_interval:
                move_timer %= move_interval
                direction = next_direction
                head = snake[0] + direction
                if (
                    head.x < 0
                    or head.x >= BOARD_COLUMNS
                    or head.y < 0
                    or head.y >= BOARD_ROWS
                ):
                    state = GAME_OVER
                else:
                    eating = head == food
                    body_to_check = snake if eating else snake[:-1]
                    if head in body_to_check:
                        state = GAME_OVER
                    else:
                        snake.insert(0, head)
                        if eating:
                            score += 10
                            food = random_food(snake)
                            if score > best_score:
                                best_score = score
                                save_best_score(save_path, best_score)
                            if food is None:
                                state = WON
                        else:
                            snake.pop()
                turn_locked = False
                if state == GAME_OVER:
                    if score > best_score:
                        best_score = score
                        save_best_score(save_path, best_score)

        if state == HOME:
            play_rect, difficulty_rects = draw_home(
                screen,
                fonts,
                mouse_pos,
                selected_difficulty,
                best_score,
                stars,
                animation_time,
            )
        else:
            draw_background(screen, stars, animation_time)
            draw_header(screen, small_font, medium_font, state, mouse_pos)
            draw_hud(
                screen,
                fonts,
                score,
                best_score,
                score // 50 + 1,
                elapsed,
            )
            draw_board(screen, snake, food, elapsed)
            if state in (PLAYING, PAUSED):
                touch_buttons = draw_touch_controls(screen, fonts, mouse_pos)
            if state in (PAUSED, GAME_OVER, WON):
                primary_rect, menu_rect = draw_overlay(
                    screen, fonts, mouse_pos, state, score
                )

        pygame.display.flip()
        await asyncio.sleep(1 / 60)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
