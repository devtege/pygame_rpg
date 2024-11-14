import pygame
import sys
import random

pygame.init()


# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRASS = (0, 255, 0)
GRASS2 = (0, 230, 0)
GRASS3 = (0, 200, 0)
GRASS4 = (24, 129, 24)
WATER = (0, 0, 255)
DIRT = (139, 69, 19)
DIRT2 = (160, 82, 45)

# other constants
TILE_SIZE = 50
FPS = 30
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 40

# create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pocket RPG")

# class for the tiles
class Tile(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = x, y


# class for the player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PLAYER_SIZE, PLAYER_SIZE])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed


# Creating the map
def generate_map():
        map_data = []
        tile_types = [GRASS, GRASS, GRASS2, GRASS, GRASS3, GRASS4,  DIRT, DIRT2, WATER]

        # creating a map with random tiles
        for row in range(12):
            row_data = []
            for col in range(16):
                tile = random.choice(tile_types)
                row_data.append(tile)
            map_data.append(row_data)
        return map_data


# Rendering the map
def render_map(map_data):
    tiles = pygame.sprite.Group()
    for row_num, row in enumerate(map_data):
        for col_num, tile_color in enumerate(row):
            x = col_num * TILE_SIZE
            y = row_num * TILE_SIZE
            tile = Tile(tile_color, x, y)
            tiles.add(tile)
    return tiles


# setup
player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# generating the map
map_data = generate_map()
tiles = render_map(map_data)
tile_group = pygame.sprite.Group()
tile_group.add(tiles)

clock = pygame.time.Clock()

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    all_sprites.update()

    screen.fill(BLACK)

    tiles.draw(screen)
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()