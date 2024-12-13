import pygame
import numpy as np
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Ninja")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

EXPLOSION_COLORS = [RED, ORANGE, YELLOW, WHITE]

LIVES = 3

apple_image = pygame.image.load("Image/apple.png")
watermelon_image = pygame.image.load("Image/watermelon.png")
lemon_image = pygame.image.load("Image/lemon.png")
eggplant_image = pygame.image.load("Image/eggplant.png")
bomb_image = pygame.image.load("Image/bomb.png")
wall_image = pygame.image.load("Image/wall.jpg")


fruit_images = {
    "apple": pygame.transform.scale(apple_image, (80, 80)),
    "watermelon": pygame.transform.scale(watermelon_image, (80, 80)),
    "lemon": pygame.transform.scale(lemon_image, (80, 80)),
    "eggplant": pygame.transform.scale(eggplant_image, (80, 80)),
}
bomb_image = pygame.transform.scale(bomb_image, (80, 80))
wall_image = pygame.transform.scale(wall_image, (WIDTH, HEIGHT))


class Particle:
    def __init__(self, x, y, radius, speed, angle, color, lifetime):
        self.pos = np.array([x, y], dtype=float)
        self.speed = speed
        self.angle = angle
        self.radius = radius
        self.color = color
        self.lifetime = lifetime

    def update(self, dt):
        self.pos[0] += self.speed * math.cos(self.angle) * dt
        self.pos[1] += self.speed * math.sin(self.angle) * dt
        self.lifetime -= dt

    def draw(self, screen):
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)


class Fruit:
    def __init__(self, x, y, radius, speed, angle, image, fruit_type=None, is_bomb=False):
        self.initial_pos = np.array([x, y], dtype=float)
        self.pos = np.array([x, y], dtype=float)
        self.radius = radius
        self.speed = speed
        self.angle = math.radians(angle)
        self.time = 0
        self.gravity = 9.81
        self.split = False
        self.is_bomb = is_bomb
        self.image = image
        self.fruit_type = fruit_type  

    def update(self, dt):
        self.time += dt
        self.pos[0] = self.initial_pos[0] + self.speed * math.cos(self.angle) * self.time
        self.pos[1] = self.initial_pos[1] - (self.speed * math.sin(self.angle) * self.time - 0.5 * self.gravity * self.time ** 2)

    def draw(self, screen):
        if not self.split:
            rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
            screen.blit(self.image, rect)

    def mouse_collision(self, mouse_pos):
        left = self.pos[0] - self.radius  
        right = self.pos[0] + self.radius  
        top = self.pos[1] - self.radius  
        bottom = self.pos[1] + self.radius  
        return left <= mouse_pos[0] <= right and top <= mouse_pos[1] <= bottom


fruits = []
particles = []
spawn_timer = 0
clock = pygame.time.Clock()


fruit_colors = {
    "apple": RED,
    "watermelon": RED,
    "lemon": YELLOW,
    "eggplant": PURPLE,
}


running = True
global_lives = LIVES

while running:
    screen.blit(wall_image, (0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = np.array(pygame.mouse.get_pos(), dtype=float)
            for fruit in fruits:
                if fruit.mouse_collision(mouse_pos):
                    fruit.split = True
                    if fruit.is_bomb:
                        global_lives -= 1
                        for _ in range(20):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = random.uniform(50, 150)
                            radius = random.randint(2, 5)
                            color = random.choice(EXPLOSION_COLORS)
                            lifetime = random.uniform(0.5, 1.5)
                            particles.append(Particle(fruit.pos[0], fruit.pos[1], radius, speed, angle, color, lifetime))
                    else:
                        for _ in range(15):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = random.uniform(30, 100)
                            radius = random.randint(3, 6)
                            color = fruit_colors[fruit.fruit_type]
                            lifetime = random.uniform(0.5, 1.0)
                            particles.append(Particle(fruit.pos[0], fruit.pos[1], radius, speed, angle, color, lifetime))
                    fruits.remove(fruit)

    spawn_timer += 1
    if spawn_timer > 30:
        x = random.randint(100, WIDTH - 100)
        y = HEIGHT + 100
        speed = random.uniform(80, 110)
        angle = random.uniform(70, 110)
        if random.choice([False, False, True]): 
            fruit = Fruit(x, y, 30, speed, angle, bomb_image, is_bomb=True)
        else:
            fruit_type = random.choice(list(fruit_images.keys()))
            fruit_image = fruit_images[fruit_type]
            fruit = Fruit(x, y, 30, speed, angle, fruit_image, fruit_type=fruit_type, is_bomb=False)
        fruits.append(fruit)
        spawn_timer = 0

    dt = 0.1
    for fruit in fruits[:]:
        fruit.update(dt)
        fruit.draw(screen)
        if fruit.pos[1] > HEIGHT + 100:
            fruits.remove(fruit)

    for particle in particles[:]:
        particle.update(dt)
        if particle.lifetime <= 0:
            particles.remove(particle)
        else:
            particle.draw(screen)

    font = pygame.font.SysFont(None, 36)
    lives_text = font.render(f"Lives: {global_lives}", True, (0, 0, 0))
    screen.blit(lives_text, (10, 10))

    if global_lives <= 0:
        game_over_text = font.render("Game Over!", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - 80, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
