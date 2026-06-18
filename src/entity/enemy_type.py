"""Specific enemy types with unique behaviors and stats."""

import pygame
from typing import Optional

from core.animation import Animation
from .enemy import Enemy, AnimatedEnemy
from projectile.bullet import Bullet
from config import (
    ENEMY_SWARM_HP,
    ENEMY_SWARM_SPEED,
    ENEMY_SWARM_COLOR,
    ENEMY_SWARM_ATTACK_RANGE,
    ENEMY_TANK_HP,
    ENEMY_TANK_SPEED,
    ENEMY_TANK_COLOR,
    ENEMY_TANK_ATTACK_RANGE,
    ENEMY_TANK_DAMAGE,
    ENEMY_SHOOTER_HP,
    ENEMY_SHOOTER_SPEED,
    ENEMY_SHOOTER_COLOR,
    ENEMY_SHOOTER_ATTACK_RANGE,
    ENEMY_SHOOTER_DAMAGE,
)

# Shooter behavior constants
SHOOTER_ADVANCE_DISTANCE = 50  # How close to chase before backing away
SHOOTER_RETREAT_DISTANCE = 50  # How far to back away if too close
SHOOTER_BULLET_SPEED = 400
SHOOTER_BULLET_COLOR = (255, 50, 50)
SHOOTER_SHOOT_COOLDOWN = 1500  # milliseconds


class Swarm(AnimatedEnemy):
    """Fast melee enemy that attacks in groups.
    
    Stats:
    - Fast movement
    - Low health
    - Low damage
    - Weak in 1v1, strong in groups
    """

    def __init__(self, x: int, y: int, room: pygame.Rect) -> None:
        """Initialize Swarm enemy.
        
        Args:
            x: Starting X position
            y: Starting Y position
            room: Patrol room
        """
        super().__init__(
            x, y,
            ENEMY_SWARM_HP,
            ENEMY_SWARM_SPEED,
            ENEMY_SWARM_COLOR,
            room
        )
        self.attack_range = ENEMY_SWARM_ATTACK_RANGE
        self.damage = 1

        # Load animations
        self.anim_left = Animation(
            "assets/fast-enemy-run-left.png",
            columns=5,
            speed=0.1,
            scale=1.5
        )
        self.anim_right = Animation(
            "assets/fast-enemy-run-right.png",
            columns=5,
            speed=0.1,
            scale=1.5
        )
        self.current_anim = self.anim_right


class Tank(AnimatedEnemy):
    """Slow heavy enemy that deals high damage.
    
    Stats:
    - Slow movement
    - Very high health
    - High damage
    - Tanky, high threat when encountered
    """

    def __init__(self, x: int, y: int, room: pygame.Rect) -> None:
        """Initialize Tank enemy.
        
        Args:
            x: Starting X position
            y: Starting Y position
            room: Patrol room
        """
        super().__init__(
            x, y,
            ENEMY_TANK_HP,
            ENEMY_TANK_SPEED,
            ENEMY_TANK_COLOR,
            room
        )
        self.attack_range = ENEMY_TANK_ATTACK_RANGE
        self.damage = ENEMY_TANK_DAMAGE

        # Load animations
        self.anim_left = Animation(
            "assets/tank-sprite-left.png",
            columns=4,
            speed=0.25,
            scale=2.5
        )
        self.anim_right = Animation(
            "assets/tank-sprite-right.png",
            columns=4,
            speed=0.25,
            scale=2.5
        )
        self.current_anim = self.anim_right


class Shooter(AnimatedEnemy):
    """Ranged enemy that maintains distance.
    
    Stats:
    - Moderate movement
    - Moderate health
    - Ranged attack
    - Keeps distance, dangerous at range
    """

    def __init__(self, x: int, y: int, room: pygame.Rect) -> None:
        """Initialize Shooter enemy.
        
        Args:
            x: Starting X position
            y: Starting Y position
            room: Patrol room
        """
        super().__init__(
            x, y,
            ENEMY_SHOOTER_HP,
            ENEMY_SHOOTER_SPEED,
            ENEMY_SHOOTER_COLOR,
            room
        )
        self.attack_range = ENEMY_SHOOTER_ATTACK_RANGE
        self.damage = ENEMY_SHOOTER_DAMAGE
        self.last_shot_time: int = 0
        self.shoot_cooldown: int = SHOOTER_SHOOT_COOLDOWN

        # Load animations
        self.anim_left = Animation(
            "assets/shooter-left-run-Sheet.png",
            columns=6,
            speed=0.25,
            scale=1.5
        )
        self.anim_right = Animation(
            "assets/shooter-right-run-Sheet.png",
            columns=6,
            speed=0.25,
            scale=1.5
        )
        self.current_anim = self.anim_right

    def _handle_chase(self, player, world, dt: float) -> pygame.math.Vector2:
        """Handle chase behavior with range management.
        
        Shooter maintains optimal distance:
        - Too far: advance toward player
        - In range: hold position and shoot
        - Too close: retreat from player
        
        Args:
            player: Player object
            world: World object
            dt: Delta time
            
        Returns:
            Movement direction vector
        """
        # Direct line of sight to player
        if self.check_los(player.rect, world.walls):
            self.path.clear()

            # Calculate distance and direction to player
            vec_to_player = pygame.math.Vector2(
                player.rect.centerx - self.rect.centerx,
                player.rect.centery - self.rect.centery
            )
            dist = vec_to_player.magnitude()
            direction = pygame.math.Vector2(0, 0)

            # Range management logic
            if dist > self.attack_range + SHOOTER_ADVANCE_DISTANCE:
                # Too far, advance
                direction = vec_to_player
            elif dist < self.attack_range - SHOOTER_RETREAT_DISTANCE:
                # Too close, retreat
                direction = -vec_to_player
            # else: in optimal range, maintain position

            # Shoot if ready
            self._attempt_shoot(player, world)

            return direction
        else:
            # No line of sight, use parent pathfinding
            return super()._handle_chase(player, world, dt)

    def _attempt_shoot(self, player, world) -> None:
        """Shoot at player if cooldown is ready.
        
        Args:
            player: Player object to shoot at
            world: World object to add bullet to
        """
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_shot_time >= self.shoot_cooldown and
                world.bullets is not None):
            self.last_shot_time = current_time
            self._fire_bullet(player, world.bullets)

    def _fire_bullet(self, player, bullets: list) -> None:
        """Create and fire bullet toward player.
        
        Args:
            player: Player object to aim at
            bullets: List to add bullet to
        """
        bullet = Bullet(
            self.rect.centerx,
            self.rect.centery,
            player.rect.centerx,
            player.rect.centery,
            SHOOTER_BULLET_SPEED,
            SHOOTER_BULLET_COLOR,
            self.damage
        )
        bullets.append(bullet)
