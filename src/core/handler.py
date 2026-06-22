import pygame

import config as cfg

class Handler:
    def __init__(self, player, cyber_core, world):
        self.player = player
        self.cyber_core = cyber_core
        self.world = world

    def intro_process_events(self, game, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.running = False

    def game_process_events(self, game, transition_manager, camera_x: float, camera_y: float, events):
        for event in events:
            if event.type == pygame.QUIT:
                game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.paused = not game.paused
                if event.key == pygame.K_q:
                    self.player.ping(self.world)

                #быстрый доступ оружия
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
                    self.player.shot(camera_x, camera_y, self.world)

            if self.world.mod == cfg.DARK_MOD:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        was_dark = self.world.mod == cfg.DARK_MOD
                        if self.cyber_core.core_activate(self.world, self.player):
                            game.set_normal_mod()

                        if was_dark and self.world.core_activated and not self.world.boss_spawned:
                            game.spawn_boss_in_start_room()
                            transition_manager.trigger_transition()

    def menu_process_events(self, game, events) -> str | None:
        for event in events:
            if event.type == pygame.QUIT:
                game.running = False

            if event.type == pygame.MOUSEMOTION:
                game.menu.update_selection_by_mouse()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                    game.menu.update_selection_by_keyboard(event)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return game.menu.handle_space()
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_d, pygame.K_a):
                    return game.menu.update_volume(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
               return game.menu.handle_left_mouse_button()

        return None