import random

class Camera:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.shake_intensity = 0.0

    def add_shake(self, amount: float):
        """Добавляет тряску экрана"""
        self.shake_intensity = max(self.shake_intensity, amount)

    def get_offset(self, target_rect, dt: float) -> tuple[int, int]:
        if self.shake_intensity > 0:
            self.shake_intensity -= 50 * dt
            if self.shake_intensity < 0: 
                self.shake_intensity = 0

        # Центрируем камеру на цели
        cam_x = target_rect.x + (target_rect.width / 2) - (self.width / 2)
        cam_y = target_rect.y + (target_rect.height / 2) - (self.height / 2) 

        # Применяем тряску
        if self.shake_intensity > 0:
            cam_x += random.uniform(-self.shake_intensity, self.shake_intensity)
            cam_y += random.uniform(-self.shake_intensity, self.shake_intensity)

        return int(cam_x), int(cam_y)
