import pygame

from dungeon.BSP.BSP_generation import BSPGeneration as BSP
from dungeon.boos_arena import BossArena

from entity.player import Player
from entity.cyber_core import CyberCore
from entity.elevator import Elevator
from entity.boss import Boss

from core.world import World
from core.renderer import WorldRenderer, DarkRenderer
from core.transition_manager import TransitionManager
from core.handler import Handler
from core.camera import Camera
from core.spawner import Spawner
from core.audio_manager import AudioManager

from menu.main_menu import MainMenu
from menu.terminal import Terminal

import config as cfg


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("CYBER_PUC: 2067")

        self.screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.volume = 100

        self.menu = MainMenu(self, self.screen)
        self.camera = Camera(cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        self.transition_manager = TransitionManager(self.screen, self.camera)
        self.audio_manager = AudioManager()

        self._new_game()

    def run_terminal(self, script):
        self.terminal = Terminal(self.screen, self.player.score, script)

        if script == cfg.SCRIPT_WIN:
            self.audio_manager.play_bgm(cfg.WIN_MUSIC)
        elif script == cfg.SCRIPT_LOSE: 
            self.audio_manager.play_bgm(cfg.BOOM_SOUND)
            self.audio_manager.queue_bgm(cfg.INTRO_MUSIC)
        else:
            self.audio_manager.play_bgm(cfg.INTRO_MUSIC)

        while self.running:
            self.handler.intro_process_events()

            if self.terminal.update(self.audio_manager): break
            self.terminal.draw()

            pygame.display.flip()

        if script == cfg.SCRIPT_INTRO: 
            self.run_game()
        else:
            self.run_menu()

    def run_game(self):
        self.running = True
        self.audio_manager.play_bgm(cfg.DARK_MUSIC)

        while self.running:
            dt = self.get_dt()
            cam_x, cam_y = self.camera.get_offset(self.player.rect)

            if not self.paused: 
                self._update(dt)
                self.handler.game_process_events(cam_x, cam_y)
                self._draw(cam_x, cam_y)
            else: 
                self.menu.update(dt)
                self.handler.menu_process_events()
                self.menu.draw()

            pygame.display.flip()

    def run_menu(self):
        self.audio_manager.play_bgm(cfg.MENU_MUSIC)

        while self.running:
            dt = self.get_dt()

            self.handler.menu_process_events()
            self.menu.update(dt)
            self.menu.draw()

            pygame.display.flip()

    def set_normal_mod(self):
        self.world.mod = cfg.NORMAL_MOD
        self.world.core_activated = True
        self.audio_manager.play_bgm(cfg.ACTION_MUSIC)

    def spawn_boss_in_start_room(self):
        if self.world.boss_spawned:
            return
        if self.world.start_room is None:
            return

        room = self.world.start_room
        boss_x = room.centerx - 32
        boss_y = room.centery - 32

        boss = Boss(boss_x, boss_y, room)
        self.world.enemies.append(boss)
        self.world.boss_spawned = True

    def get_dt(self):
        return min(0.05, self.clock.tick(cfg.FPS) / 1000.0)

    def _new_game(self):
        self.world = World()
        self.dungeon_generator = BSP(self.world)
        
        self.dungeon_generator.generate_dungeon()

        player_x, player_y = self.dungeon_generator.get_start_coord()
        core_x, core_y = self.dungeon_generator.get_cyber_core_coord(player_x, player_y)
        
        self.cyber_core = CyberCore(core_x, core_y)
        self.player = Player(player_x + 100, player_y)
        self.elevator = Elevator(player_x, player_y)
        self.world.start_room = self.dungeon_generator.find_room_by_point(player_x, player_y)

        self.world_renderer = WorldRenderer(self.screen, self.world, self.player, self.elevator, self.cyber_core)
        self.dark_renderer = DarkRenderer(self.screen, self.world, self.player, self.cyber_core)
        self.handler = Handler(self, self.player, self.cyber_core)
        self.boss_arena = BossArena(self.world)

        self.spawner = Spawner(self.world, self.dungeon_generator, self.player)

        self.spawner.spawn_initial()

        self.running = True
        self.paused = False

    def _death_player(self):
        self.run_terminal(cfg.SCRIPT_WIN)

    def _update(self, dt: float):
        self.camera.update(dt)
        self.transition_manager.update(dt)
        self.player.update(dt, self.world)
        self.elevator.update()
        if self.cyber_core: self.cyber_core.update(dt)

        for bullet in self.world.bullets[:]:
            bullet.update(self.world, self.player, dt)
        for grenade in self.world.grenades[:]:
            grenade.update(self.world, self.player, self.camera, dt)
        for effect in self.world.effects[:]:
            effect.update(self.world.effects, dt)
        for enemy in self.world.enemies[:]:
            enemy.update(self.world, self.player, dt)
        for ping in self.world.pings[:]:
            ping.update(self.world, self.player, dt)

        self.player.process_weapon_damage(self.world.enemies, self.world.walls)

        for enemy in self.world.enemies[:]:
            if enemy.hp > 0: continue
            
            self.player.up_score()
            self.world.enemies.remove(enemy)

        for item in self.world.items[:]:
            if self.player.rect.colliderect(item.rect):
                if self.player.hp < cfg.PLAYER_HP:
                    self.player.healling()
                    self.world.items.remove(item)

        if self.player.hp <= 0:
            self._death_player()

        if self.elevator.check_trigger(self.player) and self.world.mod != cfg.BOSS_MOD:
            self._start_second_level()

    def _start_second_level(self):
        self.world.mod = cfg.BOSS_MOD

        self.cyber_core = None

        self.world.clear_map()

        self.player.pos.x = (cfg.MAP_WIDTH // 2 * cfg.TILE_SIZE) - self.player.rect.width // 2
        self.player.pos.y = (cfg.MAP_WIDTH // 2 * cfg.TILE_SIZE) - self.player.rect.height // 2 + 15 * cfg.TILE_SIZE
        self.elevator.rect.x = self.player.pos.x
        self.elevator.rect.y = self.player.pos.y

        self.boss_arena.create_arena()
        self.world_renderer.init_map_surface()

    def _draw(self, cam_x, cam_y):
        current_weapon = self.player.inventory.get_current()
        if hasattr(current_weapon, 'is_firing') and current_weapon.is_firing:
            self.camera.add_shake(3.0)

        self.world_renderer.draw_world(cam_x, cam_y)
        if self.world.mod == cfg.DARK_MOD:
            self.dark_renderer.draw(cam_x, cam_y)
        self.world_renderer.draw_interface()
        self.transition_manager.draw_flash() # отрисовка ослепления при переходе на активный режим