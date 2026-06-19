import pygame

from dungeon.BSP.BSP_generation import BSPGeneration as BSP
from entity.player import Player
from entity.cyber_core import CyberCore

from core.world import World
from core.renderer import Renderer
from core.handler import Handler
from core.camera import Camera 
from core.spawner import Spawner
from core.menu import MainMenu

import config as cfg


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("CYBER_PUC: 2067")

        self.screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.menu = MainMenu(self.screen)
        self._new_game()

    def _new_game(self):
        self.world = World()
        self.dungeon_generator = BSP(self.world)
        self.dungeon_generator.generate_dungeon()

        player_x, player_y = self.dungeon_generator.get_start_coord()
        core_x, core_y = self.dungeon_generator.get_cyber_core_coord(player_x, player_y)
        
        self.cyber_core = CyberCore(core_x, core_y)
        self.player = Player(player_x, player_y)
        self.renderer = Renderer(self.screen, self.player, self.cyber_core, self.world)
        self.handler = Handler(self.player, self.cyber_core, self.world)
        self.camera = Camera(cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        self.spawner = Spawner(self.world, self.dungeon_generator, self.player)
        
        self.spawner.spawn_initial()  
        
        self.running = True 

    def _death_player(self):
        self.renderer.draw_death_screen()
        self._new_game()

    def _update(self, dt: float):
        self.player.update(dt, self.world)   
        self.cyber_core.update()

        for bullet in self.world.bullets[:]:
            bullet.update(self.world, self.player, dt)

        for grenade in self.world.grenades[:]:
            grenade.update(self.world, self.camera, dt)
  
        for effect in self.world.effects[:]:
            effect.update(self.world.effects, dt)

        for enemy in self.world.enemies[:]:
            enemy.update(self.world, self.player, dt)

        for ping in self.world.pings[:]:
            ping.update(self.world, self.player, dt)

        self.player.process_weapon_damage(self.world.enemies, self.world.walls)
        self.world.enemies[:] = [enemy for enemy in self.world.enemies if enemy.hp > 0]
        
        for item in self.world.items[:]:
            if self.player.rect.colliderect(item.rect):
                if self.player.hp < cfg.PLAYER_HP: 
                    self.player.hp += 1
                    self.world.items.remove(item)

        if self.player.hp <= 0:
            self._death_player()

    def _draw(self, cam_x, cam_y, dt):
        current_weapon = self.player.inventory.get_current()
        if hasattr(current_weapon, 'is_firing') and current_weapon.is_firing:
            self.camera.add_shake(3.0) 

        self.renderer.draw(cam_x, cam_y)

    def run_game(self):
        while self.running:
            dt = min(0.05, self.clock.tick(cfg.FPS) / 1000.0)

            cam_x, cam_y = self.camera.get_offset(self.player.rect, dt)
            
            self.handler.game_process_events(self, cam_x, cam_y)
            self._update(dt)
            self._draw(cam_x, cam_y, dt)

    def run_menu(self):
        while self.running:
            new_state = self.handler.menu_process_events(self)

            if new_state == cfg.START_GAME_BUTTON:
                self.run_game()
                return
            elif new_state == cfg.SETTINGS_BUTTON:
                pass
            elif new_state == cfg.EXIT_BUTTON:
                pygame.quit()
                return

            dt = min(0.05, self.clock.tick(cfg.FPS) / 1000.0)

            self.menu.draw(dt)
            pygame.display.flip()