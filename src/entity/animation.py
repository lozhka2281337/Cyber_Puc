import pygame

class Animation:
    def __init__(self, path: str, columns: int, speed: float, scale: float = 1.0):
        # Загружаем картинку
        sheet = pygame.image.load(path).convert_alpha()
        
        # Вычисляем размер одного кадра
        width = sheet.get_width() // columns
        height = sheet.get_height()
        
        # Автоматическая нарезка
        self.frames = []
        for i in range(columns):
            rect = pygame.Rect(i * width, 0, width, height)
            frame = sheet.subsurface(rect)
            
            # Увеличиваем пиксель, если нужно
            if scale != 1.0:
                frame = pygame.transform.scale(frame, (int(width * scale), int(height * scale)))
                
            self.frames.append(frame)
            
        self.speed = speed
        self.timer = 0.0
        self.current_idx = 0

    def update(self, dt: float) -> None:
        """Двигает анимацию вперед на основе времени dt"""
        self.timer += dt
        if self.timer >= self.speed:
            self.timer = 0.0
            self.current_idx = (self.current_idx + 1) % len(self.frames)

    def get_frame(self, flip_x: bool = False) -> pygame.Surface:
        """Отдает готовую картинку. тут flip_x отражает её по горизонтали."""
        frame = self.frames[self.current_idx]
        if flip_x:
            # Отражаем по X (True) и не отражаем по Y (False)
            return pygame.transform.flip(frame, True, False)
        return frame
