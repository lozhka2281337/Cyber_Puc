import pygame

from menu.main_menu import MenuStates

import config as cfg

class Handler:
    def __init__(self, game, player, cyber_core):
        self.game = game
        self.player = player
        self.cyber_core = cyber_core

    def intro_process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                    self.game.running = False

    def game_process_events(self, camera_x: float, camera_y: float):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            self._process_event(event, camera_x, camera_y)

    def menu_process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
                return  
            
            button_clicked = self.game.menu.handle_event(event)

            if button_clicked and button_clicked != cfg.DEFAULT_MENU_BUTTON:
                self._process_button_action(button_clicked)

    def _process_button_action(self, button_clicked):
        if button_clicked == cfg.START_GAME_BUTTON:
            self.game.run_terminal(cfg.SCRIPT_INTRO)
            
        elif button_clicked == cfg.CONTINUE_BUTTON:
            self.game.paused = False
            
        elif button_clicked == cfg.SETTINGS_BUTTON:
            self.game.menu.state_change(cfg.SETTINGS_BUTTON)
            
        elif button_clicked == cfg.BACK_BUTTON:
            self.game.menu.state_change(cfg.BACK_BUTTON)
            
        elif button_clicked == cfg.EXIT_BUTTON:
            self.game.running = False
            
        elif button_clicked == cfg.VOLUME_BUTTON:
            self.game.audio_manager.set_bgm_volume(self.game.volume / 100)

    
    def _process_event(self, event, camera_x, camera_y):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.paused = not self.game.paused
                self.game.menu.set_state(MenuStates.PAUSE)
            if event.key == pygame.K_q:
                self.player.ping(self.game.world)

            if event.key == pygame.K_1:
                self.player.select_weapon(0)
            if event.key == pygame.K_2:
                self.player.select_weapon(1)
            if event.key == pygame.K_3:
                self.player.select_weapon(2)
            if event.key == pygame.K_4:
                self.player.select_weapon(3)
            if event.key == pygame.K_5:
                self.player.select_weapon(4)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.player.switch_weapon(forward=True)
            if event.button == 5:
                self.player.switch_weapon(forward=False)
            if event.button == 1:
                self.player.shot(camera_x, camera_y, self.game.world)

        if self.game.world.mod == cfg.DARK_MOD:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if self.cyber_core and self.cyber_core.core_activate(self.player):
                        self.game.set_normal_mod()
                        self.game.transition_manager.trigger_transition()
                        self.player.update_target(cfg.DESTROY_TARGET_MES)

