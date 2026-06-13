import pygame
import math

from core.inventory import Inventory 
from core.animation import Animation 
from projectile.ping_wave import PingWave

import config as cfg

class Player:
    def __init__(self, x: int, y: int):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, cfg.PLAYER_SIZE, cfg.PLAYER_SIZE)
        self.speed = cfg.PLAYER_SPEED
        self.color = cfg.PLAYER_COLOR
        self.hp = cfg.PLAYER_HP

        self.inventory = Inventory()

        self.anim = Animation("assets/main-Sheet.png", columns=6, speed=0.07, scale=1.5)
        self.flip_x = True 

        self.invulnerable_timer = 0 # таймер для щита бессмертия, появляющийся после получения урона
        self.ping_timer = 0
    
    def switch_weapon(self, forward: bool):
        if forward:
            self.inventory.next_weapon()
        else:
            self.inventory.prev_weapon()

    def _check_enemy_collisions(self, enemies):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                self.get_damage(enemy.damage)

    def shot(self, camera_x: int, camera_y: int, world) -> None:
        self.inventory.get_current().shot(self.pos, camera_x, camera_y, world)

    def ping(self, world):
        if self.ping_timer <= 0 and world.mod == cfg.DARK_MOD: 
            world.pings.append(PingWave(self.pos.x, self.pos.y))
            self.ping_timer = cfg.PING_TIMER

    def process_weapon_damage(self, enemies, walls) -> None:
        self.inventory.get_current().process_damage(enemies, self.rect, walls)
        
    def get_damage(self, damage=1):
        if self.invulnerable_timer <= 0: 
            self.hp -= damage
            self.invulnerable_timer = 3.0

    def _movement(self, direction: pygame.math.Vector2, dt: float, walls: list):
        """ двигаем игрока:
        1) нормализация
        2) двигаем по x - проверяем на коллизии
        3) двигаем по y - проверяем на коллизии  
        """

        if direction.magnitude() > 0:
            direction = direction.normalize()

        current_weapon = self.inventory.get_current()
        current_speed = self.speed
        
        if getattr(current_weapon, 'is_firing', False) or getattr(current_weapon, 'is_charging', False):
            current_speed = self.speed * 0.2

        self.pos.x += direction.x * current_speed * dt
        self.rect.x = int(self.pos.x)

        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.x > 0: self.rect.right = wall.left
                elif direction.x < 0: self.rect.left = wall.right
                self.pos.x = float(self.rect.x) 

        self.pos.y += direction.y * current_speed * dt
        self.rect.y = int(self.pos.y) 

        for wall in walls:
            if self.rect.colliderect(wall):
                if direction.y > 0: self.rect.bottom = wall.top
                elif direction.y < 0: self.rect.top = wall.bottom         
                self.pos.y = float(self.rect.y)

    def _update_shield_timer(self, dt):
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

    def _update_ping_timer(self, dt):
        if self.ping_timer > 0:
            self.ping_timer -= dt

    def _update_sprite(self, direction, dt):
        # Поворот спрайта 
        if direction.x < 0:
            self.flip_x = False 
        elif direction.x > 0:
            self.flip_x = True 

        # Обновление кадров 
        if direction.magnitude() > 0:
            self.anim.update(dt) 
        else:
            self.anim.current_idx = 0 

    def update(self, dt: float, world): 
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0, 0)

        if keys[pygame.K_w] or keys[pygame.K_UP]: direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: direction.x += 1
        
        self._movement(direction, dt, world.walls)
        self._check_enemy_collisions(world.enemies)
        self.inventory.update_all()

        self._update_sprite(direction, dt)

        # обновление таймера пинга и щита бессмертия
        self._update_ping_timer(dt)
        self._update_shield_timer(dt)

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        screen_x = self.rect.x - cam_x
        screen_y = self.rect.y - cam_y
        
        #  Отрисовка спрайта вместо квадратов, короче тут получаем нужный кадр( если нужно ,то перевернутый)
        frame = self.anim.get_frame(self.flip_x)
        
        # Вычисляем центр хитбокса
        center_x = screen_x + self.rect.width // 2
        center_y = screen_y + self.rect.height // 2
        
        # Центруем ее по хитбоксу 
        frame_rect = frame.get_rect(center=(center_x, center_y))
        
        # Рисуем
        surface.blit(frame, frame_rect)

        if self.invulnerable_timer > 0: self.draw_shield(surface, screen_x, screen_y)

    def draw_shield(self, surface: pygame.Surface, screen_x: float, screen_y: float):
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 5  
        radius = 40 + int(pulse)
        pygame.draw.circle(surface, (0, 255, 150), (screen_x + 16, screen_y + 16), radius, 3)
        pygame.draw.circle(surface, (0, 255, 150), (screen_x + 16, screen_y + 16), radius + 4, 1)