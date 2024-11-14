import pygame
import sys
import random
import noise

pygame.init()

# Colors
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
        self.image.fill(WHITE)
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

        # Check both current and next position tiles for water
        current_tile_x = self.rect.centerx // TILE_SIZE
        current_tile_y = self.rect.centery // TILE_SIZE
        next_tile_x = (new_x + PLAYER_SIZE // 2) // TILE_SIZE
        next_tile_y = (new_y + PLAYER_SIZE // 2) // TILE_SIZE

        # Only move if the next position is within bounds and not water
        if (0 <= next_tile_x < MAP_WIDTH and 
            0 <= next_tile_y < MAP_HEIGHT and 
            map_data[next_tile_y][next_tile_x] != WATER):
            self.rect.x = new_x
            self.rect.y = new_y

        # Update camera position
        camera_rect.x = self.rect.centerx - SCREEN_WIDTH // 2
        camera_rect.y = self.rect.centery - SCREEN_HEIGHT // 2

        # Keep camera within map bounds
        camera_rect.clamp_ip(pygame.Rect(0, 0, 
                                       MAP_WIDTH * TILE_SIZE, 
                                       MAP_HEIGHT * TILE_SIZE))

def generate_map():
    map_data = []
    scale = 50.0  # Adjust this to change the scale of the terrain
    octaves = 6    # Number of passes for the noise
    persistence = 0.5
    lacunarity = 2.0
    
    # Generate base noise map
    for row in range(MAP_HEIGHT):
        current_row = []
        for col in range(MAP_WIDTH):
            nx = col/MAP_WIDTH - 0.5
            ny = row/MAP_HEIGHT - 0.5
            
            # Generate Perlin noise value
            value = noise.pnoise2(nx*scale, 
                                ny*scale, 
                                octaves=octaves, 
                                persistence=persistence, 
                                lacunarity=lacunarity, 
                                repeatx=MAP_WIDTH, 
                                repeaty=MAP_HEIGHT, 
                                base=42)
            
            # Normalize the value to 0-1 range
            value = (value + 1) / 2
            
            # Assign terrain based on noise value
            if value < 0.2:
                tile = WATER
            elif value < 0.3:
                tile = DIRT
            elif value < 0.4:
                tile = DIRT2
            elif value < 0.7:
                tile = GRASS4
            elif value < 0.8:
                tile = GRASS3
            elif value < 0.9:
                tile = GRASS2
            else:
                tile = GRASS
                
            current_row.append(tile)
        map_data.append(current_row)
    
    return map_data

def render_map(map_data, camera_rect):
    tiles = pygame.sprite.Group()
    
    # Calculate visible range
    start_col = max(0, camera_rect.left // TILE_SIZE)
    end_col = min(MAP_WIDTH, (camera_rect.right // TILE_SIZE) + 1)
    start_row = max(0, camera_rect.top // TILE_SIZE)
    end_row = min(MAP_HEIGHT, (camera_rect.bottom // TILE_SIZE) + 1)
    
    # Only render visible tiles
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

# Find a valid starting position for the player (not on water)
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

    player.update(map_data, camera_rect)

    screen.fill(BLACK)

    tiles = render_map(map_data, camera_rect)
    tiles.draw(screen)

    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()