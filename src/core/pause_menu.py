import pygame
import config as cfg
from core.menu import MainMenu, MenuStates


class PauseMenu(MainMenu):
    def __init__(self, screen):
        super().__init__(screen)

        self.title_text = "ПАУЗА"

        self.menu_options = [cfg.CONTINUE_BUTTON, cfg.SETTINGS_BUTTON, cfg.EXIT_BUTTON]

        self._create_buttons()
        self.selected_index = 0


    def handle_space(self) -> str:
        if self.state == MenuStates.MAIN:
            if self.selected_index == 0:
                return cfg.CONTINUE_BUTTON

            elif self.selected_index == 1:
                return cfg.SETTINGS_BUTTON

            elif self.selected_index == 2:
                return cfg.EXIT_BUTTON

        elif self.state == MenuStates.SETTINGS:
            if self.selected_index == 0:
                return cfg.VOLUME_BUTTON

            elif self.selected_index == 1:
                return cfg.BACK_BUTTON

        return cfg.DEFAULT_MENU_BUTTON
