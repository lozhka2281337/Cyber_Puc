import pygame

from .effects import SparkEffect

from config import BULLET_SIZE

class Bullet:
    def __init__(self, x, y, target_x, target_y, speed, color, damage, angle_offset=0, max_dist=None, player_bullet=False):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, BULLET_SIZE, BULLET_SIZE)
        
        self.speed = speed
        self.damage = damage
        self.color = color

        self.max_dist = max_dist
        self.start_pos = pygame.math.Vector2(x, y)
        self.player_bullet = player_bullet

        self.direction = pygame.math.Vector2(target_x - x, target_y - y)
        self._correct_direction(angle_offset)

    def update(self, world, player, dt):
        self._movenment(world, dt)
        
        if self._check_wall_colide(world): return 

        if self.player_bullet: self._check_player_bullet_hit(world)
        else:                  self._check_enemy_bullet_hit(world, player)
            

    def draw(self, surface, cam_x, cam_y):
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.ellipse(surface, self.color, offset_rect)


    def _correct_direction(self, angle_offset):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
            
            if angle_offset != 0:
                self.direction = self.direction.rotate(angle_offset)
        else:
            self.direction = pygame.math.Vector2(1, 0)

    def _movenment(self, world, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.centerx = round(self.pos.x)
        self.rect.centery = round(self.pos.y)

        if self.max_dist:
            if self.pos.distance_to(self.start_pos) > self.max_dist:
                world.bullets.remove(self)
        

    def _check_wall_colide(self, world) -> bool:
        for wall in world.walls:
            if self.rect.colliderect(wall):
                self._bullet_death(world)
                
                return True
        
        return False

    def _check_player_bullet_hit(self, world):
        for enemy in world.enemies[:]: 
            if self.rect.colliderect(enemy.rect):
                self._bullet_death(world)
                
                enemy.get_damage(self.damage)              
                push_dir = pygame.math.Vector2(self.direction.x, self.direction.y)

                if push_dir.magnitude() > 0: enemy.knockback += push_dir.normalize() * 250              
                
                break

    def _check_enemy_bullet_hit(self, world, player):
        if self.rect.colliderect(player.rect):
                self.player.get_damage(self.damage)
                self._bullet_death(world)

    def _bullet_death(self, world):
        world.effects.append(SparkEffect(self.rect.centerx, self.rect.centery, self.color))
        world.bullets.remove(self)
