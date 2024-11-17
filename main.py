import pygame
import sys
import random

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
PLAYER_SIZE = 50
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
        self.pos = pygame.Vector2(self.rect.center)  # Use Vector2 for smoother movement
        self.speed = 5
        self.velocity = pygame.Vector2(0, 0)  # Player's velocity for smooth movement

    def update(self, keys, map_data, camera_rect):
        # Apply velocity changes based on input
        if keys[pygame.K_LEFT]:
            self.velocity.x = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.velocity.x = self.speed
        else:
            self.velocity.x = 0  # Stop horizontal movement if no key is pressed

        if keys[pygame.K_UP]:
            self.velocity.y = -self.speed
        elif keys[pygame.K_DOWN]:
            self.velocity.y = self.speed
        else:
            self.velocity.y = 0  # Stop vertical movement if no key is pressed

        # Apply acceleration for smoother movement
        self.pos += self.velocity

        # Check if player hits water at their new position
        new_rect = self.rect.copy()
        new_rect.center = self.pos  # Get the new potential position
        if self.is_on_water(map_data, new_rect):
            return  # Don't update position if it's water

        # Update the player's position (convert from Vector2 back to int)
        self.rect.center = self.pos

        # Prevent player from moving out of bounds
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - PLAYER_SIZE))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - PLAYER_SIZE))

        # Update camera to follow the player smoothly
        camera_rect.center = self.rect.center
        self.update_camera_bounds(camera_rect)

    def is_on_water(self, map_data, rect):
        """Check if any corner of the player is on a water tile."""
        corners = [
            (rect.left, rect.top),
            (rect.right, rect.top),
            (rect.left, rect.bottom),
            (rect.right, rect.bottom)
        ]

        for corner in corners:
            tile_x = corner[0] // TILE_SIZE
            tile_y = corner[1] // TILE_SIZE
            if 0 <= tile_x < MAP_WIDTH and 0 <= tile_y < MAP_HEIGHT:
                if map_data[tile_y][tile_x] == WATER:
                    return True
        return False

    def update_camera_bounds(self, camera_rect):
        """Clamp the camera to keep it within the bounds of the map."""
        camera_rect.left = max(0, camera_rect.left)
        camera_rect.top = max(0, camera_rect.top)
        camera_rect.right = min(MAP_WIDTH * TILE_SIZE, camera_rect.right)
        camera_rect.bottom = min(MAP_HEIGHT * TILE_SIZE, camera_rect.bottom)


def smooth_map(map_data, iterations=2):
    for _ in range(iterations):
        new_map = [[tile for tile in row] for row in map_data]
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if x > 0 and x < MAP_WIDTH - 1 and y > 0 and y < MAP_HEIGHT - 1:
                    water_count = sum(1 for dy in [-1, 0, 1] for dx in [-1, 0, 1]
                                      if map_data[y + dy][x + dx] == WATER)
                    if water_count >= 5:
                        new_map[y][x] = WATER
                    elif water_count <= 3:
                        new_map[y][x] = GRASS
        map_data = new_map
    return map_data


def generate_map():
    # Initialize the map with random tiles (water or land)
    map_data = [[GRASS if random.random() > 0.4 else WATER for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

    # Apply the Cellular Automata rules to improve the map's structure
    for _ in range(5):  # Run multiple iterations to smooth the map
        map_data = cellular_automata(map_data)

    # Replace some grass with dirt, grass2, etc., for variety
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


def cellular_automata(map_data):
    new_map = [[tile for tile in row] for row in map_data]

    for y in range(1, MAP_HEIGHT - 1):
        for x in range(1, MAP_WIDTH - 1):
            # Count the number of adjacent water tiles
            water_count = sum(1 for dy in [-1, 0, 1] for dx in [-1, 0, 1] if map_data[y + dy][x + dx] == WATER)

            # Apply the rules: if too many water tiles, make this a water tile
            if water_count >= 5:
                new_map[y][x] = WATER
            elif water_count <= 3:
                new_map[y][x] = GRASS

    return new_map


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

    keys = pygame.key.get_pressed()
    player.update(keys, map_data, camera_rect)

    screen.fill(BLACK)

    tiles = render_map(map_data, camera_rect, player.rect)
    tiles.draw(screen)

    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
