import pygame
import math
import random


class SparkEffect:
    def __init__(self, x, y, color):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, 1, 1) 
        self.color = color
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 150
        
        self.is_effect = True 
        
        self.sparks = []
        for _ in range(random.randint(4, 8)):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(150, 450)
            self.sparks.append({
                'pos': pygame.math.Vector2(x, y),
                'vel': pygame.math.Vector2(math.cos(angle) * speed, math.sin(angle) * speed),
                'radius': random.uniform(2, 5)
            })

    def update(self, effects, dt):
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            effects.remove(self)
            return
            
        for s in self.sparks:
            s['pos'] += s['vel'] * dt
            s['radius'] -= 15 * dt 

    def draw(self, surface, cam_x, cam_y):
        for s in self.sparks:
            if s['radius'] > 0:
                draw_pos = (int(s['pos'].x - cam_x), int(s['pos'].y - cam_y))
                pygame.draw.circle(surface, self.color, draw_pos, int(s['radius']))
                pygame.draw.circle(surface, (255, 255, 255), draw_pos, max(1, int(s['radius']) // 2))