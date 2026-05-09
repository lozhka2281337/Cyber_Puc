import pygame
from .enemy import Enemy
from .bullet import Bullet 

from config import (ENEMY_SWARM_HP, ENEMY_SWARM_SPEED, ENEMY_SWARM_COLOR, ENEMY_SWARM_ATTACK_RANGE,
                    ENEMY_TANK_HP, ENEMY_TANK_SPEED, ENEMY_TANK_COLOR, ENEMY_TANK_ATTACK_RANGE, ENEMY_TANK_DAMAGE,
                    ENEMY_SHOOTER_HP, ENEMY_SHOOTER_SPEED, ENEMY_SHOOTER_COLOR, ENEMY_SHOOTER_ATTACK_RANGE, ENEMY_SHOOTER_DAMAGE)

# 1. SWARM (Быстрый бегун, берет количеством)
class Swarm(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, ENEMY_SWARM_HP, ENEMY_SWARM_SPEED, ENEMY_SWARM_COLOR)
        self.attack_range = ENEMY_SWARM_ATTACK_RANGE
        self.damage = 1


# 2. TANK (Медленный, толстый, бьет больно)
class Tank(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, ENEMY_TANK_HP, ENEMY_TANK_SPEED, ENEMY_TANK_COLOR)
        self.attack_range = ENEMY_TANK_ATTACK_RANGE
        self.damage = ENEMY_TANK_DAMAGE


# 3. SHOOTER (Держит дистанцию, стреляет)
class Shooter(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, ENEMY_SHOOTER_HP, ENEMY_SHOOTER_SPEED, ENEMY_SHOOTER_COLOR)
        self.attack_range = ENEMY_SHOOTER_ATTACK_RANGE
        self.damage = ENEMY_SHOOTER_DAMAGE
        self.last_shot_time = 0
        self.shoot_cooldown = 1500 

    # Принимаем пули 
    def update(self, dt: float, player, world) -> None: 
        sees_player = self.check_los(player.rect, world.walls)
        direction = pygame.math.Vector2(0, 0)
        if sees_player: 
            vec_to_player = pygame.math.Vector2(player.rect.centerx - self.rect.centerx, 
                                                player.rect.centery - self.rect.centery)
            dist = vec_to_player.magnitude()
            # Отвечает за дистанцию
            if dist > self.attack_range + 50:
                direction = vec_to_player
            elif dist < self.attack_range - 50:
                direction = -vec_to_player
            else:
                direction = pygame.math.Vector2(0, 0) 
                current_time = pygame.time.get_ticks()
                
                # Что-то типо предохранителя
                if current_time - self.last_shot_time >= self.shoot_cooldown and world.bullets is not None:
                    self.last_shot_time = current_time
                    self._shoot(player, world.bullets)     

        if direction.magnitude() > 0:
            direction = direction.normalize()
        self.move(world.walls, dt, direction)
        
    def _shoot(self, player, bullets: list) -> None:
        new_bullet = Bullet(self.rect.centerx, self.rect.centery, 
                            player.rect.centerx, player.rect.centery, 
                            400, (255, 50, 50), self.damage)
        new_bullet.is_enemy_bullet = True 
        bullets.append(new_bullet)