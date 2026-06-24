import pygame

import config as cfg

class Handler:
    def __init__(self, game, player, cyber_core, world):
        self.game = game
        self.player = player
        self.cyber_core = cyber_core

    def intro_process_events(self, ):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.running = False
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if hasattr(self.game, "terminal") and self.game.terminal:
                        self.game.terminal.skip()

    def game_process_events(self, camera_x: float, camera_y: float):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if self.game.paused: self._process_pause_event(event)
            else: self._process_event(event, camera_x, camera_y)

    def menu_process_events(self, ):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.MOUSEMOTION:
                self.game.menu.update_selection_by_mouse()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                    self.game.menu.update_selection_by_keyboard(event)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._process_button_clicked()
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_d, pygame.K_a):
                    self.game.menu.update_volume(event)
                    self._process_button_clicked()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
               self._process_button_clicked()
    
    def _process_event(self, event, camera_x, camera_y):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.paused = not self.game.paused
            if event.key == pygame.K_q:
                self.player.ping(self.game.world)

            if event.key == pygame.K_1:
                self.player.select_weapon(0, self.game.world)
            if event.key == pygame.K_2:
                self.player.select_weapon(1, self.game.world)
            if event.key == pygame.K_3:
                self.player.select_weapon(2, self.game.world)
            if event.key == pygame.K_4:
                self.player.select_weapon(3, self.game.world)
            if event.key == pygame.K_5:
                self.player.select_weapon(4, self.game.world)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.player.switch_weapon(forward=False, world=self.game.world)
            if event.button == 5:
                self.player.switch_weapon(forward=True, world=self.game.world)
            if event.button == 1:
                self.player.shot(camera_x, camera_y, self.game.world)

        if self.game.world.mod == cfg.DARK_MOD:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if self.cyber_core and self.cyber_core.core_activate(self.player):
                        self.game.set_normal_mod()
                        self.game.transition_manager.trigger_transition()

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

    def _process_button_clicked(self):
        button_clicked = self.game.menu.handle_space()
        if button_clicked == cfg.START_GAME_BUTTON:
            self.game.run_terminal(cfg.SCRIPT_INTRO)
        elif button_clicked == cfg.SETTINGS_BUTTON:
            self.game.menu.state_change(cfg.SETTINGS_BUTTON)
        elif button_clicked == cfg.EXIT_BUTTON:
            self.game.running = False
        elif button_clicked == cfg.VOLUME_BUTTON:
            self.game.audio_manager.set_bgm_volume(self.game.menu.volume / 100)
        elif button_clicked == cfg.BACK_BUTTON:
            self.game.menu.state_change(cfg.BACK_BUTTON)