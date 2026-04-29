import pygame
import math
import random

from config import BULLET_SIZE

class Bullet:
    def __init__(self, x, y, target_x, target_y, speed, color, damage, angle_offset=0, max_dist=None):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, BULLET_SIZE, BULLET_SIZE)
        
        self.speed = speed
        self.damage = damage
        self.color = color

        self.max_dist = max_dist
        self.start_pos = pygame.math.Vector2(x, y)
        self.is_alive = True

        self.direction = pygame.math.Vector2(target_x - x, target_y - y)
        self.correct_direction(angle_offset)

    def correct_direction(self, angle_offset):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
            
            if angle_offset != 0:
                self.direction = self.direction.rotate(angle_offset)
        else:
            self.direction = pygame.math.Vector2(1, 0)

    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.centerx = round(self.pos.x)
        self.rect.centery = round(self.pos.y)

        if self.max_dist:
            if self.pos.distance_to(self.start_pos) > self.max_dist:
                self.is_alive = False 

    def draw(self, surface, cam_x, cam_y):
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.ellipse(surface, self.color, offset_rect)

class Grenade(Bullet):
    def __init__(self, x, y, target_x, target_y, speed, color, blast_radius, fuse_time, max_range):
        super().__init__(x, y, target_x, target_y, speed, color, damage=0, max_dist=max_range)
        
        self.blast_radius = blast_radius
        self.fuse_time = fuse_time
        self.spawn_time = pygame.time.get_ticks()
        self.exploded = False
        self.is_moving = True

        target_pos = pygame.math.Vector2(target_x, target_y)
        dist_to_target = self.start_pos.distance_to(target_pos)
        self.target_dist = min(dist_to_target, max_range)

    def update(self, dt):
        if self.is_moving:
            if self.pos.distance_to(self.start_pos) < self.target_dist:
                self.pos += self.direction * self.speed * dt
                self.rect.centerx = round(self.pos.x)
                self.rect.centery = round(self.pos.y)
            else:
                self.is_moving = False 
                
        current_time = pygame.time.get_ticks()
        if current_time - self.spawn_time >= self.fuse_time:
            self.exploded = True

    def draw(self, surface, cam_x, cam_y):
        offset_rect = self.rect.move(-cam_x, -cam_y)
        grenade_center = offset_rect.center
        
        time_alive = pygame.time.get_ticks() - self.spawn_time
        blink_rate = max(50, 200 - (time_alive // 4)) 

        is_bright_phase = (time_alive // blink_rate) % 2 == 0

        surf_size = (self.blast_radius * 2) + 10
        temp_surface = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        temp_center = surf_size // 2
        if is_bright_phase:
            outline_color = (255, 50, 50, 255) 
            fill_color = (255, 50, 50, 70)    
            grenade_body_color = (255, 50, 50)
        else:
            outline_color = (150, 50, 50, 255) 
            fill_color = (150, 50, 50, 30)   
            grenade_body_color = self.color    


        pygame.draw.circle(temp_surface, fill_color, (temp_center, temp_center), self.blast_radius)
        pygame.draw.circle(temp_surface, outline_color, (temp_center, temp_center), self.blast_radius, 2) 

        blit_pos = (grenade_center[0] - temp_center, grenade_center[1] - temp_center)
        surface.blit(temp_surface, blit_pos)
        
        pygame.draw.ellipse(surface, grenade_body_color, offset_rect)

# НОВЫЙ КЛАСС: Эффект Искр для оружия
class SparkEffect:
    def __init__(self, x, y, color):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, 1, 1) 
        self.color = color
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 150
        self.is_alive = True
        
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

    def update(self, dt):
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.is_alive = False
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