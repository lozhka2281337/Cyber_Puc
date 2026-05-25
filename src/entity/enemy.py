import pygame
from config import ENEMY_SIZE

class Enemy:
    def __init__(self, x: int, y: int, hp: int, speed: int, color: tuple):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)       
        self.hp = hp
        self.speed = speed
        self.color = color
        self.knockback = pygame.math.Vector2(0, 0)
        self.is_moving = False 

    def move(self, walls: list[pygame.Rect], dt: float, direction: pygame.math.Vector2) -> None:
        old_pos = pygame.math.Vector2(self.pos)
        
        velocity_x = direction.x * self.speed + self.knockback.x
        velocity_y = direction.y * self.speed + self.knockback.y

        self.pos.x += velocity_x * dt
        self.rect.x = round(self.pos.x)

        for wall in walls:
            if self.rect.colliderect(wall):
                if velocity_x > 0: self.rect.right = wall.left
                elif velocity_x < 0: self.rect.left = wall.right
                self.pos.x = float(self.rect.x)
                self.knockback.x = 0 

        self.pos.y += velocity_y * dt
        self.rect.y = round(self.pos.y)
        
        for wall in walls:
            if self.rect.colliderect(wall):
                if velocity_y > 0: self.rect.bottom = wall.top
                elif velocity_y < 0: self.rect.top = wall.bottom
                self.pos.y = float(self.rect.y)
                self.knockback.y = 0

        if self.knockback.magnitude() > 10:
            self.knockback = self.knockback.lerp(pygame.math.Vector2(0, 0), dt * 10)
        else:
            self.knockback.x, self.knockback.y = 0, 0
            
        self.is_moving = old_pos.distance_to(self.pos) > 0.01

    def get_damage(self, damage: int) -> None:
        self.hp -= damage

    def check_los(self, target_rect: pygame.Rect, walls: list[pygame.Rect]) -> bool: 
        line = (self.rect.center, target_rect.center)
        for wall in walls:
            if wall.clipline(line):
                return False
        return True 

    def update(self, dt: float, player, world) -> None:
        sees_player = self.check_los(player.rect, world.walls)
        direction = pygame.math.Vector2(0, 0)
        
        if sees_player: 
            direction = pygame.math.Vector2(player.rect.centerx - self.rect.centerx, 
                                            player.rect.centery - self.rect.centery)       
        if direction.magnitude() > 0:
            direction = direction.normalize()
            
        self.move(world.walls, dt, direction)

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.rect(surface, self.color, offset_rect)