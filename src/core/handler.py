import pygame
from projectile.effects import SparkEffect 
from config import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE

class Handler:
    def __init__(self, player, world):
        self.player = player

        self.world = world
        self.walls = world.walls
        self.bullets = world.bullets
        self.enemies = world.enemies
        self.effects = world.effects
        self.grenades = world.grenades

    def process_events(self, game, camera_x: float, camera_y: float) -> bool | None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            
            # выход на esc
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # обработка колесика мышки (переключает оружие)
                if event.button == 4:
                    self.player.switch_weapon(forward=False)
                if event.button == 5:
                    self.player.switch_weapon(forward=True)
                if event.button == 1: 
                    self.player.shot(camera_x, camera_y, game.world)
