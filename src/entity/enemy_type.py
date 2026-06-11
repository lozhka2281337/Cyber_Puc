import pygame
from core.animation import Animation
from .enemy import Enemy, AnimatedEnemy
from projectile.bullet import Bullet
from config import (ENEMY_SWARM_HP, ENEMY_SWARM_SPEED, ENEMY_SWARM_COLOR, ENEMY_SWARM_ATTACK_RANGE,
                    ENEMY_TANK_HP, ENEMY_TANK_SPEED, ENEMY_TANK_COLOR, ENEMY_TANK_ATTACK_RANGE, ENEMY_TANK_DAMAGE,
                    ENEMY_SHOOTER_HP, ENEMY_SHOOTER_SPEED, ENEMY_SHOOTER_COLOR, ENEMY_SHOOTER_ATTACK_RANGE, ENEMY_SHOOTER_DAMAGE)

# 1. SWARM (Быстрый бегун, берет количеством)
class Swarm(AnimatedEnemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, ENEMY_SWARM_HP, ENEMY_SWARM_SPEED, ENEMY_SWARM_COLOR)
        self.attack_range = ENEMY_SWARM_ATTACK_RANGE
        self.damage = 1
        self.anim_left = Animation("assets/fast-enemy-run-left.png", columns=5, speed=0.1, scale=1.5)
        self.anim_right = Animation("assets/fast-enemy-run-right.png", columns=5, speed=0.1, scale=1.5)
        self.current_anim = self.anim_right

# 2. TANK (Медленный, толстый, бьет больно)
class Tank(AnimatedEnemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, ENEMY_TANK_HP, ENEMY_TANK_SPEED, ENEMY_TANK_COLOR)
        self.attack_range = ENEMY_TANK_ATTACK_RANGE
        self.damage = ENEMY_TANK_DAMAGE
        self.anim_left = Animation("assets/tank-sprite-left.png", columns=4, speed=0.25, scale=2.5)
        self.anim_right = Animation("assets/tank-sprite-right.png", columns=4, speed=0.25, scale=2.5)
        self.current_anim = self.anim_right

# 3. SHOOTER (Держит дистанцию, стреляет)
class Shooter(AnimatedEnemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, ENEMY_SHOOTER_HP, ENEMY_SHOOTER_SPEED, ENEMY_SHOOTER_COLOR)
        self.attack_range = ENEMY_SHOOTER_ATTACK_RANGE
        self.damage = ENEMY_SHOOTER_DAMAGE
        self.last_shot_time = 0
        self.shoot_cooldown = 1500
        self.anim_left = Animation("assets/shooter-left-run-Sheet.png", columns=6, speed=0.25, scale=1.5)
        self.anim_right = Animation("assets/shooter-right-run-Sheet.png", columns=6, speed=0.25, scale=1.5)
        self.current_anim = self.anim_right

    def _handle_chase(self, player, world, dt: float) -> pygame.math.Vector2:

        if self.check_los(player.rect, world.walls):
            vec_to_player = pygame.math.Vector2(player.rect.centerx - self.rect.centerx,

                                                player.rect.centery - self.rect.centery)
            dist = vec_to_player.magnitude()
            direction = pygame.math.Vector2(0, 0)

            if dist > self.attack_range + 50:
                direction = vec_to_player
            elif dist < self.attack_range - 50:
                direction = -vec_to_player

            if self.visible_timer > 0:
                self.visible_timer -= dt

            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot_time >= self.shoot_cooldown and world.bullets is not None:
                self.last_shot_time = current_time
                self._shoot(player, world.bullets)

            return direction

        elif self.last_known_pos:
            vec_to_lkp = self.last_known_pos - self.pos
            if vec_to_lkp.magnitude() < 50:
                self.last_known_pos = None 
                return pygame.math.Vector2(0, 0)
            return vec_to_lkp

        return pygame.math.Vector2(0, 0)


    def _shoot(self, player, bullets: list) -> None:
        new_bullet = Bullet(self.rect.centerx, self.rect.centery,
                            player.rect.centerx, player.rect.centery,
                            400, (255, 50, 50), self.damage)
        bullets.append(new_bullet)