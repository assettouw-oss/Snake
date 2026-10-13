import asyncio
import pygame
import random

pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

snake = [(200, 200)]
direction = (20, 0)
food = (300, 200)
score = 0

def new_food():
    return (random.randint(0, (WIDTH-20)//20)*20, random.randint(0, (HEIGHT-20)//20)*20)

async def main():
    global snake, direction, food, score
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction!= (0, 20):
                    direction = (0, -20)
                if event.key == pygame.K_DOWN and direction!= (0, -20):
                    direction = (0, 20)
                if event.key == pygame.K_LEFT and direction!= (20, 0):
                    direction = (-20, 0)
                if event.key == pygame.K_RIGHT and direction!= (-20, 0):
                    direction = (20, 0)

        # bouge serpent
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        # murs
        if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT or head in snake:
            snake = [(200, 200)]
            direction = (20, 0)
            score = 0
            food = new_food()
            continue

        snake.insert(0, head)
        if head == food:
            score += 1
            food = new_food()
        else:
            snake.pop()

        screen.fill((0, 0, 0))
        for s in snake:
            pygame.draw.rect(screen, (0, 255, 0), (*s, 20, 20))
        pygame.draw.rect(screen, (255, 0, 0), (*food, 20, 20))
        pygame.display.flip()
        clock.tick(10)
        await asyncio.sleep(0)

asyncio.run(main())


