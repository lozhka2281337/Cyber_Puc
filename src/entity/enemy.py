import pygame
from config import ENEMY_SIZE

class Enemy:
    def __init__(self, x, y, hp, speed, color):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        
        self.hp = hp
        self.speed = speed
        self.color = color

    def move(self, walls: list, dt: float, direction: pygame.math.Vector2):
        self.pos.x += direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)

        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.x > 0: self.rect.right = wall.left
                elif direction.x < 0: self.rect.left = wall.right
                self.pos.x = self.rect.x

        self.pos.y += direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)
        
        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.y > 0: self.rect.bottom = wall.top
                elif direction.y < 0: self.rect.top = wall.bottom
                self.pos.y = self.rect.y

    def get_damage(self, damage):
        self.hp -= damage

    def check_los(self, target_rect, walls): 
        line = (self.rect.center, target_rect.center)
        for wall in walls:
            if wall.clipline(line):
                return False
        return True 

    def draw(self, surface, cam_x, cam_y):
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.rect(surface, self.color, offset_rect)