import pygame
import random
import math
from enum import Enum, auto

from .enemy import Enemy, EnemyState
from projectile.grenade import Grenade
from projectile.effects import SparkEffect

BOSS_SIZE = 64
BOSS_HP = 500
BOSS_SPEED = 180
BOSS_COLOR = (180, 0, 255)

PHASE2_HP_RATIO = 0.60
PHASE3_HP_RATIO = 0.30

ATTACK_COOLDOWN = {1: 2.5, 2: 2.0, 3: 1.5}
LASER_CHARGE_TIME = 1.2
LASER_FIRE_TIME = {1: 1.0, 2: 1.0, 3: 1.5}
LASER_DMG_INTERVAL = 0.5
LASER_BEAM_WIDTH = {1: 12, 2: 12, 3: 24}
MELEE_DURATION = 0.35
MELEE_HIT_FRAC = 0.5
MELEE_REACH = 90
MELEE_ARC = 160
MELEE_DAMAGE = 2
DASH_DURATION = 0.25
DASH_COOLDOWN = {1: 5.0, 2: 4.0, 3: 3.0}
DASH_SPEED = {1: 500, 2: 550, 3: 700}
SUMMON_DURATION = 2.0

PREFERRED_MIN_DIST = 180
PREFERRED_MAX_DIST = 350

GRENADE_SPEED = 350
GRENADE_BLAST_R = 90
GRENADE_FUSE = 1200
GRENADE_MAX_RANGE = 400
GRENADE_COLOR = (220, 50, 200)

PHASE_COLOR = {1: (180, 0, 255), 2: (255, 120, 0), 3: (255, 0, 50)}
LASER_COLOR = {1: (0, 200, 255), 2: (255, 150, 0), 3: (255, 50, 50)}

BOSS_CONTACT_DAMAGE = 2
BOSS_BULLET_DAMAGE = 10
BOSS_GRENADE_DAMAGE = 45
BOSS_LASER_TICK_DAMAGE = 12
BOSS_MELEE_DAMAGE = 90


class BossPhase(Enum):
    PHASE1 = 1
    PHASE2 = 2
    PHASE3 = 3


class BossState(Enum):
    CHASE_KITE = auto()
    ATTACK_GRENADE = auto()
    ATTACK_MELEE = auto()
    ATTACK_LASER_CHARGE = auto()
    ATTACK_LASER_FIRE = auto()
    DASH = auto()
    SUMMON = auto()


class Boss(Enemy):
    def __init__(self, x: int, y: int, room: pygame.Rect):
        super().__init__(x, y, BOSS_HP, BOSS_SPEED, BOSS_COLOR, room)
        self.rect = pygame.Rect(x, y, BOSS_SIZE, BOSS_SIZE)
        self.pos = pygame.math.Vector2(x, y)

        self.max_hp = BOSS_HP
        self.damage = BOSS_CONTACT_DAMAGE
        self.state = EnemyState.CHASE

        self.phase = BossPhase.PHASE1
        self.boss_state = BossState.CHASE_KITE

        self.attack_cooldown = 2.0
        self.attack_timer = 0.0
        self.dash_cooldown = 3.0
        self.dash_timer = 0.0
        self.dash_velocity = pygame.math.Vector2(0, 0)

        self.laser_dir = pygame.math.Vector2(1, 0)
        self.laser_dmg_timer = 0.0
        self._laser_end_cache = None

        self.melee_angle = 0.0
        self.melee_hit_done = False

        self.phase2_triggered = False
        self.phase3_triggered = False
        self.summon_timer = 0.0
        self.is_invulnerable = False
        self.summon_at_center = False
        self.minions_spawned = False

        self._walls = []
        self._cam_x = 0.0
        self._cam_y = 0.0

        self._font_phase = pygame.font.SysFont("Courier New", 14, bold=True)

        self.last_laser_hit_time = -9999.0
        self.last_player_melee_hit_time = -9999.0

    def get_damage(self, damage: int, damage_type="default", source="player") -> None:
        if self.is_invulnerable:
            return

        if damage_type == "grenade":
            if source == "boss":
                return
            self.hp -= BOSS_GRENADE_DAMAGE
            return

        if damage_type == "laser":
            now = pygame.time.get_ticks() / 1000.0
            if now - self.last_laser_hit_time < 0.25:
                return
            self.last_laser_hit_time = now
            self.hp -= BOSS_LASER_TICK_DAMAGE
            return

        if damage_type == "melee":
            now = pygame.time.get_ticks() / 1000.0
            if now - self.last_player_melee_hit_time < 0.25:
                return
            self.last_player_melee_hit_time = now
            self.hp -= BOSS_MELEE_DAMAGE
            return

        if damage_type == "bullet":
            self.hp -= min(damage, BOSS_BULLET_DAMAGE)
            return

        self.hp -= damage

    def update(self, world, player, dt: float) -> None:
        self._walls = world.walls
        self._check_phase_transition()
        self._tick_boss_fsm(world, player, dt)
        self._decay_knockback(dt)

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        self._cam_x = cam_x
        self._cam_y = cam_y

        phase_n = self.phase.value
        color = PHASE_COLOR[phase_n]
        offset = self.rect.move(-cam_x, -cam_y)

        inner = tuple(max(0, c // 3) for c in color)
        pygame.draw.rect(surface, inner, offset)
        pygame.draw.rect(surface, color, offset, 3)

        self._draw_corner_brackets(surface, offset, color)

        if self.is_invulnerable:
            pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.008)) * 8)
            shield_rect = offset.inflate(pulse * 2 + 6, pulse * 2 + 6)
            pygame.draw.rect(surface, (100, 220, 255), shield_rect, 2)

        self._draw_hp_bar(surface, offset, color)

        label = self._font_phase.render(f"ROOT-KIT [P{phase_n}]", True, color)
        surface.blit(label, (offset.centerx - label.get_width() // 2, offset.top - 24))

        if self.boss_state == BossState.ATTACK_MELEE:
            self._draw_melee_arc(surface, offset)
        elif self.boss_state in (BossState.ATTACK_LASER_CHARGE, BossState.ATTACK_LASER_FIRE):
            self._draw_laser_visual(surface, offset, phase_n)

    def _check_phase_transition(self) -> None:
        phase_n = self.phase.value
        hp_ratio = self.hp / self.max_hp

        if phase_n == 1 and hp_ratio < PHASE2_HP_RATIO and not self.phase2_triggered:
            self.phase2_triggered = True
            self.phase = BossPhase.PHASE2
            self.boss_state = BossState.SUMMON
            self.summon_timer = SUMMON_DURATION
            self.summon_at_center = False
            self.minions_spawned = False
            self.is_invulnerable = False

        elif phase_n == 2 and hp_ratio < PHASE3_HP_RATIO and not self.phase3_triggered:
            self.phase3_triggered = True
            self.phase = BossPhase.PHASE3
            self.attack_cooldown = 1.0

    def _tick_boss_fsm(self, world, player, dt: float) -> None:
        if self.boss_state == BossState.CHASE_KITE:
            self._tick_chase_kite(world, player, dt)
        elif self.boss_state == BossState.ATTACK_GRENADE:
            self._tick_attack_grenade(world, player, dt)
        elif self.boss_state == BossState.ATTACK_MELEE:
            self._tick_attack_melee(world, player, dt)
        elif self.boss_state == BossState.ATTACK_LASER_CHARGE:
            self._tick_laser_charge(world, player, dt)
        elif self.boss_state == BossState.ATTACK_LASER_FIRE:
            self._tick_laser_fire(world, player, dt)
        elif self.boss_state == BossState.DASH:
            self._tick_dash(world, player, dt)
        elif self.boss_state == BossState.SUMMON:
            self._tick_summon(world, dt)

    def _tick_chase_kite(self, world, player, dt: float) -> None:
        dist = self.pos.distance_to(player.pos)

        self.attack_cooldown -= dt
        if self.attack_cooldown <= 0:
            self._pick_attack(dist, self.phase.value, world, player)
            return

        self.dash_cooldown -= dt
        if self.dash_cooldown <= 0 and dist > 80:
            self._start_dash(player)
            return

        direction = self._calc_kite_direction(player, dist)
        direction = self._apply_separation(world.enemies, direction)
        self.move(world.walls, dt, direction)

    def _calc_kite_direction(self, player, dist: float) -> pygame.math.Vector2:
        to_player = pygame.math.Vector2(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery
        )

        if to_player.magnitude() == 0:
            return pygame.math.Vector2(0, 0)

        to_player_n = to_player.normalize()

        if dist > PREFERRED_MAX_DIST:
            return to_player_n
        if dist < PREFERRED_MIN_DIST:
            return -to_player_n

        strafe = pygame.math.Vector2(-to_player_n.y, to_player_n.x)
        t = pygame.time.get_ticks() // 3000
        if t % 2 == 0:
            strafe = -strafe
        return strafe

    def _pick_attack(self, dist: float, phase_n: int, world, player) -> None:
        has_los = self.check_los(player.rect, self._walls)

        melee_chance = max(0.2, 0.5 - (phase_n - 1) * 0.15)
        laser_chance = max(0.3, 0.6 - (phase_n - 1) * 0.15)

        if dist < 130:
            self._enter_melee(player)
        elif dist < 300 and has_los:
            if random.random() < melee_chance:
                self._enter_melee(player)
            else:
                self._enter_grenade(world, player)
        elif has_los:
            if random.random() < laser_chance:
                self._enter_laser_charge(player)
            else:
                self._enter_grenade(world, player)
        else:
            self._enter_grenade(world, player)

    def _enter_grenade(self, world, player) -> None:
        grenade = Grenade(
            self.rect.centerx,
            self.rect.centery,
            player.rect.centerx,
            player.rect.centery,
            GRENADE_SPEED,
            GRENADE_COLOR,
            GRENADE_BLAST_R,
            GRENADE_FUSE,
            GRENADE_MAX_RANGE,
            owner="boss",
            damage=2
        )
        world.grenades.append(grenade)
        self.boss_state = BossState.ATTACK_GRENADE
        self.attack_timer = 0.5

    def _tick_attack_grenade(self, world, player, dt: float) -> None:
        direction = self._calc_kite_direction(player, self.pos.distance_to(player.pos))
        self.move(world.walls, dt, direction)

        self.attack_timer -= dt
        if self.attack_timer <= 0:
            self._reset_to_chase()

    def _enter_melee(self, player) -> None:
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        self.melee_angle = math.degrees(math.atan2(dy, dx))
        self.melee_hit_done = False
        self.boss_state = BossState.ATTACK_MELEE
        self.attack_timer = MELEE_DURATION

    def _tick_attack_melee(self, world, player, dt: float) -> None:
        to_p = pygame.math.Vector2(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery
        )
        if to_p.magnitude() > 0:
            self.move(world.walls, dt, to_p.normalize() * 0.3)

        self.attack_timer -= dt

        if not self.melee_hit_done and self.attack_timer <= MELEE_DURATION * (1 - MELEE_HIT_FRAC):
            self.melee_hit_done = True
            self._apply_melee_damage(player)

        if self.attack_timer <= 0:
            self._reset_to_chase()

    def _apply_melee_damage(self, player) -> None:
        boss_center = pygame.math.Vector2(self.rect.center)
        player_center = pygame.math.Vector2(player.rect.center)
        dist = boss_center.distance_to(player_center)

        if dist <= MELEE_REACH + 16:
            dx = player_center.x - boss_center.x
            dy = player_center.y - boss_center.y
            angle_to_player = math.degrees(math.atan2(dy, dx))
            angle_diff = (angle_to_player - self.melee_angle + 180) % 360 - 180

            if abs(angle_diff) <= MELEE_ARC / 2:
                player.get_damage(MELEE_DAMAGE)

    def _enter_laser_charge(self, player) -> None:
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        d = pygame.math.Vector2(dx, dy)
        self.laser_dir = d.normalize() if d.magnitude() > 0 else pygame.math.Vector2(1, 0)
        self.boss_state = BossState.ATTACK_LASER_CHARGE
        self.attack_timer = LASER_CHARGE_TIME
        self.laser_dmg_timer = 0.0

    def _tick_laser_charge(self, world, player, dt: float) -> None:
        self.attack_timer -= dt
        if self.attack_timer <= 0:
            self.boss_state = BossState.ATTACK_LASER_FIRE
            self.attack_timer = LASER_FIRE_TIME[self.phase.value]

    def _tick_laser_fire(self, world, player, dt: float) -> None:
        self.attack_timer -= dt
        self.laser_dmg_timer -= dt

        if self.laser_dmg_timer <= 0:
            self.laser_dmg_timer = LASER_DMG_INTERVAL
            self._check_laser_player_damage(player)

        if self.attack_timer <= 0:
            self._laser_end_cache = None
            self._reset_to_chase()

    def _check_laser_player_damage(self, player) -> None:
        start = pygame.math.Vector2(self.rect.center)
        end = self._get_laser_end(start, self._walls)

        if player.rect.clipline((int(start.x), int(start.y)), (int(end.x), int(end.y))):
            player.get_damage(1)

    def _get_laser_end(self, start: pygame.math.Vector2, walls: list[pygame.Rect], max_range: float = 1500.0) -> pygame.math.Vector2:
        end_raw = start + self.laser_dir * max_range
        end_pt = end_raw
        min_dist = max_range

        for wall in walls:
            hit = wall.clipline((int(start.x), int(start.y)), (int(end_raw.x), int(end_raw.y)))
            if hit:
                hp = pygame.math.Vector2(hit[0])
                d = start.distance_to(hp)
                if d < min_dist:
                    min_dist = d
                    end_pt = hp
        return end_pt

    def _start_dash(self, player) -> None:
        phase_n = self.phase.value
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        d = pygame.math.Vector2(dx, dy)
        direction = d.normalize() if d.magnitude() > 0 else pygame.math.Vector2(1, 0)
        self.dash_velocity = direction * DASH_SPEED[phase_n]
        self.boss_state = BossState.DASH
        self.dash_timer = DASH_DURATION

    def _tick_dash(self, world, player, dt: float) -> None:
        phase_n = self.phase.value
        if random.random() < 0.4:
            world.effects.append(SparkEffect(self.rect.centerx, self.rect.centery, PHASE_COLOR[phase_n]))

        self.move(world.walls, dt, self.dash_velocity.normalize())
        self.knockback = pygame.math.Vector2(self.dash_velocity.x, self.dash_velocity.y)

        self.dash_timer -= dt
        if self.dash_timer <= 0:
            self.knockback = pygame.math.Vector2(0, 0)
            self.dash_cooldown = DASH_COOLDOWN[phase_n]
            self.boss_state = BossState.CHASE_KITE

    def _tick_summon(self, world, dt: float) -> None:
        center = pygame.math.Vector2(self.room.center)
        dist_to_center = self.pos.distance_to(center)

        if not self.summon_at_center:
            if dist_to_center > 20:
                direction = (center - self.pos).normalize()
                self.move(world.walls, dt, direction)
            else:
                self.summon_at_center = True
                self.is_invulnerable = True

        if not self.minions_spawned:
            self._spawn_minions(world)
            self.minions_spawned = True

        self.summon_timer -= dt
        if self.summon_timer <= 0:
            self.is_invulnerable = False
            self.summon_at_center = False
            self.minions_spawned = False
            self._reset_to_chase()

    def _spawn_minions(self, world) -> None:
        from .enemy_type import Swarm, Tank, Shooter

        groups = [
            (Swarm, 2),
            (Tank, 1),
            (Shooter, 1),
        ]

        margin = 50
        room = self.room

        for EnemyCls, count in groups:
            for _ in range(count):
                x = random.randint(room.left + margin, max(room.left + margin + 1, room.right - margin - 32))
                y = random.randint(room.top + margin, max(room.top + margin + 1, room.bottom - margin - 32))
                world.enemies.append(EnemyCls(x, y, room))

    def _reset_to_chase(self) -> None:
        phase_n = self.phase.value
        self.boss_state = BossState.CHASE_KITE
        self.attack_cooldown = ATTACK_COOLDOWN[phase_n]

    def _draw_hp_bar(self, surface: pygame.Surface, offset_rect: pygame.Rect, color: tuple) -> None:
        bar_w = offset_rect.width
        bar_h = 8
        bar_x = offset_rect.x
        bar_y = offset_rect.bottom + 4
        fill_w = int(bar_w * max(0, self.hp / self.max_hp))

        pygame.draw.rect(surface, (40, 10, 10), (bar_x, bar_y, bar_w, bar_h))
        if fill_w > 0:
            pygame.draw.rect(surface, color, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(surface, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 1)

    def _draw_corner_brackets(self, surface: pygame.Surface, rect: pygame.Rect, color: tuple) -> None:
        sz = 8
        pts = [
            (rect.left, rect.top, sz, 0),
            (rect.left, rect.top, 0, sz),
            (rect.right - sz, rect.top, sz, 0),
            (rect.right, rect.top, 0, sz),
            (rect.left, rect.bottom - sz, sz, 0),
            (rect.left, rect.bottom, 0, -sz),
            (rect.right - sz, rect.bottom - sz, sz, 0),
            (rect.right, rect.bottom, 0, -sz),
        ]
        for x, y, dx, dy in pts:
            pygame.draw.line(surface, color, (x, y), (x + dx, y + dy), 2)

    def _draw_melee_arc(self, surface: pygame.Surface, offset_rect: pygame.Rect) -> None:
        from config import SCREEN_WIDTH, SCREEN_HEIGHT
        arc_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        center = (offset_rect.centerx, offset_rect.centery)

        progress = 1.0 - max(0, self.attack_timer / MELEE_DURATION)
        alpha_val = int(220 * (1.0 - progress))

        start_a = math.radians(self.melee_angle - MELEE_ARC / 2)
        end_a = math.radians(self.melee_angle + MELEE_ARC / 2)
        points = [center]
        steps = 12
        for i in range(steps + 1):
            a = start_a + (end_a - start_a) * (i / steps)
            px = center[0] + math.cos(a) * MELEE_REACH
            py = center[1] + math.sin(a) * MELEE_REACH
            points.append((px, py))

        phase_col = PHASE_COLOR[self.phase.value]
        pygame.draw.polygon(arc_surf, (*phase_col, alpha_val // 3), points)
        pygame.draw.polygon(arc_surf, (*phase_col, alpha_val), points, 2)
        surface.blit(arc_surf, (0, 0))

    def _draw_laser_visual(self, surface: pygame.Surface, offset_rect: pygame.Rect, phase_n: int) -> None:
        col = LASER_COLOR[phase_n]
        beam_w = LASER_BEAM_WIDTH[phase_n]
        start_s = (offset_rect.centerx, offset_rect.centery)
        start_w = pygame.math.Vector2(self.rect.center)

        if self.boss_state == BossState.ATTACK_LASER_CHARGE:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.02)) * 6
            radius = int(10 + pulse)
            pygame.draw.circle(surface, col, start_s, radius)
            pygame.draw.circle(surface, (255, 255, 255), start_s, max(1, radius - 4))
            aim_end_w = start_w + self.laser_dir * 200
            aim_end_s = (int(aim_end_w.x - self._cam_x), int(aim_end_w.y - self._cam_y))
            pygame.draw.line(surface, (*col, 120), start_s, aim_end_s, 1)

        elif self.boss_state == BossState.ATTACK_LASER_FIRE:
            end_w = self._get_laser_end(start_w, self._walls)
            self._laser_end_cache = end_w
            end_s = (int(end_w.x - self._cam_x), int(end_w.y - self._cam_y))

            pygame.draw.line(surface, col, start_s, end_s, beam_w)
            pygame.draw.line(surface, (255, 255, 255), start_s, end_s, max(1, beam_w // 3))

            spark_r = int(beam_w * 1.5 + abs(math.sin(pygame.time.get_ticks() * 0.05)) * 3)
            pygame.draw.circle(surface, col, end_s, spark_r)
            pygame.draw.circle(surface, (255, 255, 255), end_s, max(2, spark_r // 2))