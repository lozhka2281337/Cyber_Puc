import pygame
import math
import config as cfg

class Elevator:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, cfg.TILE_SIZE * 2, cfg.TILE_SIZE * 2)
        
        self.is_active = False
        
        self.animation_timer = 0.0

    def activate(self):
        self.is_active = True

    def check_trigger(self, player) -> bool:
        if self.is_active and self.rect.colliderect(player.rect):
            return True
        return False

    def update(self):
        self.animation_timer = (self.animation_timer + 0.05) % (2 * math.pi)

    def draw(self, surface, cam_x, cam_y):
        view_rect = self.rect.move(-cam_x, -cam_y)
        pulse = math.sin(self.animation_timer) * 12

        if not self.is_active:
            pygame.draw.rect(surface, (25, 30, 40), view_rect)
            pygame.draw.rect(surface, (100, 110, 120), view_rect, 2)
        else:
            pygame.draw.rect(surface, (10, 25, 20), view_rect)
            glow_rect = view_rect.inflate(18 + pulse, 18 + pulse)
            pygame.draw.rect(surface, (0, 255, 120), glow_rect, 1)
            pygame.draw.rect(surface, (0, 255, 120), view_rect, 3)
