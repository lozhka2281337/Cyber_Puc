import pygame
from core.animation import Animation
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
        self.anim_left = Animation("assets/fast-enemy-run-left.png", columns=5, speed=0.1, scale=1.5)
        self.anim_right = Animation("assets/fast-enemy-run-right.png", columns=5, speed=0.1, scale=1.5)
        self.current_anim = self.anim_right 

    def update(self, dt: float, player, world) -> None:
        super().update(dt, player, world)
        
        if player.rect.centerx < self.rect.centerx:
            self.current_anim = self.anim_left
        else:
            self.current_anim = self.anim_right   
        if self.is_moving:
            self.current_anim.update(dt)
        else:
            self.current_anim.current_idx = 0

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        frame = self.current_anim.get_frame()
        screen_x = self.rect.x - cam_x
        screen_y = self.rect.y - cam_y
        center_x = screen_x + self.rect.width // 2
        center_y = screen_y + self.rect.height // 2
        frame_rect = frame.get_rect(center=(center_x, center_y))  
        surface.blit(frame, frame_rect)


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
        bullets.append(new_bullet)