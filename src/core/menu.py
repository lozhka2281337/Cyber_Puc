import pygame
import random

import config as cfg


class MainMenu:
    def __init__(self, screen):
        self.screen = screen

        self.width = screen.get_width()
        self.height = screen.get_height()

        # шрифты
        self.title_font = pygame.font.SysFont("Courier New", 50, bold=True)
        self.menu_font = pygame.font.SysFont("Courier New", 24, bold=True)

        self.title_text = cfg.GAME_TITLE
        self.menu_options = [cfg.START_GAME_BUTTON, cfg.SETTINGS_BUTTON, cfg.EXIT_BUTTON]
        self.current_message = ""  

        self.button_rects = []
        self._create_buttons()

        self.scanline_y = 0
        self.selected_index = 0

    def draw(self, dt):
        self.screen.fill(cfg.COLOR_BG)

        self._draw_grid()
        self._draw_scannig_line(dt)
        self._draw_title()
        self._draw_buttons()

    def handle_space(self) -> str:
        if self.selected_index == 0:
            return cfg.START_GAME_BUTTON
        elif self.selected_index == 1:
            return cfg.SETTINGS_BUTTON
        elif self.selected_index == 2:
            pygame.quit()

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
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected_index -= 1
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected_index += 1

        self.selected_index = self.selected_index % len(self.menu_options)

    def _create_buttons(self):
        for i in range(len(self.menu_options)):
            btn_w, btn_h = 340, 50
            rect = pygame.Rect(self.width//2 - btn_w//2, self.height//2 - 30 + i * 70, btn_w, btn_h)
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

        if random.random() < 0.05:  # 5% шанс искажения каждый кадр
            off_x = random.randint(-3, 3)
            off_y = random.randint(-1, 1)

            glitch_surf = self.title_font.render(self.title_text, True, cfg.COLOR_NEON_RED)
            self.screen.blit(glitch_surf, glitch_surf.get_rect(center=(self.width//2 + off_x * 2, self.height//5 + off_y)))

        title_surf = self.title_font.render(self.title_text, True, cfg.COLOR_NEON_BLUE)
        self.screen.blit(title_surf, title_surf.get_rect(center=(self.width//2 + off_x, self.height//5 + off_y)))
        pygame.draw.line(self.screen, cfg.COLOR_NEON_BLUE, (self.width//4, self.height//5 + 40), (3 * self.width//4, self.height//5 + 40), 2)

    def _draw_buttons(self):
        for i, opt in enumerate(self.menu_options):
            is_selected = (i == self.selected_index)
            rect = self.button_rects[i]

            # Цвета активного/пассивного состояния
            border_color = (25, 35, 45) 
            text_color = cfg.COLOR_TEXT_MUTED
            if is_selected: 
                border_color = cfg.COLOR_NEON_GREEN 
                text_color = cfg.COLOR_NEON_GREEN

            # Фон кнопки и рамка
            pygame.draw.rect(self.screen, (13, 18, 26), rect)
            pygame.draw.rect(self.screen, border_color, rect, 2)

            # Рисуем хакерские«уголки для выделенной кнопки
            if is_selected:
                pygame.draw.rect(self.screen, cfg.WHITE, (rect.x - 3, rect.y - 3, 8, 3))
                pygame.draw.rect(self.screen, cfg.WHITE, (rect.x - 3, rect.y - 3, 3, 8))
                display_text = f"> {opt} <"
            else:
                display_text = opt

            text_surf = self.menu_font.render(display_text, True, text_color)
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))
