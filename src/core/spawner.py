import pygame 
import random

from entity.enemy_type import Swarm, Tank, Shooter
from entity.items import HealthPack 

import config as cfg

class Spawner:
    def __init__(self, world, dungeon_generator, player):
        self.world = world
        self.dungeon_generator = dungeon_generator
        self.player = player

    def spawn_initial(self):
        self._spawn_enemies()
        self._spawn_items()

    def spawn_second_floor_wave(self):
        enemy_count = random.randint(cfg.SECOND_FLOOR_WAVE_MIN, cfg.SECOND_FLOOR_WAVE_MAX)
        arena_room = pygame.Rect(0, 0, cfg.MAP_WIDTH * cfg.TILE_SIZE, cfg.MAP_HEIGHT * cfg.TILE_SIZE)

        for _ in range(enemy_count):
            spawn_x, spawn_y = self._get_safe_arena_spawn_pos(cfg.ENEMY_SIZE)

            roll = random.random()
            if roll < 0.2:
                enemy = Tank(spawn_x, spawn_y, arena_room)
            elif roll < 0.5:
                enemy = Shooter(spawn_x, spawn_y, arena_room)
            else:
                enemy = Swarm(spawn_x, spawn_y, arena_room)

            self.world.enemies.append(enemy)

    def _spawn_enemies(self):
        spawned_count = 0
        shuffled_rooms = random.sample(self.world.rooms, len(self.world.rooms))

        for room in shuffled_rooms:
            if spawned_count >= cfg.INITIAL_ENEMY_COUNT:
                break

            if room.collidepoint(self.player.pos.x, self.player.pos.y):
                continue

            remaining = cfg.INITIAL_ENEMY_COUNT - spawned_count
            
            # Динамические границы: защита от краша, если остался 1 враг до лимита
            min_group = min(2, remaining)
            max_group = min(5, remaining)
            
            group_size = random.randint(min_group, max_group)
            
            for _ in range(group_size):
                spawn_x, spawn_y = self._get_safe_spawn_pos(room, cfg.ENEMY_SIZE)
                
                roll = random.random()
                if roll < 0.2:
                    enemy = Tank(spawn_x, spawn_y, room)
                elif roll < 0.5:
                    enemy = Shooter(spawn_x, spawn_y, room)
                else:
                    enemy = Swarm(spawn_x, spawn_y, room)
                    
                self.world.enemies.append(enemy)
                spawned_count += 1

    def _spawn_items(self):
        item_count = min(10, len(self.world.rooms))
        rooms_for_items = random.sample(self.world.rooms, item_count)
        
        for room in rooms_for_items:
            spawn_x, spawn_y = self._get_safe_spawn_pos(room, cfg.HEALTH_PACK_SIZE)
            self.world.items.append(HealthPack(spawn_x, spawn_y))

    def _get_safe_spawn_pos(self, room: pygame.Rect, entity_size: int) -> tuple[int, int]:
        margin = cfg.TILE_SIZE
        if room.width > margin * 2 + entity_size and room.height > margin * 2 + entity_size:
            x = random.randint(room.left + margin, room.right - margin - entity_size)
            y = random.randint(room.top + margin, room.bottom - margin - entity_size)
        else:
            x = room.centerx - entity_size // 2
            y = room.centery - entity_size // 2
            
        return x, y

    def _get_safe_arena_spawn_pos(self, entity_size: int) -> tuple[int, int]:
        floor_tiles = []
        player_tile_x = int(self.player.pos.x // cfg.TILE_SIZE)
        player_tile_y = int(self.player.pos.y // cfg.TILE_SIZE)

        for y in range(cfg.MAP_HEIGHT):
            for x in range(cfg.MAP_WIDTH):
                if self.world.matrix[y][x] != 0:
                    continue

                if abs(x - player_tile_x) <= 4 and abs(y - player_tile_y) <= 4:
                    continue

                floor_tiles.append((x, y))

        if not floor_tiles:
            return self.player.rect.centerx, self.player.rect.centery

        tile_x, tile_y = random.choice(floor_tiles)
        spawn_x = tile_x * cfg.TILE_SIZE + (cfg.TILE_SIZE - entity_size) // 2
        spawn_y = tile_y * cfg.TILE_SIZE + (cfg.TILE_SIZE - entity_size) // 2
        return spawn_x, spawn_y