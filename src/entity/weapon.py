import pygame
import math
from .bullet import Bullet, Grenade

# БАЗОВЫЙ КЛАСС (Родитель) 
class Weapon:
    def __init__(self, name, damage, radius, clip, shot_delay):
        self.name = name          
        self.damage = damage
        self.radius = radius
        self.clip = clip     
        self.shot_delay = shot_delay
        self.last_shot_time = 0

    def shot(self, player_pos, camera_x: float, camera_y: float) -> list:
        return []

    def update(self):
        pass


# НАСЛЕДНИК: ОГНЕСТРЕЛЬНОЕ ОРУЖИЕ (Пистолет, Дробовик)
class GunWeapon(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, b_speed, b_color, spread=0, count=1, b_range=None):
        super().__init__(name, damage, radius, clip, shot_delay)
        
        self.b_speed = b_speed    
        self.b_color = b_color   
        self.spread = spread      
        self.count = count        
        self.b_range = b_range   

    def shot(self, player_pos, camera_x: float, camera_y: float) -> list:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < self.shot_delay:
            return [] 

        self.last_shot_time = current_time

        mx, my = pygame.mouse.get_pos()
        target_x, target_y = mx + camera_x, my + camera_y
        start_x, start_y = player_pos.x + 16, player_pos.y + 16

        bullets = []
        for i in range(self.count):
            angle = 0
            if self.count > 1:
                angle = (i - (self.count - 1) / 2) * self.spread

            b = Bullet(start_x, start_y, target_x, target_y, 
                       self.b_speed, self.b_color, self.damage, angle, self.b_range, True)
    
            bullets.append(b)

        return bullets


# НАСЛЕДНИК: ЛАЗЕРНОЕ ОРУЖИЕ 
class LaserWeapon(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, duration, beam_width, color, charge_time=400):
        super().__init__(name, damage, radius, clip, shot_delay)
        
        self.duration = duration      
        self.beam_width = beam_width  
        self.color = color            
        self.charge_time = charge_time 
        
        self.is_charging = False
        self.is_firing = False
        self.active_timer = 0
        
        self.locked_dir = pygame.math.Vector2(0, 0)

    def shot(self, player_pos, camera_x: float, camera_y: float) -> list:
        current_time = pygame.time.get_ticks()
        
        if self.is_firing or self.is_charging or current_time - self.last_shot_time < self.shot_delay:
            return []

        self.last_shot_time = current_time
        
        self.is_charging = True
        self.active_timer = current_time + self.charge_time
        
        mx, my = pygame.mouse.get_pos()
        target_world = (mx + camera_x, my + camera_y)
        start_center = (player_pos.x + 16, player_pos.y + 16)
        dir_vec = pygame.math.Vector2(target_world[0] - start_center[0], target_world[1] - start_center[1])
        
        if dir_vec.magnitude() > 0:
            self.locked_dir = dir_vec.normalize()
        else:
            self.locked_dir = pygame.math.Vector2(1, 0)
            
        return []

    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.is_charging:
            if current_time > self.active_timer:
                self.is_charging = False
                self.is_firing = True
                self.active_timer = current_time + self.duration 
                
        elif self.is_firing:
            if current_time > self.active_timer:
                self.is_firing = False


# НАСЛЕДНИК: БЛИЖНИЙ БОЙ (USB-Katana)
class MeleeWeapon(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, reach, arc_degrees, color):
        super().__init__(name, damage, radius, clip, shot_delay)
        self.reach = reach
        self.arc_degrees = arc_degrees
        self.color = color
        
        self.is_swinging = False
        self.swing_duration = 200
        self.swing_timer = 0
        self.locked_angle = 0
        self.hit_enemies = [] 

    def shot(self, player_pos, camera_x: float, camera_y: float) -> list:
        current_time = pygame.time.get_ticks()
        
        if self.is_swinging or current_time - self.last_shot_time < self.shot_delay:
            return []

        self.last_shot_time = current_time
        
        self.is_swinging = True
        self.swing_timer = current_time + self.swing_duration
        self.hit_enemies = []
        
 
        mx, my = pygame.mouse.get_pos()
        target_world_x, target_world_y = mx + camera_x, my + camera_y
        start_center_x, start_center_y = player_pos.x + 16, player_pos.y + 16
        
        dx = target_world_x - start_center_x
        dy = target_world_y - start_center_y
        self.locked_angle = math.degrees(math.atan2(dy, dx))
        
        return []

    def update(self):
        if self.is_swinging and pygame.time.get_ticks() > self.swing_timer:
            self.is_swinging = False


# НАСЛЕДНИК: ГРАНАТЫ (Zip-Bomb)
class GrenadeWeapon(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, throw_speed, blast_radius, fuse_time, max_range):
        super().__init__(name, damage, radius, clip, shot_delay)
        self.throw_speed = throw_speed
        self.blast_radius = blast_radius
        self.fuse_time = fuse_time
        self.max_range = max_range
        self.color = (255, 100, 150) 

    def shot(self, player_pos, camera_x: float, camera_y: float) -> list:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < self.shot_delay:
            return []

        self.last_shot_time = current_time

        mx, my = pygame.mouse.get_pos()
        target_x, target_y = mx + camera_x, my + camera_y
        start_x, start_y = player_pos.x + 16, player_pos.y + 16

        grenade = Grenade(
            start_x, start_y, 
            target_x, target_y, 
            self.throw_speed, 
            self.color, 
            self.blast_radius, 
            self.fuse_time, 
            self.max_range
        )

        return [grenade]