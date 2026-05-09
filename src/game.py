import pygame

from entity.enemy_type import Swarm, Tank, Shooter
from entity.player import Player
from entity.weapon import LaserWeapon 
from dungeon.dungeon_generation import DungeonGeneration as dg

from world import World
from renderer import Renderer
from handler import Handler

from config import (SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, 
                    SPAWN_ENEMY_EVENT, SPAWN_ENEMY_TIME, 
                    FPS, SHOT_DELAY, BLUE_WALL, TILE_SIZE, ENEMY_SIZE)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Roguelike Prototype")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.FONT = pygame.font.SysFont("Arial", 32, bold = True)

        self.clock = pygame.time.Clock()

        self.new_game()

    def new_game(self):
        self.world = World()

        self.dungeon_generator = dg(self.world)
        start_x, start_y = self.dungeon_generator.get_start_coord()

        self.player = Player(start_x, start_y)
        self.renderer = Renderer(self.screen, self.player, self.world)
        self.handler = Handler(self.player, self.world)

        self.running = True

        # УМНЫЙ СПАВН ВРАГОВ
        safe_spots = self.dungeon_generator.get_random_floor_coords(20)
        
        for i, (spot_x, spot_y) in enumerate(safe_spots):
            dist_x = abs(spot_x - start_x)
            dist_y = abs(spot_y - start_y)
            
            if dist_x > 300 or dist_y > 300:
                spawn_x = spot_x + (TILE_SIZE - ENEMY_SIZE) // 2
                spawn_y = spot_y + (TILE_SIZE - ENEMY_SIZE) // 2
                
                # РАСПРЕДЕЛЕНИЕ ТИПОВ ВРАГОВ
                roll = i % 4
                if roll == 0:
                    self.world.enemies.append(Tank(spawn_x, spawn_y))
                elif roll == 1:
                    self.world.enemies.append(Shooter(spawn_x, spawn_y)) 
                else:
                    self.world.enemies.append(Swarm(spawn_x, spawn_y))

    def death_player(self):
        self.renderer.draw_death_screen()
        self.new_game()

    def update(self, dt: float):
        self.player.update(dt, self.world.walls)

        for weapon in self.player.inventory:
            weapon.update()

        for bullet in self.world.bullets:
            bullet.update(dt)

        for grenade in self.world.grenades:
            grenade.update(dt)

        for effect in self.world.effects:
            effect.update(dt)

        for enemy in self.world.enemies:
            enemy.update(dt, self.player, self.world)

        self.handler.process_elements(self)
        self.handler.process_player_damage(self)
        self.handler.process_laser_damage()
        self.handler.process_melee_damage()

    """ главная функция """

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  
            
            if dt > 0.05: 
                dt = 0.05

            camera_x = int(self.player.rect.x + 16 - SCREEN_WIDTH / 2)
            camera_y = int(self.player.rect.y + 16 - SCREEN_HEIGHT / 2)
            
            self.handler.process_events(self, camera_x, camera_y)

            self.update(dt)
            
            camera_x = int(self.player.rect.x + 16 - SCREEN_WIDTH / 2)
            camera_y = int(self.player.rect.y + 16 - SCREEN_HEIGHT / 2)
            
            self.renderer.draw(camera_x, camera_y)