import pygame
import random

from config import ENEMY_SIZE, ENEMY_SCOUT_COLOR, ENEMY_SCOUT_SPEED, ENEMY_SCOUT_HP

class Enemy:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        
        self.hp = ENEMY_SCOUT_HP
        self.speed = ENEMY_SCOUT_SPEED
        self.color = ENEMY_SCOUT_COLOR

        self.wander_dir = pygame.math.Vector2(0, 0) # вектор, по которому враг блуждает без дела
        self.timer = 0                              # таймер, который говорит, когда нужно менять направление для блуждания
 
    def move(self, walls: list, sees_player: bool, dt: int, direction: pygame.math.Vector2):
        self.pos.x += direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)

        # не даем врагу двигаться через стены по x
        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.x > 0: self.rect.right = wall.left
                elif direction.x < 0: self.rect.left = wall.right
                self.pos.x = self.rect.x
                if not sees_player: self.timer = 0 

        self.pos.y += direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)
        
        # не даем врагу двигаться через стены по y
        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.y > 0: self.rect.bottom = wall.top
                elif direction.y < 0: self.rect.top = wall.bottom
                self.pos.y = self.rect.y
                if not sees_player: self.timer = 0

    def get_damage(self, damage):
        self.hp -= damage

    def check_los(self, target_rect, walls): 
        # функция проверяет - есть ли между врагом и игроком стена

        line = (self.rect.center, target_rect.center)
        for wall in walls:
            if wall.clipline(line):
                return False
        return True 

    def update(self, dt, player, walls): 
        sees_player = self.check_los(player.rect, walls)
        self.timer -= dt

        # проверяем, есть ли между цетром игрока и центром врага стена,
        # если есть - враг начинает двигаться в сторону игрока,
        # иначе меняется вектор для блуждания

        if sees_player: direction = pygame.math.Vector2(player.rect.centerx - self.rect.centerx, 
                                                        player.rect.centery - self.rect.centery)
        else:
            if self.timer <= 0:
                self.timer = random.uniform(1.0, 2.5) 
                self.wander_dir = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            
            direction = self.wander_dir

        # номализация
        if direction.magnitude() > 0:
            direction = direction.normalize()

        # двигаем врага
        self.move(walls, sees_player, dt, direction)
                
    def draw(self, surface, cam_x, cam_y):
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.rect(surface, self.color, offset_rect)