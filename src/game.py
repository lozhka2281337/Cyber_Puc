import pygame

from entity.enemy import Enemy
from entity.player import Player
from entity.weapon import LaserWeapon 
from dungeon.dungeon_generation import DungeonGeneration as dg

from renderer import Renderer
from handler import Handler

from config import (SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, 
                    SPAWN_ENEMY_EVENT, SPAWN_ENEMY_TIME, 
                    FPS, SHOT_DELAY, BLUE_WALL, TILE_SIZE)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Roguelike Prototype")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.FONT = pygame.font.SysFont("Arial", 32, bold = True)

        self.clock = pygame.time.Clock()

        self.new_game()

    def new_game(self):
        self.bullets = []
        self.health_packs = []
        self.enemies = []
        self.walls = []

        self.dungeon_generator = dg(self.walls)
        start_x, start_y = self.dungeon_generator.get_start_coord()

        self.player = Player(start_x, start_y)
        self.renderer = Renderer(self.screen, self.player, self.walls, self.bullets, self.enemies)
        self.handler = Handler(self.player, self.walls, self.bullets, self.enemies)

        self.running = True

        """ потом убрать"""
        #self.enemies.append(Enemy(100, 100))
        #self.enemies.append(Enemy(-200, 100))
        #self.enemies.append(Enemy(-500, 100))
        #self.walls.append(pygame.Rect(100, -250, 50, 500))
        #self.walls.append(pygame.Rect(-200, -250, 50, 500))
        #self.walls.append(pygame.Rect(-500, -250, 50, 500))

    def death_player(self):
        self.renderer.draw_death_screen()
        
        self.new_game()


    def update(self, dt: float):
        self.player.update(dt, self.walls)

        for weapon in self.player.inventory:
            weapon.update()

        for bullet in self.bullets:
            bullet.update(dt)

        for enemy in self.enemies:
            enemy.update(dt, self.player, self.walls)

        self.handler.process_bullets()
        self.handler.process_player_damage(self)
        self.handler.process_laser_damage()
        self.handler.process_melee_damage()

    """ главная функция """

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  

            camera_x = int(self.player.rect.x + 16 - SCREEN_WIDTH / 2)
            camera_y = int(self.player.rect.y + 16 - SCREEN_HEIGHT / 2)
            
            self.handler.process_events(self, camera_x, camera_y)

            self.update(dt)
            
            camera_x = int(self.player.rect.x + 16 - SCREEN_WIDTH / 2)
            camera_y = int(self.player.rect.y + 16 - SCREEN_HEIGHT / 2)
            
            self.renderer.draw(camera_x, camera_y)