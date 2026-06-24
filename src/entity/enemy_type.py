import pygame
from core.animation import Animation
from .enemy import Enemy, AnimatedEnemy
from projectile.bullet import Bullet
import config as cfg
from config import (ENEMY_SWARM_HP, ENEMY_SWARM_SPEED, ENEMY_SWARM_COLOR, ENEMY_SWARM_ATTACK_RANGE,
                    ENEMY_TANK_HP, ENEMY_TANK_SPEED, ENEMY_TANK_COLOR, ENEMY_TANK_ATTACK_RANGE, ENEMY_TANK_DAMAGE,
                    ENEMY_SHOOTER_HP, ENEMY_SHOOTER_SPEED, ENEMY_SHOOTER_COLOR, ENEMY_SHOOTER_ATTACK_RANGE, ENEMY_SHOOTER_DAMAGE,
                    SHOOTER_ADVANCE_DISTANCE, SHOOTER_RETREAT_DISTANCE, SHOOTER_BULLET_SPEED, SHOOTER_BULLET_COLOR, SHOOTER_SHOOT_COOLDOWN)


# 1. SWARM (Быстрый бегун, берет количеством)
class Swarm(AnimatedEnemy):
    def __init__(self, x: int, y: int, room: pygame.Rect):
        super().__init__(x, y, ENEMY_SWARM_HP, ENEMY_SWARM_SPEED, ENEMY_SWARM_COLOR, room)
        self.attack_range = ENEMY_SWARM_ATTACK_RANGE
        self.damage = 1
        self.base_damage = self.damage
        self.anim_left = Animation("assets/fast-enemy-run-left.png", columns=5, speed=0.1, scale=1.5)
        self.anim_right = Animation("assets/fast-enemy-run-right.png", columns=5, speed=0.1, scale=1.5)
        self.current_anim = self.anim_right


# 2. TANK (Медленный, толстый, бьет больно)
class Tank(AnimatedEnemy):
    def __init__(self, x: int, y: int, room: pygame.Rect):
        super().__init__(x, y, ENEMY_TANK_HP, ENEMY_TANK_SPEED, ENEMY_TANK_COLOR, room)
        self.attack_range = ENEMY_TANK_ATTACK_RANGE
        self.damage = ENEMY_TANK_DAMAGE
        self.base_damage = self.damage
        self.anim_left = Animation("assets/tank-sprite-left.png", columns=4, speed=0.25, scale=2.5)
        self.anim_right = Animation("assets/tank-sprite-right.png", columns=4, speed=0.25, scale=2.5)
        self.current_anim = self.anim_right


# 3. SHOOTER (Держит дистанцию, стреляет)
class Shooter(AnimatedEnemy):
    def __init__(self, x: int, y: int, room: pygame.Rect):
        super().__init__(x, y, ENEMY_SHOOTER_HP, ENEMY_SHOOTER_SPEED, ENEMY_SHOOTER_COLOR, room)
        self.attack_range = ENEMY_SHOOTER_ATTACK_RANGE
        self.damage = ENEMY_SHOOTER_DAMAGE
        self.base_damage = self.damage
        self.last_shot_time = 0
        self.shoot_cooldown = SHOOTER_SHOOT_COOLDOWN
        self.anim_left = Animation("assets/shooter-left-run-Sheet.png", columns=6, speed=0.25, scale=1.5)
        self.anim_right = Animation("assets/shooter-right-run-Sheet.png", columns=6, speed=0.25, scale=1.5)
        self.current_anim = self.anim_right

    def _handle_chase(self, player, world, dt: float) -> pygame.math.Vector2:
        if self.check_los(player.rect, world.walls):
            self.path.clear() 
            
            vec_to_player = self._vector_to_player(player)
            dist = vec_to_player.magnitude()
            direction = pygame.math.Vector2(0, 0)

            if dist > self.attack_range + SHOOTER_ADVANCE_DISTANCE:
                direction = vec_to_player
            elif dist < self.attack_range - SHOOTER_RETREAT_DISTANCE:
                direction = -vec_to_player

            self._attempt_shoot(player, world)
            return direction
        else:
            return super()._handle_chase(player, world, dt)

    def _attempt_shoot(self, player, world) -> None:
        current_time = pygame.time.get_ticks()
        cooldown = self.shoot_cooldown
        if world.mod == cfg.DARK_MOD and not world.core_activated:
            cooldown = int(cooldown * cfg.ENEMY_STEALTH_SHOOT_COOLDOWN_MULTIPLIER)

        if current_time - self.last_shot_time >= cooldown and world.bullets is not None:
            self.last_shot_time = current_time
            self._fire_bullet(player, world.bullets)

    def _fire_bullet(self, player, bullets: list) -> None:
        start = self._center_vector()
        target = self._vector_to_player(player)

        new_bullet = Bullet(start.x, start.y,
                            start.x + target.x, start.y + target.y,
                            SHOOTER_BULLET_SPEED, SHOOTER_BULLET_COLOR, self.damage)
        bullets.append(new_bullet)