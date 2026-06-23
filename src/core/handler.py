import pygame

import config as cfg

class Handler:
    def __init__(self, game, player, cyber_core, world):
        self.game = game
        self.player = player
        self.cyber_core = cyber_core

    def intro_process_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.running = False

    def game_process_events(self, transition_manager, camera_x: float, camera_y: float):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if self.game.paused: self._process_pause_event(event)
            else: self._process_event(event, transition_manager, camera_x, camera_y)

    def menu_process_events(self, events) -> str | None:
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.MOUSEMOTION:
                self.game.menu.update_selection_by_mouse()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                    self.game.menu.update_selection_by_keyboard(event)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return self.game.menu.handle_space()
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_d, pygame.K_a):
                    return self.game.menu.update_volume(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
               return self.game.menu.handle_left_mouse_button()

        return None
    
    def _process_event(self, event, transition_manager, camera_x, camera_y):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.paused = not self.game.paused
            if event.key == pygame.K_q:
                self.player.ping(self.game.world)

            if event.key == pygame.K_1:
                self.player.inventory.set_weapon(0)
            if event.key == pygame.K_2:
                self.player.inventory.set_weapon(1)
            if event.key == pygame.K_3:
                self.player.inventory.set_weapon(2)
            if event.key == pygame.K_4:
                self.player.inventory.set_weapon(3)
            if event.key == pygame.K_5:
                self.player.inventory.set_weapon(4)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.player.switch_weapon(forward=False)
            if event.button == 5:
                self.player.switch_weapon(forward=True)
            if event.button == 1:
                self.player.shot(camera_x, camera_y, self.game.world)

        if self.game.world.mod == cfg.DARK_MOD:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    was_dark = self.game.world.mod == cfg.DARK_MOD
                    if self.cyber_core.core_activate(self.game.world, self.player):
                        self.game.set_normal_mod()

                    if was_dark and self.game.world.core_activated and not self.game.world.boss_spawned:
                        self.game.spawn_boss_in_start_room()
                        transition_manager.trigger_transition()

    def _process_pause_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.paused = False

        button = self.game.pause_menu.handle_event(event)
        if button == cfg.CONTINUE_BUTTON:
            self.game.paused = False
        elif button == cfg.SETTINGS_BUTTON:
            self.game.pause_menu.state_change(cfg.SETTINGS_BUTTON)
        elif button == cfg.VOLUME_BUTTON:
            self.game.audio_manager.set_bgm_volume(self.game.pause_menu.volume / 100)
        elif button == cfg.BACK_BUTTON:
            self.game.pause_menu.state_change(cfg.BACK_BUTTON)
        elif button == cfg.EXIT_BUTTON:
            self.game.running = False