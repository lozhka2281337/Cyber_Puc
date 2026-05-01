import random
import pygame

from config import TILE_SIZE, ROWS, COLS#, MAP_WIDTH, MAP_HEIGHT

MAP_WIDTH = 100
MAP_HEIGHT = 100

# ГЕНЕРАЦИЯ УРОВНЯ (

class DungeonGeneration:
    def __init__(self, walls, n=4000):
        self.n = n
        self.walls = walls

        self.dungeon_map = [[1 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.directions = [[0, 1], [1, 0], [-1, 0], [0, -1]]
        
        self.generate_dungeon()

    def generate_dungeon(self):
        x = random.randint(1, MAP_WIDTH-2)
        y = random.randint(1, MAP_HEIGHT-2)

        steps_made = 0
        while steps_made < self.n:
            dx, dy = random.choice(self.directions)
            
            if 1 <= x + dx < MAP_WIDTH - 1 and 1 <= y + dy < MAP_HEIGHT - 1:
                x += dx
                y += dy

                if self.dungeon_map[y][x] == 1: 
                    self.dungeon_map[y][x] = 0
                    steps_made += 1

        self.create_walls()

    def create_walls(self):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if self.dungeon_map[y][x] == 1:
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    self.walls.append(rect)
            
    def get_start_coord(self):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if self.dungeon_map[y][x] == 0:
                    return x * TILE_SIZE, y * TILE_SIZE
                    
        return TILE_SIZE, TILE_SIZE

    def get_random_floor_coords(self, count):
        floors = []
        
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if self.dungeon_map[y][x] == 0:
                    floors.append((x * TILE_SIZE, y * TILE_SIZE))
        
        if len(floors) < count:
            return floors
        return random.sample(floors, count)