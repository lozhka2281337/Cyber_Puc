import pygame

import config as cfg

class Handler:
    def __init__(self, player, cyber_core, world):
        self.player = player
        self.cyber_core = cyber_core
        self.world = world

    def game_process_events(self, game, camera_x: float, camera_y: float):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.running = False
                if event.key == pygame.K_q:
                    self.player.ping(self.world)

            if event.type == pygame.MOUSEBUTTONDOWN:
                # обработка колесика мышки (переключает оружие)
                if event.button == 4:
                    self.player.switch_weapon(forward=False)
                if event.button == 5:
                    self.player.switch_weapon(forward=True)
                if event.button == 1: 
                    self.player.shot(camera_x, camera_y, game.world)        
            
            if self.world.mod == cfg.DARK_MOD:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        self.cyber_core.core_activate(self.world, self.player)

    def menu_process_events(self, game) -> str | None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False

            # Наведение мыши автоматически меняет выбранный пункт
            if event.type == pygame.MOUSEMOTION:
                game.menu.update_selection_by_mouse()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                    game.menu.update_selection_by_keyboard(event)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return game.menu.handle_space()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
               return game.menu.handle_left_mouse_button()
        
        return None


