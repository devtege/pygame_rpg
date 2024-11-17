import pygame
import sys
import random

pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)  # Changed the player color to red for better visibility
GRASS = (0, 255, 0)
GRASS2 = (0, 230, 0)
GRASS3 = (0, 200, 0)
GRASS4 = (24, 129, 24)
WATER = (0, 0, 255)
DIRT = (139, 69, 19)
DIRT2 = (160, 82, 45)

# Other constants
TILE_SIZE = 50
FPS = 30
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 40
MAP_WIDTH = 64
MAP_HEIGHT = 48

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pocket RPG")

class Tile(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = x, y

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PLAYER_SIZE, PLAYER_SIZE])
        self.image.fill(RED)  # Changed to red for better visibility
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5

    def update(self, map_data, camera_rect):
        keys = pygame.key.get_pressed()

        new_x = self.rect.x
        new_y = self.rect.y

        if keys[pygame.K_LEFT]:
            new_x -= self.speed
        if keys[pygame.K_RIGHT]:
            new_x += self.speed
        if keys[pygame.K_UP]:
            new_y -= self.speed
        if keys[pygame.K_DOWN]:
            new_y += self.speed

        # Check next position for water
        next_tile_x = (new_x + PLAYER_SIZE // 2) // TILE_SIZE
        next_tile_y = (new_y + PLAYER_SIZE // 2) // TILE_SIZE

        # Move player only if next tile is valid and not water
        if (0 <= next_tile_x < MAP_WIDTH and 
            0 <= next_tile_y < MAP_HEIGHT and 
            map_data[next_tile_y][next_tile_x] != WATER):
            self.rect.x = new_x
            self.rect.y = new_y

        # Update camera to center around the player, but keep the player within bounds
        camera_rect.centerx = self.rect.centerx
        camera_rect.centery = self.rect.centery

        # Prevent camera from going out of bounds (the edges of the map)
        camera_rect.left = max(0, camera_rect.left)
        camera_rect.top = max(0, camera_rect.top)
        camera_rect.right = min(MAP_WIDTH * TILE_SIZE, camera_rect.right)
        camera_rect.bottom = min(MAP_HEIGHT * TILE_SIZE, camera_rect.bottom)

def smooth_map(map_data, iterations=2):
    for _ in range(iterations):
        new_map = [[tile for tile in row] for row in map_data]
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if x > 0 and x < MAP_WIDTH-1 and y > 0 and y < MAP_HEIGHT-1:
                    water_count = sum(1 for dy in [-1, 0, 1] for dx in [-1, 0, 1]
                                    if map_data[y + dy][x + dx] == WATER)
                    if water_count >= 5:
                        new_map[y][x] = WATER
                    elif water_count <= 3:
                        new_map[y][x] = GRASS
        map_data = new_map
    return map_data

def generate_map():
    map_data = [[GRASS for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    
    # Reduce the number of water bodies
    for _ in range(MAP_WIDTH * MAP_HEIGHT // 65):
        center_x = random.randint(0, MAP_WIDTH-1)
        center_y = random.randint(0, MAP_HEIGHT-1)
        size = random.randint(2, 4)
        
        for y in range(max(0, center_y-size), min(MAP_HEIGHT, center_y+size)):
            for x in range(max(0, center_x-size), min(MAP_WIDTH, center_x+size)):
                if random.random() < 0.7:
                    map_data[y][x] = WATER
    
    map_data = smooth_map(map_data)
    
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if map_data[y][x] != WATER:
                rand = random.random()
                if rand < 0.1:
                    map_data[y][x] = DIRT
                elif rand < 0.2:
                    map_data[y][x] = DIRT2
                elif rand < 0.5:
                    map_data[y][x] = GRASS2
                elif rand < 0.7:
                    map_data[y][x] = GRASS3
                elif rand < 0.9:
                    map_data[y][x] = GRASS4
    
    return map_data

def render_map(map_data, camera_rect, player_rect):
    tiles = pygame.sprite.Group()

    # Calculate visible range with a buffer around the player
    player_x, player_y = player_rect.centerx, player_rect.centery
    start_col = max(0, (player_x // TILE_SIZE) - 10)
    end_col = min(MAP_WIDTH, (player_x // TILE_SIZE) + 10)
    start_row = max(0, (player_y // TILE_SIZE) - 7)
    end_row = min(MAP_HEIGHT, (player_y // TILE_SIZE) + 7)
    
    # Only render tiles around the player
    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            x = col * TILE_SIZE - camera_rect.x
            y = row * TILE_SIZE - camera_rect.y
            tile = Tile(map_data[row][col], x, y)
            tiles.add(tile)
            
    return tiles

# Setup
player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

map_data = generate_map()

# Make sure player doesn't spawn on water
valid_start = False
while not valid_start:
    start_x = random.randint(0, MAP_WIDTH - 1)
    start_y = random.randint(0, MAP_HEIGHT - 1)
    if map_data[start_y][start_x] != WATER:
        player.rect.centerx = start_x * TILE_SIZE + TILE_SIZE // 2
        player.rect.centery = start_y * TILE_SIZE + TILE_SIZE // 2
        valid_start = True

camera_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
clock = pygame.time.Clock()

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update player and camera
    player.update(map_data, camera_rect)

    # Clear the screen
    screen.fill(BLACK)

    # Render map with camera offset
    tiles = render_map(map_data, camera_rect, player.rect)
    tiles.draw(screen)

    # Draw the player (ensure player is drawn last so it appears on top)
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()