import pygame

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