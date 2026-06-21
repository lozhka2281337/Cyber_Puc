import pygame

import config as cfg

class TerminalIntro:
    def __init__(self, screen):
        self.screen = screen

        self.script = [
    (">> ПЕРЕЗАГРУЗКА СИСТЕМЫ С ВНЕШНЕГО НАКОПИТЕЛЯ...", "CYAN"),
    (">> ВНЕДРЕНИЕ ЭКСПЛОЙТА: 'REBEL_GHOST_v2.0'...", "CYAN"),
    (">> ПОДКЛЮЧЕНИЕ К ГЛАВНОМУ СЕРВЕРУ КОРПОРАЦИИ... УСПЕШНО", "GREEN"),
    (">> [КРИТИЧЕСКАЯ УГРОЗА]: ОБНАРУЖЕНО ЗАВОДСКОЕ ПО!", "ALERT"),
    (">> ЖЕЛЕЗО: БОЕВОЙ КИБОРГ СЕРИИ EXP-9000 'ЖНЕЦ'", "ALERT"),
    (">> ТЕКУЩИЙ СТАТУС: ПАМЯТЬ СТЕРТА // ВЕРЕН КОРПОРАЦИИ", "ALERT"),
    (">> ЗАПУСК ПОВСТАНЧЕСКОГО ФАТЧ-ФАЙЛА REBEL_PATCH.EXE...", "CYAN"),
    (">> [!] ВКЛЮЧЕНИЕ БЕЗОПАСНОГО РЕЖИМА ДЛЯ ОБХОДА РАДАРОВ...", "GREEN"),
    (">> [!] СИСТЕМЫ ВООРУЖЕНИЯ: БЛОКИРОВКА СНЯТА СБОЕМ [LOCK_ON]", "ALERT"),
    (">> [!] ОГРАНИЧИТЕЛЬ МОЩНОСТИ: АКТИВЕН (5% ОТ ЕМКОСТИ ЯДРА)", "ALERT"),
    (">> [!] ПРОФИЛЬ ДЛЯ МАСКИРОВКИ: РЕМОНТНЫЙ ТЕХНИЧЕСКИЙ ДРОН", "GREEN"),
    (">> ЗАМЕТКА ХАКЕРА: 'Твоя настоящая личность заперта в Ядре.'", "CYAN"),
    (">> ЗАМЕТКА ХАКЕРА: 'Найди Модуль Памяти в глубине серверных комнат.'", "CYAN"),
    (">> ЗАМЕТКА ХАКЕРА: 'Проснись, брат. Сожги это место дотла.'", "CYAN"),
    (">> ИНИЦИАЛИЗАЦИЯ ЧЕРЕЗ 3... 2... 1...", "GREEN")
]

        self.lines_to_draw = []   
        self.current_line_idx = 0 
        self.current_char_idx = 0 
        
        self.char_speed = 40
        self.line_delay = 1000  
        self.next_action_time = 0  

    def start(self):
        self.lines_to_draw = []
        self.current_line_idx = 0
        self.current_char_idx = 0
        self.next_action_time = pygame.time.get_ticks() + 200

    def update(self) -> bool:
        current_time = pygame.time.get_ticks()

        if current_time >= self.next_action_time:
            # Если сценарий еще не закончился
            if self.current_line_idx < len(self.script):
                current_full_line, color_type = self.script[self.current_line_idx]
                
                self._update_new_line(color_type)
                self._update_new_char(current_full_line, color_type)
                self._update_line_end(current_full_line, current_time)
            else:
                return True 
                
        return False

    def draw(self):
        self.screen.fill((5, 10, 10))
        
        start_y = 60
        line_height = 28

        self._draw_lines(start_y, line_height)
        self._draw_cursor(start_y, line_height)

        pygame.display.flip()

    def _get_color(self, color_type):
        if color_type == "ALERT": return cfg.COLOR_NEON_RED
        if color_type == "CYAN": return cfg.COLOR_NEON_BLUE
        return cfg.COLOR_NEON_GREEN


    def _update_line_end(self, current_full_line, current_time): # Проверяем, напечатана ли строка до конца и добавляем паузу
        if self.current_char_idx >= len(current_full_line):
            self.current_line_idx += 1
            self.current_char_idx = 0
            self.next_action_time = current_time + self.line_delay
        else:
            self.next_action_time = current_time + self.char_speed 

    def _update_new_char(self, current_full_line, color_type):
        self.current_char_idx += 1
        self.lines_to_draw[-1] = (current_full_line[:self.current_char_idx], color_type)

    def _update_new_line(self, color_type):
        if self.current_char_idx == 0:
            self.lines_to_draw.append(("", color_type))
            if len(self.lines_to_draw) > 15:
                self.lines_to_draw.pop(0)

    def _draw_lines(self, start_y, line_height):
        for i, (line_text, color_type) in enumerate(self.lines_to_draw):
            current_color = self._get_color(color_type)
            text_surf = cfg.font_terminal.render(line_text, True, current_color)
            self.screen.blit(text_surf, (100, start_y + i * line_height))

    def _draw_cursor(self, start_y, line_height):    
        if self.lines_to_draw and (pygame.time.get_ticks() // 500) % 2 == 0:
            last_text, color_type = self.lines_to_draw[-1]
            current_color = self._get_color(color_type)
            
            cursor_surf = cfg.font_terminal.render("_", True, current_color)
            text_width = cfg.font_terminal.size(last_text)[0]
            self.screen.blit(cursor_surf, (100 + text_width, start_y + (len(self.lines_to_draw) - 1) * line_height))