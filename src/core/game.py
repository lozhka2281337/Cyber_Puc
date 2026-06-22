import pygame

from dungeon.BSP.BSP_generation import BSPGeneration as BSP
from entity.player import Player
from entity.cyber_core import CyberCore
from entity.boss import Boss

from core.world import World
from core.renderer import WorldRenderer, DarkRenderer
from core.transition_manager import TransitionManager
from core.handler import Handler
from core.camera import Camera
from core.spawner import Spawner
from core.menu import MainMenu
from core.pause_menu import PauseMenu
from core.audio_manager import AudioManager
from core.intro import TerminalIntro

import config as cfg


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("CYBER_PUC: 2067")

        self.screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.menu = MainMenu(self.screen)
        self._new_game()

    def run_intro(self):
        self.audio_manager.play_bgm(cfg.MENU_MUSIC)

        while self.running:
            events = pygame.event.get()
            self.handler.intro_process_events(self, events)

            if self.terminal_intro.update():
                break

            self.terminal_intro.draw()

        self.world.mod = cfg.DARK_MOD
        self.running = True
        self.run_game()


    def run_game(self):
        while self.running:
            dt = min(0.05, self.clock.tick(cfg.FPS) / 1000.0)
            cam_x, cam_y = self.camera.get_offset(self.player.rect)
            events = pygame.event.get()

            # ПАуза
            if self.paused:
                # 1. Рисуем мир
                self.world_renderer.draw_world(cam_x, cam_y)
                if self.world.mod == cfg.DARK_MOD:
                    self.dark_renderer.draw(cam_x, cam_y)
                self.world_renderer.draw_interface()
                self.transition_manager.draw_flash()

                # 2. Рисуем затемнение
                self.screen.blit(self.pause_overlay, (0, 0))

                # 3. Рисуем меню паузы
                self.pause_menu.draw(dt)

                # 4. Обновляем экран ТОЛЬКО ОДИН РАЗ
                pygame.display.flip()

                # Обработка событий меню паузы
                for event in events:
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.paused = False

                    button = self.pause_menu.handle_event(event)
                    if button == "ПРОДОЛЖИТЬ":
                        self.paused = False
                    elif button == cfg.SETTINGS_BUTTON:
                        self.pause_menu.state_change(cfg.SETTINGS_BUTTON)
                    elif button == cfg.VOLUME_BUTTON:
                        self.audio_manager.set_bgm_volume(self.pause_menu.volume / 100)
                    elif button == cfg.BACK_BUTTON:
                        self.pause_menu.state_change(cfg.BACK_BUTTON)
                    elif button == cfg.EXIT_BUTTON:
                        pygame.quit()
                        return
                continue

            # === ИГРА АКТИВНА ===
            self.handler.game_process_events(self, self.transition_manager, cam_x, cam_y, events)
            self._update(dt)
            self._draw(cam_x, cam_y)


            # Обновляем экран ТОЛЬКО ОДИН РАЗ для обычной игры
            pygame.display.flip()


    def run_menu(self):
        self.audio_manager.play_bgm(cfg.MENU_MUSIC)

        while self.running:
            events = pygame.event.get()
            button_clicked = self.handler.menu_process_events(self, events)

            if button_clicked == cfg.START_GAME_BUTTON:
                self.run_intro()
                return
            elif button_clicked == cfg.SETTINGS_BUTTON:
                self.menu.state_change(cfg.SETTINGS_BUTTON)
            elif button_clicked == cfg.EXIT_BUTTON:
                pygame.quit()
                return
            elif button_clicked == cfg.VOLUME_BUTTON:
                self.audio_manager.set_bgm_volume(self.menu.volume / 100)
            elif button_clicked == cfg.BACK_BUTTON:
                self.menu.state_change(cfg.BACK_BUTTON)

            dt = min(0.05, self.clock.tick(cfg.FPS) / 1000.0)
            self.menu.draw(dt)
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

    def _new_game(self):
        self.world = World()
        self.dungeon_generator = BSP(self.world)
        self.dungeon_generator.generate_dungeon()

        player_x, player_y = self.dungeon_generator.get_start_coord()
        core_x, core_y = self.dungeon_generator.get_cyber_core_coord(player_x, player_y)

        self.cyber_core = CyberCore(core_x, core_y)
        self.player = Player(player_x, player_y)
        self.world.player = self.player
        self.world.start_room = self._find_room_by_point(player_x, player_y)

        self.terminal_intro = TerminalIntro(self.screen)
        self.world_renderer = WorldRenderer(self.screen, self.world, self.player, self.cyber_core)
        self.dark_renderer = DarkRenderer(self.screen, self.world, self.player, self.cyber_core)
        self.handler = Handler(self.player, self.cyber_core, self.world)
        self.camera = Camera(cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        self.transition_manager = TransitionManager(self.screen, self.camera)
        self.audio_manager = AudioManager()
        self.spawner = Spawner(self.world, self.dungeon_generator, self.player)

        self.spawner.spawn_initial()

        self.running = True
        self.paused = False

        self.pause_overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.pause_overlay.fill((0, 0, 0, 180))

        self.pause_menu = PauseMenu(self.screen)

    def _find_room_by_point(self, x: int, y: int):
        for room in self.world.rooms:
            if room.collidepoint(x, y):
                return room
        return self.world.rooms[0] if self.world.rooms else None

    def _death_player(self):
        self.world_renderer.draw_death_screen()
        self._new_game()

    def _update(self, dt: float):
        self.camera.update(dt)
        self.transition_manager.update(dt)
        self.player.update(dt, self.world)
        self.cyber_core.update(dt)

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

    def _draw(self, cam_x, cam_y):
        current_weapon = self.player.inventory.get_current()
        if hasattr(current_weapon, 'is_firing') and current_weapon.is_firing:
            self.camera.add_shake(3.0)

        self.world_renderer.draw_world(cam_x, cam_y)
        if self.world.mod == cfg.DARK_MOD:
            self.dark_renderer.draw(cam_x, cam_y)
        self.world_renderer.draw_interface()
        self.transition_manager.draw_flash()

        if self.paused:
            self.screen.blit(self.pause_overlay, (0, 0))