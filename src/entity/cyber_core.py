import pygame
import math
import random

import config as cfg

# красивые частицы для ядра 
class Particle:
    def __init__(self, x, y, dx, dy, live_time):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.live_time = live_time

    def update(self) -> bool:
        self.x += self.dx
        self.y += self.dy
        self.live_time -= 1
        
        return self.live_time > 0

    def draw(self, surface, cam_x, cam_y):
        # Рассчитываем прозрачность (255 - полная прозрачность)
        alpha = max(0, min(255, int((self.live_time / 20) * 255)))
        
        p_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
        p_surf.fill((0, 230, 255, alpha))

        render_x = int(self.x) - cam_x
        render_y = int(self.y) - cam_y

        surface.blit(p_surf, (render_x, render_y))

# ядро (цель игрока)
class CyberCore:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.animation_timer = 0.0
        self.particles = []  

    def update(self):
        self.animation_timer = (self.animation_timer + 0.07) % (2 * math.pi)
        
        self._spawn_particles()
        self._update_particles()

    def draw(self, surface, cam_x, cam_y):
        self._draw_particles(surface, cam_x, cam_y)

        pulse = math.sin(self.animation_timer) * 6
        
        self._draw_pulsating_frame(surface, cam_x, cam_y, pulse)
        self._draw_core_center(surface, cam_x, cam_y, pulse)
        self._draw_orbital_dot(surface, cam_x, cam_y)

    def core_activate(self, world, player):
        if self.can_interact(player):
            world.mod = cfg.NORMAL_MOD
            

    def can_interact(self, player) -> bool:
        # Раздуваем хитбокс ядра на 40 пикселей для зоны взаимодействия
        interaction_zone = self.rect.inflate(40, 40)
        return interaction_zone.colliderect(player)

    def _spawn_particles(self):
        if random.random() < 0.2:
            px = self.rect.centerx + random.randint(-10, 10)
            py = self.rect.centery + random.randint(-10, 10)

            self.particles.append(Particle(px, py, random.uniform(-0.5, 0.5), random.uniform(-1.0, -2.0), 60))

    def _update_particles(self):
        for p in self.particles[:]:
            if not p.update():
                self.particles.remove(p)

    def _draw_particles(self, surface, cam_x, cam_y):
        for p in self.particles:
            p.draw(surface, cam_x, cam_y)

    def _draw_pulsating_frame(self, surface, cam_x, cam_y, pulse):
        view_rect = self.rect.move(-cam_x, -cam_y)

        glow_rect = view_rect.inflate(12 + pulse, 12 + pulse)
        pygame.draw.rect(surface, (0, 100, 160), glow_rect, 1)        

    def _draw_core_center(self, surface, cam_x, cam_y, pulse):
        view_rect = self.rect.move(-cam_x, -cam_y)

        inner_rect = view_rect.inflate(-pulse // 2, -pulse // 2)
        pygame.draw.rect(surface, (0, 67, 74), inner_rect)
        pygame.draw.rect(surface, (255, 255, 255), inner_rect, 2) # Белый контур

    def _draw_orbital_dot(self, surface, cam_x, cam_y):
        angle = self.animation_timer * 2
        r_x = int(self.rect.centerx + math.cos(angle) * 25) - cam_x
        r_y = int(self.rect.centery + math.sin(angle) * 10) - cam_y
        pygame.draw.circle(surface, (110, 219, 154), (r_x, r_y), 3)