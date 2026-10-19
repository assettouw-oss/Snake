import random, pygame, asyncio

CELL_SIZE = 20
CELL_NUMBER = 30
WIDTH = CELL_SIZE * CELL_NUMBER
HEIGHT = CELL_SIZE * CELL_NUMBER
GAME_HEIGHT = HEIGHT - 100

BACKGROUND = (23, 42, 23)
DARK_GREEN = (16, 31, 18)
GREEN = (90, 220, 100)
LIGHT_GREEN = (145, 255, 145)
PINK = (255, 105, 160)
WHITE = (245, 245, 245)
GRAY = (185, 195, 185)
BUTTON_GREEN = (50, 155, 75)
BUTTON_HOVER = (70, 190, 95) 

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    title_font = pygame.font.Font(None, 88)
    medium_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    play_button = pygame.Rect(WIDTH // 2 - 105, HEIGHT // 2 + 35, 210, 65)
    
    def random_food(snake):
        while True:
            f = pygame.Vector2(random.randrange(CELL_NUMBER), random.randrange(GAME_HEIGHT // CELL_SIZE))
            if f not in snake: return f
    
    def new_game():
        start = pygame.Vector2(CELL_NUMBER // 2, (GAME_HEIGHT // CELL_SIZE) // 2)
        snake = [start, start - pygame.Vector2(1,0), start - pygame.Vector2(2,0)]
        return snake, pygame.Vector2(1,0), random_food(snake), 0

    def draw_cell(pos, color):
        rect = pygame.Rect(int(pos.x*CELL_SIZE)+2, int(pos.y*CELL_SIZE)+2, CELL_SIZE-4, CELL_SIZE-4)
        pygame.draw.rect(screen, color, rect, border_radius=5)

    HOME, PLAYING, GAME_OVER = 0,1,2
    state = HOME
    snake, direction, food, score = new_game()
    next_dir = direction
    FPS = 12
    move_timer = 0

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if state in (HOME, GAME_OVER) and play_button.collidepoint(event.pos):
                    snake, direction, food, score = new_game()
                    next_dir = direction
                    state = PLAYING
            if event.type == pygame.KEYDOWN and state == PLAYING:
                if event.key in (pygame.K_UP, pygame.K_z, pygame.K_w) and direction.y == 0: next_dir = pygame.Vector2(0,-1)
                if event.key in (pygame.K_DOWN, pygame.K_s) and direction.y == 0: next_dir = pygame.Vector2(0,1)
                if event.key in (pygame.K_LEFT, pygame.K_q, pygame.K_a) and direction.x == 0: next_dir = pygame.Vector2(-1,0)
                if event.key in (pygame.K_RIGHT, pygame.K_d) and direction.x == 0: next_dir = pygame.Vector2(1,0)

        if state == PLAYING:
            move_timer += 1
            if move_timer > 60 // FPS:
                move_timer = 0
                direction = next_dir
                head = snake[0] + direction
                if not (0 <= head.x < CELL_NUMBER and 0 <= head.y < GAME_HEIGHT // CELL_SIZE) or head in snake[:-1]:
                    state = GAME_OVER
                else:
                    snake.insert(0, head)
                    if head == food:
                        score += 1
                        food = random_food(snake)
                    else:
                        snake.pop()

        screen.fill(BACKGROUND if state==PLAYING else DARK_GREEN)
        if state == HOME:
            screen.fill(DARK_GREEN)
            txt = title_font.render("SNAKE", True, LIGHT_GREEN)
            screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2-80)))
            pygame.draw.rect(screen, BUTTON_HOVER if play_button.collidepoint(mouse_pos) else BUTTON_GREEN, play_button, border_radius=12)
            t = medium_font.render("JOUER", True, WHITE)
            screen.blit(t, t.get_rect(center=play_button.center))
        elif state == PLAYING:
            pygame.draw.circle(screen, PINK, (int(food.x*CELL_SIZE+CELL_SIZE/2), int(food.y*CELL_SIZE+CELL_SIZE/2)), CELL_SIZE//2-2)
            for i,s in enumerate(snake): draw_cell(s, LIGHT_GREEN if i==0 else GREEN)
            screen.blit(medium_font.render(f"Score: {score}", True, WHITE), (12,10))
        else:
            t = medium_font.render(f"GAME OVER - Score: {score}", True, WHITE)
            screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2-40)))
            pygame.draw.rect(screen, BUTTON_GREEN, play_button, border_radius=12)
            t2 = medium_font.render("REJOUER", True, WHITE)
            screen.blit(t2, t2.get_rect(center=play_button.center))

        pygame.display.flip()
        await asyncio.sleep(1/60)
    pygame.quit()

asyncio.run(main())
