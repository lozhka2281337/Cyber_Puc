"""Enemy entity system with state machine and AI behavior."""

import pygame
import random
from enum import Enum, auto
from typing import List, Optional, Tuple

from core.pathfinder import PathFinder
from config import (
    ENEMY_SIZE,
    AGRO_DISTANCE,
    LOSE_AGRO_DISTANCE,
    WAYPOINT_TOLERANCE
)

# Separation behavior constants
SEPARATION_RADIUS_MULTIPLIER = 1.5
SEPARATION_STRENGTH = 1.5
KNOCKBACK_DECAY_RATE = 10.0
KNOCKBACK_MIN_THRESHOLD = 10.0


class EnemyState(Enum):
    """Enemy AI states."""
    PATROL = auto()  # Patrolling assigned room
    CHASE = auto()   # Chasing player
    RETURN = auto()  # Returning to patrol room


class Enemy:
    """Base enemy class with state machine AI and movement."""

    def __init__(
        self,
        x: int,
        y: int,
        hp: int,
        speed: int,
        color: Tuple[int, int, int],
        room: pygame.Rect
    ) -> None:
        """Initialize enemy with position, stats, and behavior.
        
        Args:
            x: Starting X position
            y: Starting Y position
            hp: Health points
            speed: Movement speed in pixels/second
            color: RGB color tuple
            room: Assigned patrol room
        """
        # Position and physics
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.knockback = pygame.math.Vector2(0, 0)

        # Stats
        self.hp = hp
        self.speed = speed
        self.color = color
        self.damage = 1  # Default, can be overridden by subclasses

        # Behavior
        self.room = room
        self.state = EnemyState.PATROL
        self.agro_distance = AGRO_DISTANCE
        self.lose_agro_distance = LOSE_AGRO_DISTANCE

        # Patrol state
        self.patrol_target: Optional[pygame.math.Vector2] = None
        self.patrol_timer = 0.0

        # Chase state
        self.last_known_pos: Optional[pygame.math.Vector2] = None
        self.path: List[pygame.math.Vector2] = []

        # Visibility (for ping system)
        self.visible_timer = 0.0
        self.is_moving = False

    def move(
        self,
        walls: List[pygame.Rect],
        dt: float,
        direction: pygame.math.Vector2
    ) -> None:
        """Move enemy with collision detection and knockback.
        
        Args:
            walls: List of wall collision rectangles
            dt: Delta time
            direction: Movement direction vector
        """
        if direction.magnitude() > 0:
            direction = direction.normalize()

        old_pos = pygame.math.Vector2(self.pos)

        # Calculate velocity
        velocity_x = direction.x * self.speed + self.knockback.x
        velocity_y = direction.y * self.speed + self.knockback.y

        # Move X and handle collisions
        self.pos.x += velocity_x * dt
        self.rect.x = round(self.pos.x)
        self._resolve_x_collision(walls, velocity_x)

        # Move Y and handle collisions
        self.pos.y += velocity_y * dt
        self.rect.y = round(self.pos.y)
        self._resolve_y_collision(walls, velocity_y)

        # Decay knockback
        self._decay_knockback(dt)

        # Update movement flag
        self.is_moving = old_pos.distance_to(self.pos) > 0.01

    def _resolve_x_collision(self, walls: List[pygame.Rect], velocity_x: float) -> None:
        """Resolve X-axis collisions with walls."""
        for wall in walls:
            if self.rect.colliderect(wall):
                if velocity_x > 0:
                    self.rect.right = wall.left
                elif velocity_x < 0:
                    self.rect.left = wall.right
                self.pos.x = float(self.rect.x)
                self.knockback.x = 0
                break

    def _resolve_y_collision(self, walls: List[pygame.Rect], velocity_y: float) -> None:
        """Resolve Y-axis collisions with walls."""
        for wall in walls:
            if self.rect.colliderect(wall):
                if velocity_y > 0:
                    self.rect.bottom = wall.top
                elif velocity_y < 0:
                    self.rect.top = wall.bottom
                self.pos.y = float(self.rect.y)
                self.knockback.y = 0
                break

    def _decay_knockback(self, dt: float) -> None:
        """Decay knockback velocity over time."""
        if self.knockback.magnitude() > KNOCKBACK_MIN_THRESHOLD:
            self.knockback = self.knockback.lerp(
                pygame.math.Vector2(0, 0),
                dt * KNOCKBACK_DECAY_RATE
            )
        else:
            self.knockback.x = 0
            self.knockback.y = 0

    def get_damage(self, damage: int) -> None:
        """Take damage and enter chase state if not already.
        
        Args:
            damage: Damage amount
        """
        self.hp -= damage
        if self.state in [EnemyState.PATROL, EnemyState.RETURN]:
            self.state = EnemyState.CHASE

    def check_los(self, target_rect: pygame.Rect, walls: List[pygame.Rect]) -> bool:
        """Check if target is visible (line of sight).
        
        Args:
            target_rect: Target's rectangle
            walls: List of walls to check against
            
        Returns:
            True if target is visible, False otherwise
        """
        line = (self.rect.center, target_rect.center)
        for wall in walls:
            if wall.clipline(line):
                return False
        return True

    def _get_random_patrol_point(self) -> pygame.math.Vector2:
        """Generate random patrol point within assigned room.
        
        Returns:
            Random position within room boundaries
        """
        margin = ENEMY_SIZE
        x = random.randint(self.room.left + margin, self.room.right - margin)
        y = random.randint(self.room.top + margin, self.room.bottom - margin)
        return pygame.math.Vector2(x, y)

    def _handle_patrol(self, dt: float) -> pygame.math.Vector2:
        """Handle patrol behavior.
        
        Args:
            dt: Delta time
            
        Returns:
            Movement direction vector
        """
        # Wait at waypoint
        if self.patrol_timer > 0:
            self.patrol_timer -= dt
            return pygame.math.Vector2(0, 0)

        # Pick new patrol target if none exists
        if not self.patrol_target:
            self.patrol_target = self._get_random_patrol_point()

        # Move towards patrol target
        vec_to_target = self.patrol_target - self.pos
        if vec_to_target.magnitude() < WAYPOINT_TOLERANCE:
            # Reached waypoint, wait before next
            self.patrol_target = None
            self.patrol_timer = random.uniform(1.0, 2.5)
            return pygame.math.Vector2(0, 0)

        return vec_to_target

    def _handle_chase(self, player, world, dt: float) -> pygame.math.Vector2:
        """Handle chase behavior.
        
        Args:
            player: Player object
            world: World object with pathfinding matrix
            dt: Delta time
            
        Returns:
            Movement direction vector
        """
        # Direct line to player
        if self.check_los(player.rect, world.walls):
            self.path.clear()
            return pygame.math.Vector2(
                player.rect.centerx - self.rect.centerx,
                player.rect.centery - self.rect.centery
            )

        # Pathfind to last known position
        if self.last_known_pos:
            if not self.path:
                self.path = PathFinder.get_path(
                    world.matrix,
                    self.pos,
                    self.last_known_pos
                )

            if self.path:
                target_node = self.path[0]
                vec_to_node = target_node - self.pos

                if vec_to_node.magnitude() < WAYPOINT_TOLERANCE:
                    self.path.pop(0)
                    if not self.path:
                        return pygame.math.Vector2(0, 0)
                return vec_to_node
            else:
                self.last_known_pos = None
                return pygame.math.Vector2(0, 0)

        return pygame.math.Vector2(0, 0)

    def _handle_return(self, world, dt: float) -> pygame.math.Vector2:
        """Handle return to patrol behavior.
        
        Args:
            world: World object with pathfinding matrix
            dt: Delta time
            
        Returns:
            Movement direction vector
        """
        room_center = pygame.math.Vector2(self.room.center)

        if not self.path:
            self.path = PathFinder.get_path(world.matrix, self.pos, room_center)

        if self.path:
            target_node = self.path[0]
            vec_to_node = target_node - self.pos

            if vec_to_node.magnitude() < WAYPOINT_TOLERANCE:
                self.path.pop(0)
                if not self.path:
                    self.state = EnemyState.PATROL
                return pygame.math.Vector2(0, 0)
            return vec_to_node
        else:
            self.state = EnemyState.PATROL
            return pygame.math.Vector2(0, 0)

    def _apply_separation(
        self,
        enemies: List['Enemy'],
        current_direction: pygame.math.Vector2
    ) -> pygame.math.Vector2:
        """Apply flocking separation to avoid clustering.
        
        Args:
            enemies: List of all enemies
            current_direction: Current movement direction
            
        Returns:
            Adjusted direction with separation applied
        """
        separation_vector = pygame.math.Vector2(0, 0)
        neighbors_count = 0
        separation_radius = ENEMY_SIZE * SEPARATION_RADIUS_MULTIPLIER

        # Accumulate separation forces from nearby enemies
        for other in enemies:
            if other is self:
                continue

            dist = self.pos.distance_to(other.pos)
            if 0 < dist < separation_radius:
                # Repulsion force inversely proportional to distance
                diff = self.pos - other.pos
                diff = diff.normalize() / dist
                separation_vector += diff
                neighbors_count += 1

        # Apply averaged separation force
        if neighbors_count > 0:
            separation_vector /= neighbors_count
            if separation_vector.magnitude() > 0:
                separation_vector = separation_vector.normalize()
                current_direction = current_direction + separation_vector * SEPARATION_STRENGTH

        return current_direction

    def _update_state(self, player, world, dt: float) -> None:
        """Update AI state based on player proximity and visibility.
        
        Args:
            player: Player object
            world: World object
            dt: Delta time
        """
        dist_to_player = self.pos.distance_to(player.pos)
        has_los = self.check_los(player.rect, world.walls)
        is_player_in_room = self.room.colliderect(player.rect)

        # Update last known position if player is visible
        if has_los:
            self.last_known_pos = pygame.math.Vector2(player.rect.center)

        old_state = self.state

        # State transitions
        if self.state in [EnemyState.PATROL, EnemyState.RETURN]:
            if is_player_in_room or (dist_to_player < self.agro_distance and has_los):
                self.state = EnemyState.CHASE

        elif self.state == EnemyState.CHASE:
            if has_los:
                if not is_player_in_room and dist_to_player > self.lose_agro_distance:
                    self.state = EnemyState.RETURN
                    self.last_known_pos = None
            else:
                if not self.last_known_pos:
                    self.state = EnemyState.RETURN

        # Clear path on state change
        if self.state != old_state:
            self.path.clear()

    def update(self, world, player, dt: float) -> None:
        """Update enemy AI and movement.
        
        Args:
            world: World object
            player: Player object
            dt: Delta time
        """
        self._update_state(player, world, dt)

        # Get direction based on current state
        direction = pygame.math.Vector2(0, 0)
        if self.state == EnemyState.CHASE:
            direction = self._handle_chase(player, world, dt)
        elif self.state == EnemyState.RETURN:
            direction = self._handle_return(world, dt)
        elif self.state == EnemyState.PATROL:
            direction = self._handle_patrol(dt)

        # Apply separation behavior
        direction = self._apply_separation(world.enemies, direction)

        # Update visibility timer
        if self.visible_timer > 0:
            self.visible_timer -= dt

        # Move and apply collisions
        self.move(world.walls, dt, direction)

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        """Draw enemy on screen.
        
        Args:
            surface: Drawing surface
            cam_x: Camera X offset
            cam_y: Camera Y offset
        """
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.rect(surface, self.color, offset_rect)


class AnimatedEnemy(Enemy):
    """Enemy with sprite animation based on direction."""

    def __init__(
        self,
        x: int,
        y: int,
        hp: int,
        speed: int,
        color: Tuple[int, int, int],
        room: pygame.Rect
    ) -> None:
        """Initialize animated enemy.
        
        Args:
            x: Starting X position
            y: Starting Y position
            hp: Health points
            speed: Movement speed
            color: RGB color
            room: Patrol room
        """
        super().__init__(x, y, hp, speed, color, room)
        self.anim_left = None
        self.anim_right = None
        self.current_anim = None

    def update(self, world, player, dt: float) -> None:
        """Update animation and behavior.
        
        Args:
            world: World object
            player: Player object
            dt: Delta time
        """
        super().update(world, player, dt)

        # Select animation based on direction to player
        if player.rect.centerx < self.rect.centerx:
            self.current_anim = self.anim_left
        else:
            self.current_anim = self.anim_right

        # Update animation frame
        if self.is_moving and self.current_anim:
            self.current_anim.update(dt)
        elif self.current_anim:
            self.current_anim.current_idx = 0

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        """Draw animated enemy on screen.
        
        Args:
            surface: Drawing surface
            cam_x: Camera X offset
            cam_y: Camera Y offset
        """
        if not self.current_anim:
            super().draw(surface, cam_x, cam_y)
            return

        frame = self.current_anim.get_frame()
        screen_x = self.rect.x - cam_x
        screen_y = self.rect.y - cam_y
        center_x = screen_x + self.rect.width // 2
        center_y = screen_y + self.rect.height // 2
        frame_rect = frame.get_rect(center=(center_x, center_y))
        surface.blit(frame, frame_rect)
