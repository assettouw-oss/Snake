import random, os, math
import pygame

pygame.init()
try:
    pygame.mixer.init()
    MUSIC_ENABLED = True
except:
    MUSIC_ENABLED = False

CELL_SIZE = 20
CELL_NUMBER = 30
WIDTH = CELL_SIZE * CELL_NUMBER
HEIGHT = CELL_SIZE * CELL_NUMBER
GAME_HEIGHT = HEIGHT - 100
FPS = 8

BACKGROUND = (23, 42, 23)
DARK_GREEN = (16, 31, 18)
GREEN = (90, 220, 100)
LIGHT_GREEN = (145, 255, 145)
PINK = (255, 105, 160)
WHITE = (245, 245, 245)
GRAY = (185, 195, 185)
BUTTON_GREEN = (50, 155, 75)
BUTTON_HOVER = (70, 190, 95)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SNAKE")
clock = pygame.time.Clock()
title_font = pygame.font.Font(None, 88)
large_font = pygame.font.Font(None, 58)
medium_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
arrow_font = pygame.font.Font(None, 48)

play_button = pygame.Rect(WIDTH // 2 - 105, HEIGHT // 2 + 35, 210, 65)
BUTTON_SIZE = 54
CX = WIDTH // 2
CY = GAME_HEIGHT + 48
UP_BUTTON = pygame.Rect(CX - BUTTON_SIZE // 2, CY - 56, BUTTON_SIZE, BUTTON_SIZE)
LEFT_BUTTON = pygame.Rect(CX - BUTTON_SIZE - 12, CY, BUTTON_SIZE, BUTTON_SIZE)
DOWN_BUTTON = pygame.Rect(CX - BUTTON_SIZE // 2, CY, BUTTON_SIZE, BUTTON_SIZE)
RIGHT_BUTTON = pygame.Rect(CX + 12, CY, BUTTON_SIZE, BUTTON_SIZE)

def draw_text(text, font, color, center):
    surf = font.render(text, True, color)
    screen.blit(surf, surf.get_rect(center=center))

def draw_button(rect, label, mouse_pos, font=medium_font):
    color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_GREEN
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, LIGHT_GREEN, rect, 2, border_radius=12)
    draw_text(label, font, WHITE, rect.center)

def random_food(snake):
    while True:
        food = pygame.Vector2(random.randrange(CELL_NUMBER), random.randrange(GAME_HEIGHT // CELL_SIZE))
        if food not in snake:
            return food

def new_game():
    start = pygame.Vector2(CELL_NUMBER // 2, (GAME_HEIGHT // CELL_SIZE) // 2)
    snake = [start, start - pygame.Vector2(1, 0), start - pygame.Vector2(2, 0)]
    direction = pygame.Vector2(1, 0)
    return snake, direction, direction, random_food(snake), 0

def draw_cell(pos, color):
    rect = pygame.Rect(int(pos.x * CELL_SIZE) + 2, int(pos.y * CELL_SIZE) + 2, CELL_SIZE - 4, CELL_SIZE - 4)
    pygame.draw.rect(screen, color, rect, border_radius=5)

def draw_controls(mouse_pos):
    pygame.draw.rect(screen, DARK_GREEN, (0, GAME_HEIGHT, WIDTH, HEIGHT - GAME_HEIGHT))
    draw_text("DIRECTION", small_font, GRAY, (WIDTH // 2, GAME_HEIGHT + 14))
    draw_button(UP_BUTTON, "↑", mouse_pos, arrow_font)
    draw_button(LEFT_BUTTON, "←", mouse_pos, arrow_font)
    draw_button(DOWN_BUTTON, "↓", mouse_pos, arrow_font)
    draw_button(RIGHT_BUTTON, "→", mouse_pos, arrow_font)

def draw_game(snake, food, score, mouse_pos):
    screen.fill(BACKGROUND)
    pygame.draw.circle(screen, PINK, (int(food.x * CELL_SIZE + CELL_SIZE / 2), int(food.y * CELL_SIZE + CELL_SIZE / 2)), CELL_SIZE // 2 - 2)
    for i, segment in enumerate(snake):
        draw_cell(segment, LIGHT_GREEN if i == 0 else GREEN)
    screen.blit(medium_font.render(f"Score : {score}", True, WHITE), (12, 10))
    draw_controls(mouse_pos)

def draw_home(mouse_pos):
    screen.fill(DARK_GREEN)
    pygame.draw.circle(screen, BACKGROUND, (WIDTH // 2, HEIGHT // 2 - 55), 135)
    draw_text("SNAKE", title_font, LIGHT_GREEN, (WIDTH // 2, HEIGHT // 2 - 115))
    draw_text("Mange les fruits et grandis !", small_font, GRAY, (WIDTH // 2, HEIGHT // 2 - 48))
    for i in range(5):
        pygame.draw.rect(screen, LIGHT_GREEN if i == 0 else GREEN, (WIDTH // 2 - 50 + i * 23, HEIGHT // 2 - 15, 19, 19), border_radius=5)
    draw_button(play_button, "JOUER", mouse_pos)

def draw_game_over(mouse_pos, score):
    screen.fill(DARK_GREEN)
    draw_text("GAME OVER", large_font, WHITE, (WIDTH // 2, HEIGHT // 2 - 100))
    draw_text(f"Score final : {score}", medium_font, LIGHT_GREEN, (WIDTH // 2, HEIGHT // 2 - 45))
    draw_button(play_button, "REJOUER", mouse_pos)

def set_direction(new_direction):
    global next_direction
    if new_direction.x != -direction.x or new_direction.y != -direction.y:
        next_direction = new_direction

def handle_direction_button(pos):
    if UP_BUTTON.collidepoint(pos): set_direction(pygame.Vector2(0, -1))
    elif DOWN_BUTTON.collidepoint(pos): set_direction(pygame.Vector2(0, 1))
    elif LEFT_BUTTON.collidepoint(pos): set_direction(pygame.Vector2(-1, 0))
    elif RIGHT_BUTTON.collidepoint(pos): set_direction(pygame.Vector2(1, 0))

HOME, PLAYING, GAME_OVER = "home", "playing", "game_over"
state = HOME
snake, direction, next_direction, food, score = new_game()
running = True
move_event = pygame.USEREVENT + 1
pygame.time.set_timer(move_event, 1000 // FPS)

while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state in (HOME, GAME_OVER) and play_button.collidepoint(event.pos):
                snake, direction, next_direction, food, score = new_game()
                state = PLAYING
            elif state == PLAYING: handle_direction_button(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state == PLAYING: state = HOME
                else: running = False
            elif state == HOME and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                snake, direction, next_direction, food, score = new_game()
                state = PLAYING
            elif state == GAME_OVER and event.key == pygame.K_r:
                snake, direction, next_direction, food, score = new_game()
                state = PLAYING
            elif state == PLAYING:
                if event.key in (pygame.K_UP, pygame.K_z): set_direction(pygame.Vector2(0, -1))
                elif event.key in (pygame.K_DOWN, pygame.K_s): set_direction(pygame.Vector2(0, 1))
                elif event.key in (pygame.K_LEFT, pygame.K_q): set_direction(pygame.Vector2(-1, 0))
                elif event.key in (pygame.K_RIGHT, pygame.K_d): set_direction(pygame.Vector2(1, 0))
        elif event.type == move_event and state == PLAYING:
            direction = next_direction
            head = snake[0] + direction
            if head.x < 0 or head.x >= CELL_NUMBER or head.y < 0 or head.y >= GAME_HEIGHT // CELL_SIZE:
                state = GAME_OVER; continue
            eating = head == food
            body = snake if eating else snake[:-1]
            if head in body:
                state = GAME_OVER; continue
            snake.insert(0, head)
            if eating:
                score += 1
                food = random_food(snake)
            else:
                snake.pop()

    if state == HOME: draw_home(mouse_pos)
    elif state == PLAYING: draw_game(snake, food, score, mouse_pos)
    else: draw_game_over(mouse_pos, score)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
