import pygame
from config import ENEMY_SIZE

class Enemy:
    def __init__(self, x: int, y: int, hp: int, speed: int, color: tuple):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        
        self.hp = hp
        self.speed = speed
        self.color = color

    def move(self, walls: list[pygame.Rect], dt: float, direction: pygame.math.Vector2) -> None:
        self.pos.x += direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)

        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.x > 0: self.rect.right = wall.left
                elif direction.x < 0: self.rect.left = wall.right
                self.pos.x = float(self.rect.x)

        self.pos.y += direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)
        
        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.y > 0: self.rect.bottom = wall.top
                elif direction.y < 0: self.rect.top = wall.bottom
                self.pos.y = float(self.rect.y)

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