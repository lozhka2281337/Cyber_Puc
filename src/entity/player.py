import pygame
import math

from .bullet import Bullet
from .weapon import GunWeapon, LaserWeapon, MeleeWeapon, GrenadeWeapon
from .animation import Animation # здесь подключаем наш класс анимации

from config import PLAYER_SPEED, PLAYER_HP, PLAYER_SIZE, PLAYER_COLOR

class Player:
    def __init__(self, x: int, y: int):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.color = PLAYER_COLOR
        self.hp = PLAYER_HP

        self.invulnerable_timer = 0 # таймер для щита бессмертия, появляющийся после получения урона
        
        self.inventory = [
            GunWeapon("Scanner", 50, 20, 10, 400, 800, (255, 255, 0)), 
            GunWeapon("Firewall", 50, 20, 5, 1100, 550, (255, 100, 0), spread=15, count=5, b_range=280), 
            LaserWeapon("Defrag", 100, 20, 1, 2500, duration=800, beam_width=14, color=(0, 255, 255), charge_time=400),
            MeleeWeapon("USB-Katana", 150, 20, 1, 400, reach=70, arc_degrees=140, color=(255, 255, 255)),
            GrenadeWeapon("Zip-Bomb", 200, 20, 1, 1000, throw_speed=400, blast_radius=70, fuse_time=1000, max_range=350)
        ]
        
        self.current_weapon_idx = 0

        # Система анимации 
        self.anim = Animation("assets/main-Sheet.png", columns=6, speed=0.07, scale=1.5)
        # По умолчанию будем смотреть вправо, так как парни на лево не ходят.  
        self.flip_x = True 
    
    def shot(self, camera_x: int, camera_y: int, world) -> None:
        current_weapon = self.inventory[self.current_weapon_idx]
        current_weapon.shot(self.pos, camera_x, camera_y, world)

    def process_weapon_damage(self, enemies, walls) -> None:
        current_weapon = self.inventory[self.current_weapon_idx]
        current_weapon.process_damage(enemies, self.rect, walls)
        
    def get_damage(self, damage=1):
        if self.invulnerable_timer <= 0: 
            self.hp -= damage
            self.invulnerable_timer = 3.0

    def movement(self, direction: pygame.math.Vector2, dt: float, walls: list):
        """ двигаем игрока:
        1) нормализация
        2) двигаем по x - проверяем на коллизии
        3) двигаем по y - проверяем на коллизии  
        """

        if direction.magnitude() > 0:
            direction = direction.normalize()

        current_weapon = self.inventory[self.current_weapon_idx]
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

    def update(self, dt: float, walls: list): 
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0, 0)

        if keys[pygame.K_w] or keys[pygame.K_UP]: direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: direction.x += 1

        # Поворот спрайта 
        if direction.x < 0:
            self.flip_x = False 
        elif direction.x > 0:
            self.flip_x = True 

        self.movement(direction, dt, walls)

        # Обновление кадров 
        if direction.magnitude() > 0:
            self.anim.update(dt) 
        else:
            self.anim.current_idx = 0 

        # обновление таймера для щита бессмертия
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

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