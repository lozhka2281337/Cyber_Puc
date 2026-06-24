import pygame
import random
from enum import Enum, auto

from core.pathfinder import PathFinder
import config as cfg
from config import (ENEMY_SIZE, AGRO_DISTANCE, LOSE_AGRO_DISTANCE, WAYPOINT_TOLERANCE)
from combat.damage import DamageSource, DamageType

SEPARATION_RADIUS_MULTIPLIER = 1.5
SEPARATION_STRENGTH = 1.5
KNOCKBACK_DECAY_RATE = 10.0
KNOCKBACK_MIN_THRESHOLD = 10.0


class EnemyState(Enum):
    PATROL = auto() 
    CHASE = auto() 
    RETURN = auto() 


class Enemy:
    def __init__(self, x: int, y: int, hp: int, speed: int, color: tuple, room: pygame.Rect):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)       
        self.hp = hp
        self.speed = speed
        self.base_speed = float(speed)
        self.color = color
        self.damage = 1
        self.base_damage = 1
        self.room = room 
        self.knockback = pygame.math.Vector2(0, 0)
        self.is_moving = False
        self.state = EnemyState.PATROL
        self.agro_distance = AGRO_DISTANCE
        self.lose_agro_distance = LOSE_AGRO_DISTANCE
        self.last_known_pos = None
        self.visible_timer = 0 
        self.patrol_target = None
        self.patrol_timer = 0.0
        self.path = []
        self.path_recalc_timer = 0.0
        self.stuck_timer = 0.0

    def _center_vector(self) -> pygame.math.Vector2:
        return pygame.math.Vector2(self.rect.center)

    def _vector_to(self, target) -> pygame.math.Vector2:
        return pygame.math.Vector2(target[0] - self.pos.x, target[1] - self.pos.y)

    def _vector_to_player(self, player) -> pygame.math.Vector2:
        return self._vector_to(player.rect.center)

    def _distance_to_player(self, player) -> float:
        return self.pos.distance_to(player.pos)

    def _is_stealth_phase(self, world) -> bool:
        return world.mod == cfg.DARK_MOD and not world.core_activated

    def _update_combat_modifiers(self, world) -> None:
        if self._is_stealth_phase(world):
            self.speed = self.base_speed * cfg.ENEMY_STEALTH_POWER_MULTIPLIER
            self.damage = max(1, int(round(self.base_damage * cfg.ENEMY_STEALTH_POWER_MULTIPLIER)))
        else:
            self.speed = self.base_speed
            self.damage = self.base_damage

    def move(self, walls: list[pygame.Rect], dt: float, direction: pygame.math.Vector2) -> None:
        if direction.magnitude() > 0:
            direction = direction.normalize()

        old_pos = pygame.math.Vector2(self.pos)

        velocity_x = direction.x * self.speed + self.knockback.x
        velocity_y = direction.y * self.speed + self.knockback.y

        self.pos.x += velocity_x * dt
        self.rect.x = round(self.pos.x)
        self._resolve_x_collision(walls, velocity_x)

        self.pos.y += velocity_y * dt
        self.rect.y = round(self.pos.y)
        self._resolve_y_collision(walls, velocity_y)

        self._decay_knockback(dt)

        self.is_moving = old_pos.distance_to(self.pos) > 0.01

    def _resolve_x_collision(self, walls: list[pygame.Rect], velocity_x: float) -> None:
        for wall in walls:
            if self.rect.colliderect(wall):
                if velocity_x > 0: self.rect.right = wall.left
                elif velocity_x < 0: self.rect.left = wall.right
                self.pos.x = float(self.rect.x)
                self.knockback.x = 0
                break

    def _resolve_y_collision(self, walls: list[pygame.Rect], velocity_y: float) -> None:
        for wall in walls:
            if self.rect.colliderect(wall):
                if velocity_y > 0: self.rect.bottom = wall.top
                elif velocity_y < 0: self.rect.top = wall.bottom
                self.pos.y = float(self.rect.y)
                self.knockback.y = 0
                break

    def _decay_knockback(self, dt: float) -> None:
        if self.knockback.magnitude() > KNOCKBACK_MIN_THRESHOLD:
            self.knockback = self.knockback.lerp(pygame.math.Vector2(0, 0), dt * KNOCKBACK_DECAY_RATE)
        else:
            self.knockback.x, self.knockback.y = 0, 0

    def get_damage(self, damage: int, damage_type=DamageType.GENERIC, source=DamageSource.PLAYER) -> None:
        actual_damage = self._resolve_damage(damage, damage_type, source)
        if actual_damage <= 0:
            return

        self.hp -= actual_damage
        self._on_damage_taken(damage_type, source)

    def _resolve_damage(self, damage: int, damage_type=DamageType.GENERIC, source=DamageSource.PLAYER) -> int:
        return damage

    def _on_damage_taken(self, damage_type=DamageType.GENERIC, source=DamageSource.PLAYER) -> None:
        if self.state in (EnemyState.PATROL, EnemyState.RETURN):
            self.state = EnemyState.CHASE

    def check_los(self, target_rect: pygame.Rect, walls: list[pygame.Rect]) -> bool:
        line = (self.rect.center, target_rect.center)
        for wall in walls:
            if wall.clipline(line):
                return False
        return True

    def _get_random_patrol_point(self) -> pygame.math.Vector2:
        margin = ENEMY_SIZE 
        x = random.randint(self.room.left + margin, self.room.right - margin)
        y = random.randint(self.room.top + margin, self.room.bottom - margin)
        return pygame.math.Vector2(x, y)

    def _handle_patrol(self, dt: float) -> pygame.math.Vector2:
        if self.patrol_timer > 0:
            self.patrol_timer -= dt
            return pygame.math.Vector2(0, 0)

        if not self.patrol_target:
            self.patrol_target = self._get_random_patrol_point()

        vec_to_target = self.patrol_target - self.pos
        if vec_to_target.magnitude() < WAYPOINT_TOLERANCE:
            self.patrol_target = None
            self.patrol_timer = random.uniform(1.0, 2.5) 
            return pygame.math.Vector2(0, 0)

        return vec_to_target

    def _handle_chase(self, player, world, dt: float) -> pygame.math.Vector2:
        if self.check_los(player.rect, world.walls):
            direct_vec = self._vector_to_player(player)

            # If direct movement hits geometry, switch to path nodes to go around corners.
            if self._would_collide_while_chasing(world.walls, direct_vec):
                return self._follow_path_to(
                    world,
                    pygame.math.Vector2(player.rect.center),
                    force_recalc=self.path_recalc_timer <= 0,
                )

            self.path.clear()
            return direct_vec
                                       
        elif self.last_known_pos:
            vec_to_target = self._follow_path_to(world, self.last_known_pos)
            if vec_to_target.magnitude() > 0:
                return vec_to_target

            self.last_known_pos = None
            return pygame.math.Vector2(0, 0)

        return pygame.math.Vector2(0, 0)

    def _handle_return(self, world, dt: float) -> pygame.math.Vector2:
        room_center = pygame.math.Vector2(self.room.center)

        vec_to_target = self._follow_path_to(world, room_center)
        if vec_to_target.magnitude() > 0:
            return vec_to_target

        if self.pos.distance_to(room_center) < WAYPOINT_TOLERANCE * 2:
            self.state = EnemyState.PATROL
            return pygame.math.Vector2(0, 0)
        else:
            self.state = EnemyState.PATROL 
            return pygame.math.Vector2(0, 0)

    def _would_collide_while_chasing(self, walls: list[pygame.Rect], direction: pygame.math.Vector2) -> bool:
        if direction.magnitude() == 0:
            return False

        probe_step = direction.normalize() * max(6, self.speed * 0.15)
        test_rect = self.rect.move(round(probe_step.x), round(probe_step.y))

        for wall in walls:
            if test_rect.colliderect(wall):
                return True
        return False

    def _steer_around_walls(self, walls: list[pygame.Rect], desired: pygame.math.Vector2) -> pygame.math.Vector2:
        if desired.magnitude() == 0:
            return desired

        desired_n = desired.normalize()

        # Try a small set of angular alternatives to avoid corner locking.
        for angle in (0, -35, 35, -70, 70, -105, 105, 180):
            candidate = desired_n.rotate(angle)
            if not self._would_collide_while_chasing(walls, candidate):
                return candidate

        return desired_n

    def _follow_path_to(self, world, target_pos: pygame.math.Vector2, force_recalc: bool = False) -> pygame.math.Vector2:
        if force_recalc or not self.path or self.path_recalc_timer <= 0:
            self.path = PathFinder.get_path(world.matrix, self.pos, target_pos)
            self.path_recalc_timer = 0.2

        if not self.path:
            return pygame.math.Vector2(0, 0)

        target_node = self.path[0]
        vec_to_node = target_node - self.pos

        if vec_to_node.magnitude() < WAYPOINT_TOLERANCE:
            self.path.pop(0)
            if not self.path:
                return pygame.math.Vector2(0, 0)
            vec_to_node = self.path[0] - self.pos

        return vec_to_node

    def _apply_stuck_recovery(self, world, desired_direction: pygame.math.Vector2) -> pygame.math.Vector2:
        if desired_direction.magnitude() == 0:
            return desired_direction

        # If enemy keeps pushing but does not move, aggressively repath and strafe out.
        if self.stuck_timer > 0.35:
            self.path.clear()
            self.path_recalc_timer = 0.0
            self.stuck_timer = 0.0

            base = desired_direction.normalize()
            side = pygame.math.Vector2(-base.y, base.x)
            if self._would_collide_while_chasing(world.walls, side):
                side = -side

            if side.magnitude() > 0 and not self._would_collide_while_chasing(world.walls, side):
                return side

        return desired_direction

    def _compose_navigation_direction(self, world, player, dt: float) -> pygame.math.Vector2:
        direction = pygame.math.Vector2(0, 0)

        if self.state == EnemyState.CHASE:
            direction = self._handle_chase(player, world, dt)
        elif self.state == EnemyState.RETURN:
            direction = self._handle_return(world, dt)
        elif self.state == EnemyState.PATROL:
            direction = self._handle_patrol(dt)

        direction = self._steer_around_walls(world.walls, direction)
        direction = self._apply_separation(world.enemies, direction)
        direction = self._apply_stuck_recovery(world, direction)
        return direction

    def _apply_separation(self, enemies: list, current_direction: pygame.math.Vector2) -> pygame.math.Vector2:
        separation_vector = pygame.math.Vector2(0, 0)
        neighbors_count = 0
        separation_radius = ENEMY_SIZE * SEPARATION_RADIUS_MULTIPLIER

        for other in enemies:
            if other is self:
                continue

            dist = self.pos.distance_to(other.pos)
            if 0 < dist < separation_radius:
                diff = self.pos - other.pos
                diff = diff.normalize() / dist 
                separation_vector += diff
                neighbors_count += 1

        if neighbors_count > 0:
            separation_vector /= neighbors_count
            if separation_vector.magnitude() > 0:
                separation_vector = separation_vector.normalize()
                current_direction = current_direction + separation_vector * SEPARATION_STRENGTH

        return current_direction

    def _update_state(self, player, world, dt: float) -> None:
        dist_to_player = self._distance_to_player(player)
        has_los = self.check_los(player.rect, world.walls)
        is_player_in_room = self.room.colliderect(player.rect)

        agro_distance = self.agro_distance
        lose_agro_distance = self.lose_agro_distance
        if self._is_stealth_phase(world):
            agro_distance *= cfg.ENEMY_STEALTH_AGRO_MULTIPLIER
            lose_agro_distance *= cfg.ENEMY_STEALTH_AGRO_MULTIPLIER

        if has_los:
            self.last_known_pos = pygame.math.Vector2(player.rect.center)

        old_state = self.state

        if self.state in [EnemyState.PATROL, EnemyState.RETURN]:
            if is_player_in_room:
                self.state = EnemyState.CHASE
            elif dist_to_player < agro_distance and has_los:
                self.state = EnemyState.CHASE

        elif self.state == EnemyState.CHASE:
            if has_los:
                if not is_player_in_room and dist_to_player > lose_agro_distance:
                    self.state = EnemyState.RETURN
                    self.last_known_pos = None
            else:
                if not self.last_known_pos:
                    self.state = EnemyState.RETURN

        if self.state != old_state:
            self.path.clear()
            self.path_recalc_timer = 0.0

    def update(self, world, player, dt: float) -> None:
        if self.path_recalc_timer > 0:
            self.path_recalc_timer -= dt

        self._update_combat_modifiers(world)
        self._update_state(player, world, dt)

        direction = self._compose_navigation_direction(world, player, dt)

        if self.visible_timer > 0:
            self.visible_timer -= dt

        self.move(world.walls, dt, direction)

        if direction.magnitude() > 0 and not self.is_moving:
            self.stuck_timer += dt
        else:
            self.stuck_timer = 0.0

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        offset_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.rect(surface, self.color, offset_rect)


class AnimatedEnemy(Enemy):
    def __init__(self, x: int, y: int, hp: int, speed: int, color: tuple, room: pygame.Rect):
        super().__init__(x, y, hp, speed, color, room)
        self.anim_left = None
        self.anim_right = None
        self.current_anim = None

    def update(self, world, player, dt: float) -> None:
        super().update(world, player, dt)
        
        if player.rect.centerx < self.rect.centerx:
            self.current_anim = self.anim_left
        else:
            self.current_anim = self.anim_right

        if self.is_moving:
            self.current_anim.update(dt)
        else:
            self.current_anim.current_idx = 0

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
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