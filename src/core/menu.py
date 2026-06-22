import pygame
import random
import enum

import config as cfg


class MenuStates(enum.Enum):
    MAIN = enum.auto()
    SETTINGS = enum.auto()


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        self.state = MenuStates.MAIN
        self.title_text = cfg.GAME_TITLE

        self.menu_options = [cfg.START_GAME_BUTTON, cfg.SETTINGS_BUTTON, cfg.EXIT_BUTTON]
        self.settings_options = [cfg.VOLUME_BUTTON, cfg.BACK_BUTTON]
        self.current_message = ""

        self.button_rects = []
        self._create_buttons()

        self.scanline_y = 0
        self.selected_index = 0
        self.volume = 100

    def draw(self, dt):
        self.screen.fill(cfg.COLOR_BG)
        self._draw_grid()
        self._draw_scannig_line(dt)
        self._draw_title()
        self._draw_buttons()

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.update_selection_by_mouse()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.handle_left_mouse_button()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                self.update_selection_by_keyboard(event)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.handle_space()
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_d, pygame.K_a):
                return self.update_volume(event)
        return None

    def handle_space(self) -> str:
        if self.state == MenuStates.MAIN:
            if self.selected_index == 0:
                return cfg.START_GAME_BUTTON
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

    def handle_left_mouse_button(self) -> str:
        mouse_pos = pygame.mouse.get_pos()
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_index = i
                return self.handle_space()
        return cfg.DEFAULT_MENU_BUTTON

    def update_selection_by_mouse(self):
        mouse_pos = pygame.mouse.get_pos()
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_index = i

    def update_selection_by_keyboard(self, event):
        options = self._get_options()
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected_index -= 1
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected_index += 1
        self.selected_index = self.selected_index % len(options)

    def update_volume(self, event) -> str:
        if self.state == MenuStates.SETTINGS:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.volume = max(0, self.volume - 10)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.volume = min(100, self.volume + 10)
        return cfg.VOLUME_BUTTON

    def state_change(self, button):
        if button == cfg.BACK_BUTTON:
            self.state = MenuStates.MAIN
        elif button == cfg.SETTINGS_BUTTON:
            self.state = MenuStates.SETTINGS
        self._create_buttons()
        self.selected_index = 0

    def _get_volume_button(self):
        return f"{cfg.VOLUME_BUTTON} {self.volume}%"

    def _create_buttons(self):
        options = self._get_options()
        self.button_rects = []
        for i in range(len(options)):
            btn_w, btn_h = 340, 50
            rect = pygame.Rect(self.width // 2 - btn_w // 2, self.height // 2 - self.height * 0.2 + i * 70, btn_w,
                               btn_h)
            self.button_rects.append(rect)

    def _draw_grid(self):
        for x in range(0, self.width, 40):
            pygame.draw.line(self.screen, (15, 22, 33), (x, 0), (x, self.height), 1)
        for y in range(0, self.height, 40):
            pygame.draw.line(self.screen, (15, 22, 33), (0, y), (self.width, y), 1)

    def _draw_scannig_line(self, dt):
        self.scanline_y = (self.scanline_y + 250 * dt) % self.height
        pygame.draw.line(self.screen, (18, 32, 50), (0, self.scanline_y), (self.width, self.scanline_y), 1)

    def _draw_title(self):
        off_x, off_y = 0, 0
        if random.random() < 0.05:
            off_x = random.randint(-3, 3)
            off_y = random.randint(-1, 1)
            glitch_surf = cfg.title_font.render(self.title_text, True, cfg.COLOR_NEON_RED)
            self.screen.blit(glitch_surf,
                             glitch_surf.get_rect(center=(self.width // 2 + off_x * 2, self.height // 5 + off_y)))

        title_surf = cfg.title_font.render(self.title_text, True, cfg.COLOR_NEON_BLUE)
        self.screen.blit(title_surf, title_surf.get_rect(center=(self.width // 2 + off_x, self.height // 5 + off_y)))
        pygame.draw.line(self.screen, cfg.COLOR_NEON_BLUE, (self.width // 4, self.height // 5 + 40),
                         (3 * self.width // 4, self.height // 5 + 40), 2)

        footer_surf = cfg.info_font.render("Made by team Бурмалда", True, (80, 100, 120))
        self.screen.blit(footer_surf, footer_surf.get_rect(center=(self.width // 2, self.height - self.height * 0.1)))

    def _get_options(self):
        if self.state == MenuStates.MAIN:
            return self.menu_options
        elif self.state == MenuStates.SETTINGS:
            return self.settings_options

    def _draw_buttons(self):
        options = self._get_options()
        for i, opt in enumerate(options):
            is_selected = (i == self.selected_index)
            rect = self.button_rects[i]

            if (opt == cfg.VOLUME_BUTTON):
                opt = self._get_volume_button()

            border_color = (25, 35, 45)
            text_color = cfg.COLOR_TEXT_MUTED
            if is_selected:
                border_color = cfg.COLOR_NEON_GREEN
                text_color = cfg.COLOR_NEON_GREEN

            pygame.draw.rect(self.screen, (13, 18, 26), rect)
            pygame.draw.rect(self.screen, border_color, rect, 2)

            if is_selected:
                pygame.draw.rect(self.screen, cfg.WHITE, (rect.x - 3, rect.y - 3, 8, 3))
                pygame.draw.rect(self.screen, cfg.WHITE, (rect.x - 3, rect.y - 3, 3, 8))
                display_text = f"> {opt} <"
            else:
                display_text = opt

            text_surf = cfg.menu_font.render(display_text, True, text_color)
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))